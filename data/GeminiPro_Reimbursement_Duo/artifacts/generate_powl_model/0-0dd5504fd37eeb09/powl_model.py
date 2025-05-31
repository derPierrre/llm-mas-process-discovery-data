"""
POWL model for the expense report process.
"""
gen = ModelGenerator()

# Step 1 Activities: Employee creates and submits an expense report.
# Employee (PO0) creates and submits an expense report.
# Employee (PO0) receives an immediate on-screen confirmation.
# System (managed by PO1) sends an email notification to the employee confirming receipt.
act_A0_create_submit_report = gen.activity('PO0 creates and submits expense report')
act_A1_onscreen_confirmation = gen.activity('PO0 receives on-screen confirmation')
act_A2_system_sends_receipt_email = gen.activity('System sends PO0 receipt email')

# Step 2 Activities: Account Creation (System Admin - Conditional)
# If it is the employee's first submission, System Admin (PO1) creates a new account for the employee. This happens *after* the receipt notification is sent.
act_A3_admin_creates_account = gen.activity('PO1 creates new account for PO0 (if first submission)')

# Step 3 Activities: Amount Review & Routing (System Admin)
# System Admin (PO1) reviews the expense report amount.
# Condition: Is the amount < €1,000?
#    YES (Automatic Approval Path): System automatically approves the report. (Go to Step 5)
#    NO (Manual Approval Path): System routes the report to the Manual Approver (PO2). (Go to Step 4)
act_A4_admin_reviews_amount = gen.activity('PO1 reviews report amount')
act_A5_system_auto_approves = gen.activity('System auto-approves report (< €1000)')
act_A6_system_routes_to_manual_approver = gen.activity('System routes report to PO2 (manual approver)')

# Step 4 Activities: Manual Review (Manual Approver)
# Manual Approver (PO2) receives the report.
# PO2 checks the request for completeness.
#    If incomplete/non-compliant: PO2 rejects the report, adding comments, and sends it back to the Employee (PO0).
#        Employee (PO0) receives rejection notification with reasons.
#        Employee (PO0) can review comments and potentially request rectification or resubmit (resubmission goes back to PO2 for review).
#    If complete and compliant: PO2 performs a detailed review against company policy.
#        If approved: PO2 clicks "Approve Manually". (Go to Step 5)
#        If rejected after detailed review: PO2 rejects the report with comments, sending it back to the Employee (PO0).
act_A7_manual_approver_receives_report = gen.activity('PO2 receives report')
act_A8_manual_approver_checks_completeness = gen.activity('PO2 checks request for completeness')
act_A9_manual_approver_rejects_incomplete = gen.activity('PO2 rejects report as incomplete/non-compliant')
act_A10_employee_receives_rejection = gen.activity('PO0 receives rejection notification with reasons')
act_A11_employee_resubmits_report = gen.activity('PO0 reviews comments and resubmits report')
act_A12_manual_approver_detailed_review = gen.activity('PO2 performs detailed review against company policy')
act_A13_manual_approver_approves_manually = gen.activity('PO2 clicks "Approve Manually"') # Success exit from loop
act_A14_manual_approver_rejects_detailed = gen.activity('PO2 rejects report after detailed review')

# Step 5 Activities: Payment Processing (Financial Team)
# Financial Team (PO3) receives the approved report (either automatically or manually approved).
# PO3 initiates the direct deposit transfer to the employee's bank account.
act_A15_finance_receives_approved_report = gen.activity('PO3 (Financial Team) receives approved report')
act_A16_finance_initiates_payment = gen.activity('PO3 initiates direct deposit transfer')

# Step 6 Activities: Final Notification (Financial Team & Employee)
# PO3 generates and sends an approval notice (email) to the employee (PO0) with transaction details.
# Employee (PO0) receives the email with approval and payment details.
act_A17_finance_sends_approval_email = gen.activity('PO3 generates and sends approval notice email to PO0')
act_A18_employee_receives_payment_email = gen.activity('PO0 receives email with approval and payment details')

# Model Step 1: Submission & Initial Notification
S1_submission_and_confirmation = gen.partial_order(dependencies=[
    (act_A0_create_submit_report, act_A1_onscreen_confirmation),
    (act_A1_onscreen_confirmation, act_A2_system_sends_receipt_email)
])

# Model Step 2: Account Creation (Conditional)
# This happens *after* receipt notification (A2)
S2_conditional_account_creation = gen.xor(act_A3_admin_creates_account, None)

# Model Step 4: Manual Review Loop
# This loop models the iterative review process by PO2. If a report is rejected, the employee (PO0)
# is notified and resubmits, triggering the review cycle by PO2 again.
# The loop terminates when PO2 approves the report (act_A13_manual_approver_approves_manually).

