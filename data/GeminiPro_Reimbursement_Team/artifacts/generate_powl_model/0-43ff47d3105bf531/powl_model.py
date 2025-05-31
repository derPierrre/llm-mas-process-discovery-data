gen = ModelGenerator()

# Step 1: Submission & Initial Handling
act_submit_report = gen.activity("Employee incurs expense, gathers receipts, creates and submits expense report")
act_system_confirms_receipt = gen.activity("System sends automated email to employee confirming receipt")
act_admin_creates_account = gen.activity("System Administrator creates an account for new user")
optional_create_account = gen.xor(act_admin_creates_account, None)

initial_phase = gen.partial_order(dependencies=[
    (act_submit_report, act_system_confirms_receipt),
    (act_system_confirms_receipt, optional_create_account)
])

# Common Financial Activities (Step 4 outcomes)
act_ft_initiates_payment = gen.activity("Financial Team Member initiates direct deposit transfer")
act_ft_sends_approval_notice = gen.activity("Financial Team Member prepares and sends approval notice with payment details")
common_payment_processing = gen.partial_order(dependencies=[
    (act_ft_initiates_payment, act_ft_sends_approval_notice)
])

act_ft_sends_ma_final_rejection_notice = gen.activity("Financial Team Member prepares and sends final rejection notice (after MA definitive rejection)")

# Path A: Report amount < €1000
act_auto_review = gen.activity("System performs automated review for correctness (<€1000)")
act_notify_correction_auto = gen.activity("System notifies employee to correct errors (auto <€1000)")
act_correct_resubmit_auto = gen.activity("Employee corrects and resubmits report (auto <€1000)")
redo_auto_review_sequence = gen.partial_order(dependencies=[
    (act_notify_correction_auto, act_correct_resubmit_auto)
])
auto_review_and_correction_cycle = gen.loop(do=act_auto_review, redo=redo_auto_review_sequence)
act_system_auto_approves = gen.activity("System automatically approves report (<€1000 after review/correction)")
path_A_core_approval = gen.partial_order(dependencies=[
    (auto_review_and_correction_cycle, act_system_auto_approves)
])
full_path_A_flow = gen.partial_order(dependencies=[
    (path_A_core_approval, common_payment_processing)
])

# Path B: Report amount >= €1000
# Routing phase for Path B
act_route_to_manual = gen.activity("System routes report to appropriate Manual Approver (>=€1000)")
act_manual_approver_notified = gen.activity("Manual Approver receives notification")
path_B_routing_phase = gen.partial_order(dependencies=[
    (act_route_to_manual, act_manual_approver_notified)
])

# Manual review and correction loop part for Path B (leads to approval if successful)
act_manual_review_by_ma = gen.activity("Manual Approver reviews report for compliance and documentation (>=€1000)")
act_ft_notified_rejection_manual = gen.activity("Financial Team Member is notified of MA rejection for correction")
act_ft_sends_rejection_notice_manual = gen.activity("Financial Team Member prepares and sends MA rejection notice for correction to employee")
act_employee_corrects_resubmits_manual = gen.activity("Employee makes necessary corrections and resubmits report to MA (manual)")
redo_manual_review_correction_sequence = gen.partial_order(dependencies=[
    (act_ft_notified_rejection_manual, act_ft_sends_rejection_notice_manual),
    (act_ft_sends_rejection_notice_manual, act_employee_corrects_resubmits_manual)
])
manual_review_and_correction_loop = gen.loop(do=act_manual_review_by_ma, redo=redo_manual_review_correction_sequence)

# Path B approved outcome: loop followed by payment
path_B_approved_with_payment = gen.partial_order(dependencies=[
    (manual_review_and_correction_loop, common_payment_processing)
])

# Path B final rejection outcome: MA issues final rejection, followed by FT notice
act_ma_issues_final_rejection = gen.activity("Manual Approver issues definitive final rejection (>=€1000)")
path_B_final_rejection_with_notice = gen.partial_order(dependencies=[
    (act_ma_issues_final_rejection, act_ft_sends_ma_final_rejection_notice)
])

# Manual Approver's decision point in Path B: either approval path or final rejection path
manual_decision_outcome_paths = gen.xor(
    path_B_approved_with_payment,
    path_B_final_rejection_with_notice
)

# Full Path B flow: routing followed by the MA's decision outcome paths
full_path_B_flow = gen.partial_order(dependencies=[
    (path_B_routing_phase, manual_decision_outcome_paths)
])

# Main XOR based on amount, connecting initial phase to either full Path A or full Path B
amount_based_choice = gen.xor(full_path_A_flow, full_path_B_flow)

# Final Model: initial phase followed by the amount-based choice leading to complete sub-processes
final_model = gen.partial_order(dependencies=[
    (initial_phase, amount_based_choice)
])