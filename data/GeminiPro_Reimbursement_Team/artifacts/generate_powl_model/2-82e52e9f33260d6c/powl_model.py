gen = ModelGenerator()

# Step 1: Submission & Initial Handling Activities
act_emp_submits_report = gen.activity("Employee incurs expense, gathers receipts, creates and submits expense report")
act_sys_confirms_receipt = gen.activity("System sends automated email to employee confirming receipt")
act_admin_creates_account = gen.activity("System Administrator creates an account for new user")

# Optional account creation
optional_create_account = gen.xor(act_admin_creates_account, None)

# Initial phase of the process
initial_submission_phase = gen.partial_order(dependencies=[
    (act_emp_submits_report, act_sys_confirms_receipt),
    (act_sys_confirms_receipt, optional_create_account)
])

# Path A: Report amount < €1000
# Activities for Path A
act_sys_auto_review_A = gen.activity("System performs automated review for correctness (<€1000)")
act_sys_notifies_emp_correction_A = gen.activity("System notifies employee to correct errors (auto <€1000)")
act_emp_corrects_resubmits_A = gen.activity("Employee corrects and resubmits report (auto <€1000)")
act_sys_auto_approves_A = gen.activity("System automatically approves report (<€1000 after review/correction)")
act_ft_initiates_payment_A = gen.activity("FT initiates direct deposit for Path A (<€1000 approved)")
act_ft_sends_approval_notice_A = gen.activity("FT sends approval notice for Path A (<€1000 approved)")

# Correction loop for Path A: System auto-review, if errors, notify employee, employee corrects & resubmits, then back to auto-review.
do_auto_review_A = act_sys_auto_review_A
redo_auto_correction_A = gen.partial_order(dependencies=[
    (act_sys_notifies_emp_correction_A, act_emp_corrects_resubmits_A)
])
auto_review_correction_loop_A = gen.loop(do=do_auto_review_A, redo=redo_auto_correction_A)

# Payment processing for Path A (occurs after successful auto-review/approval from the loop)
payment_processing_A = gen.partial_order(dependencies=[
    (act_ft_initiates_payment_A, act_ft_sends_approval_notice_A)
])

# Full Path A model: auto-review/correction loop, then system approval, then payment.
full_path_A = gen.partial_order(dependencies=[
    (auto_review_correction_loop_A, act_sys_auto_approves_A),
    (act_sys_auto_approves_A, payment_processing_A)
])

# Path B: Report amount >= €1000
# Activities for Path B
act_sys_routes_to_ma_B = gen.activity("System routes report to appropriate Manual Approver (>=€1000)")
act_ma_receives_notification_B = gen.activity("Manual Approver receives notification (>=€1000)")
act_ma_reviews_report_B = gen.activity("MA reviews report for compliance and documentation (>=€1000)")
act_ft_notified_ma_rejection_for_correction_B = gen.activity("FT notified of MA rejection for correction (Path B)")
act_ft_sends_rejection_for_correction_notice_B = gen.activity("FT prepares and sends MA rejection notice for correction to employee (Path B)")
act_emp_corrects_resubmits_to_ma_B = gen.activity("Employee makes necessary corrections and resubmits report to MA (Path B)")

act_ma_issues_definitive_rejection_B = gen.activity("MA issues definitive final rejection (>=€1000 after review cycle)")
act_ft_sends_final_rejection_notice_B = gen.activity("FT prepares and sends final rejection notice after MA definitive rejection (Path B)")

act_ft_initiates_payment_B = gen.activity("FT initiates direct deposit for Path B (>=€1000 MA approved)")
act_ft_sends_approval_notice_B = gen.activity("FT sends approval notice for Path B (>=€1000 MA approved)")

# Routing phase for Path B
routing_B = gen.partial_order(dependencies=[
    (act_sys_routes_to_ma_B, act_ma_receives_notification_B)
])

# Correction loop for Path B: MA reviews. If correction needed, FT is notified, FT tells employee, employee corrects & resubmits, then MA reviews again.
do_ma_review_B = act_ma_reviews_report_B
redo_ma_correction_B = gen.partial_order(dependencies=[
    (act_ft_notified_ma_rejection_for_correction_B, act_ft_sends_rejection_for_correction_notice_B),
    (act_ft_sends_rejection_for_correction_notice_B, act_emp_corrects_resubmits_to_ma_B)
])
ma_review_correction_loop_B = gen.loop(do=do_ma_review_B, redo=redo_ma_correction_B)

# After the MA review/correction loop concludes (MA decides no more corrections via the loop):
# MA makes a final decision: Approve (leading to payment) or Definitive Rejection.

# Approved outcome for Path B (payment processing)
payment_processing_B = gen.partial_order(dependencies=[
    (act_ft_initiates_payment_B, act_ft_sends_approval_notice_B)
])
# Definitive rejection outcome for Path B (MA rejects, FT sends notice)
final_rejection_path_B = gen.partial_order(dependencies=[
    (act_ma_issues_definitive_rejection_B, act_ft_sends_final_rejection_notice_B)
])

# Decision by MA after the review/correction loop cycle:
ma_final_decision_xor_B = gen.xor(payment_processing_B, final_rejection_path_B)

# Full Path B model: routing, then MA review/correction loop, then MA's final decision (approve or definitively reject).
full_path_B = gen.partial_order(dependencies=[
    (routing_B, ma_review_correction_loop_B),
    (ma_review_correction_loop_B, ma_final_decision_xor_B)
])

# Main XOR based on amount, choosing between Full Path A and Full Path B
amount_based_choice = gen.xor(full_path_A, full_path_B)

# Final Model: initial submission phase followed by the amount-based choice
final_model = gen.partial_order(dependencies=[
    (initial_submission_phase, amount_based_choice)
])