# Path for rejection due to incompleteness, leading to employee resubmission
S4_rejection_path_incomplete_resubmit = gen.partial_order(dependencies=[
    (act_A9_manual_approver_rejects_incomplete, act_A10_employee_receives_rejection),
    (act_A10_employee_receives_rejection, act_A11_employee_resubmits_report)
])

# Path for rejection after detailed review, leading to employee resubmission
S4_rejection_path_detailed_resubmit = gen.partial_order(dependencies=[
    (act_A14_manual_approver_rejects_detailed, act_A10_employee_receives_rejection),
    (act_A10_employee_receives_rejection, act_A11_employee_resubmits_report)
])

# Outcome if PO2 approves manually (A13) - this signifies the successful completion of a review cycle within the loop.
S4_manual_approval_outcome = act_A13_manual_approver_approves_manually

# Choice within the detailed review stage: either approve (A13) or follow the rejection/resubmission path.
S4_choice_detailed_review = gen.xor(S4_manual_approval_outcome, S4_rejection_path_detailed_resubmit)

# Actions if the report is complete and compliant, leading to detailed review.
S4_actions_if_complete_and_compliant = gen.partial_order(dependencies=[
    (act_A12_manual_approver_detailed_review, S4_choice_detailed_review)
])

# Choice after PO2's completeness check: either follow the incomplete/rejection/resubmission path, or proceed to detailed review.
S4_choice_after_completeness_check = gen.xor(S4_rejection_path_incomplete_resubmit, S4_actions_if_complete_and_compliant)

# This model represents one full cycle of PO2's review. It starts with PO2 receiving the report
# and ends either with an approval (A13) or with the employee resubmitting the report (A11),
# which implies the cycle should repeat.
S4_single_manual_review_cycle_do_part = gen.partial_order(dependencies=[
    (act_A7_manual_approver_receives_report, act_A8_manual_approver_checks_completeness),
    (act_A8_manual_approver_checks_completeness, S4_choice_after_completeness_check)
])

# The manual review process is a loop. The 'do' part is one cycle of PO2's review (S4_single_manual_review_cycle_do_part).
# If this 'do' part results in an approval (A13), the loop terminates.
# If it results in a resubmission (ending with A11), the loop implicitly continues because 'redo' is None,
# allowing the 'do' part to be executed again.
S4_manual_review_process_loop = gen.loop(do=S4_single_manual_review_cycle_do_part, redo=None)

# Model Step 5 & 6: Payment Processing and Final Notification
S5_payment_actions = gen.partial_order(dependencies=[
    (act_A15_finance_receives_approved_report, act_A16_finance_initiates_payment)
])
S6_final_notification_actions = gen.partial_order(dependencies=[
    (act_A17_finance_sends_approval_email, act_A18_employee_receives_payment_email)
])
# Combine payment and final notification into a single block that follows an approved report.
S5_S6_payment_and_notification_block = gen.partial_order(dependencies=[
    (S5_payment_actions, S6_final_notification_actions)
])

# Model Step 3: Amount Review & Routing
# Path 1: Automatic Approval. If auto-approved (A5), proceed directly to payment and notification.
S3_auto_approval_path = gen.partial_order(dependencies=[
    (act_A5_system_auto_approves, S5_S6_payment_and_notification_block)
])

# Path 2: Manual Approval. If manual review is needed, route to PO2 (A6).
# This is followed by the manual review loop (S4_manual_review_process_loop).
# Once the loop completes successfully (i.e., A13 is reached internally), proceed to payment and notification.
S3_manual_approval_path = gen.partial_order(dependencies=[
    (act_A6_system_routes_to_manual_approver, S4_manual_review_process_loop),
    (S4_manual_review_process_loop, S5_S6_payment_and_notification_block)
])

# The choice based on the amount review: either the auto-approval path or the manual approval path.
S3_amount_review_choice = gen.xor(S3_auto_approval_path, S3_manual_approval_path)

# Main process flow: 
# 1. Initial submission and receipt (S1_submission_and_confirmation).
# 2. Conditional account creation (S2_conditional_account_creation) follows S1.
# 3. Admin reviews amount (act_A4_admin_reviews_amount) follows S2.
# 4. The choice based on amount (S3_amount_review_choice) follows A4.
final_model = gen.partial_order(dependencies=[
    (S1_submission_and_confirmation, S2_conditional_account_creation),
    (S2_conditional_account_creation, act_A4_admin_reviews_amount),
    (act_A4_admin_reviews_amount, S3_amount_review_choice)
])
