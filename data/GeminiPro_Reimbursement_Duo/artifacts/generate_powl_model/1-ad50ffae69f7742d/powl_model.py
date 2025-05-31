"""
POWL model for the expense report process.
"""
gen = ModelGenerator()

# Step 1 Activities: Employee creates and submits an expense report.
act_A0_create_submit_report = gen.activity('PO0 creates and submits expense report')
act_A1_onscreen_confirmation = gen.activity('PO0 receives on-screen confirmation')
act_A2_system_sends_receipt_email = gen.activity('System sends PO0 receipt email')

# Step 2 Activities: Account Creation (System Admin - Conditional)
act_A3_admin_creates_account = gen.activity('PO1 creates new account for PO0 (if first submission)')

# Step 3 Activities: Amount Review & Routing (System Admin)
act_A4_admin_reviews_amount = gen.activity('PO1 reviews report amount')
act_A5_system_auto_approves = gen.activity('System auto-approves report (< €1000)')
act_A6_system_routes_to_manual_approver = gen.activity('System routes report to PO2 (manual approver)')

# Step 4 Activities: Manual Review (Manual Approver)
act_A7_manual_approver_receives_report = gen.activity('PO2 receives report')
act_A8_manual_approver_checks_completeness = gen.activity('PO2 checks request for completeness')
act_A9_manual_approver_rejects_incomplete = gen.activity('PO2 rejects report as incomplete/non-compliant')
act_A10_employee_receives_rejection = gen.activity('PO0 receives rejection notification with reasons')
act_A11_employee_resubmits_report = gen.activity('PO0 reviews comments and resubmits report')
act_A12_manual_approver_detailed_review = gen.activity('PO2 performs detailed review against company policy')
act_A13_manual_approver_approves_manually = gen.activity('PO2 clicks "Approve Manually"')
act_A14_manual_approver_rejects_detailed = gen.activity('PO2 rejects report after detailed review')

# Step 5 Activities: Payment Processing (Financial Team)
act_A15_finance_receives_approved_report = gen.activity('PO3 (Financial Team) receives approved report')
act_A16_finance_initiates_payment = gen.activity('PO3 initiates direct deposit transfer')

# Step 6 Activities: Final Notification (Financial Team & Employee)
act_A17_finance_sends_approval_email = gen.activity('PO3 generates and sends approval notice email to PO0')
act_A18_employee_receives_payment_email = gen.activity('PO0 receives email with approval and payment details')

# Model Step 1: Submission & Initial Notification
S1_submission_and_confirmation = gen.partial_order(dependencies=[
    (act_A0_create_submit_report, act_A1_onscreen_confirmation),
    (act_A1_onscreen_confirmation, act_A2_system_sends_receipt_email)
])

# Model Step 2: Account Creation (Conditional)
S2_conditional_account_creation = gen.xor(act_A3_admin_creates_account, None)

# Model Step 4: Manual Review Loop
# Create copies for reused activities in different rejection paths
act_A10_copy_for_detailed_rejection = act_A10_employee_receives_rejection.copy()
act_A11_copy_for_detailed_rejection = act_A11_employee_resubmits_report.copy()

S4_rejection_path_incomplete_resubmit = gen.partial_order(dependencies=[
    (act_A9_manual_approver_rejects_incomplete, act_A10_employee_receives_rejection),
    (act_A10_employee_receives_rejection, act_A11_employee_resubmits_report)
])

S4_rejection_path_detailed_resubmit = gen.partial_order(dependencies=[
    (act_A14_manual_approver_rejects_detailed, act_A10_copy_for_detailed_rejection),
    (act_A10_copy_for_detailed_rejection, act_A11_copy_for_detailed_rejection)
])

S4_manual_approval_outcome = act_A13_manual_approver_approves_manually

S4_choice_detailed_review = gen.xor(S4_manual_approval_outcome, S4_rejection_path_detailed_resubmit)

S4_actions_if_complete_and_compliant = gen.partial_order(dependencies=[
    (act_A12_manual_approver_detailed_review, S4_choice_detailed_review)
])

S4_choice_after_completeness_check = gen.xor(S4_rejection_path_incomplete_resubmit, S4_actions_if_complete_and_compliant)

S4_single_manual_review_cycle_do_part = gen.partial_order(dependencies=[
    (act_A7_manual_approver_receives_report, act_A8_manual_approver_checks_completeness),
    (act_A8_manual_approver_checks_completeness, S4_choice_after_completeness_check)
])

S4_manual_review_process_loop = gen.loop(do=S4_single_manual_review_cycle_do_part, redo=None)

# Model Steps 5 & 6: Payment Processing and Final Notification (Flattened)
S5_S6_payment_and_notification_block = gen.partial_order(dependencies=[
    (act_A15_finance_receives_approved_report, act_A16_finance_initiates_payment),
    (act_A16_finance_initiates_payment, act_A17_finance_sends_approval_email),
    (act_A17_finance_sends_approval_email, act_A18_employee_receives_payment_email)
])

# Model Step 3: Amount Review & Routing
S3_auto_approval_path = gen.partial_order(dependencies=[
    (act_A5_system_auto_approves, S5_S6_payment_and_notification_block)
])

# Create a copy of the payment block for the manual path
S5_S6_payment_and_notification_block_copy_for_manual = S5_S6_payment_and_notification_block.copy()

S3_manual_approval_path = gen.partial_order(dependencies=[
    (act_A6_system_routes_to_manual_approver, S4_manual_review_process_loop),
    (S4_manual_review_process_loop, S5_S6_payment_and_notification_block_copy_for_manual)
])

S3_amount_review_choice = gen.xor(S3_auto_approval_path, S3_manual_approval_path)

# Main process flow
final_model = gen.partial_order(dependencies=[
    (S1_submission_and_confirmation, S2_conditional_account_creation),
    (S2_conditional_account_creation, act_A4_admin_reviews_amount),
    (act_A4_admin_reviews_amount, S3_amount_review_choice)
])
