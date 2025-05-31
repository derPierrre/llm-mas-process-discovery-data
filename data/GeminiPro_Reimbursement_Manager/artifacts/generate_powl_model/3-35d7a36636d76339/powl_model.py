gen = ModelGenerator()

# 1. Employee creates and submits an expense report.
act_emp_submit = gen.activity('Employee creates and submits expense report')

# 2. System sends submission confirmation.
act_sys_confirm_submission = gen.activity('System sends submission confirmation to Employee')

# 3. Conditional step: New employee handling
act_admin_notified_new_emp = gen.activity('System Administrator is notified for new employee')
act_admin_creates_account = gen.activity('System Administrator creates account and stores banking info for new employee')
sub_new_employee_account_creation = gen.partial_order(dependencies=[(act_admin_notified_new_emp, act_admin_creates_account)])
opt_new_employee_handling = gen.xor(sub_new_employee_account_creation, None) # Skippable if not a new employee

# Define final notification activities (used in multiple paths)
act_final_approval_notification = gen.activity('Employee receives final approval notification with money transfer details')
act_final_rejection_notification = gen.activity('Employee receives final rejection notification with explanation')

# Path A: Auto-approval (under €1,000 AND not resubmitted)
act_sys_auto_approves = gen.activity('System automatically approves report')
# Auto-approval path leads to the final approval notification
path_auto_approved_with_notification = gen.partial_order(dependencies=[(act_sys_auto_approves, act_final_approval_notification)])

# Path B: Manual approval (€1,000 or over, OR resubmitted)
# B.1: Routing and Review
act_route_manual = gen.activity('Report routed for manual approval') 
act_manual_approver_reviews = gen.activity('Manual Approver conducts review (checks request, compliance, documentation)')

# B.2: Manual Decision and subsequent notification paths
act_manual_approver_approves = gen.activity('Manual Approver approves report')
act_manual_approver_rejects = gen.activity('Manual Approver rejects report')

# Path B.2.a: Manual approval leads to the final approval notification (using a copy)
path_manual_approved_outcome = gen.partial_order(dependencies=[(act_manual_approver_approves, act_final_approval_notification.copy())])
# Path B.2.b: Manual rejection leads to the final rejection notification
path_manual_rejected_outcome = gen.partial_order(dependencies=[(act_manual_approver_rejects, act_final_rejection_notification)])

# XOR for manual decision outcome (either approved path or rejected path)
sub_manual_decision_and_notification = gen.xor(path_manual_approved_outcome, path_manual_rejected_outcome)

# Full manual approval path: routing -> review -> decision & notification sub-process
path_manual_approval_full = gen.partial_order(dependencies=[
    (act_route_manual, act_manual_approver_reviews),
    (act_manual_approver_reviews, sub_manual_decision_and_notification)
])

# Main choice in the process: either auto-approval path or full manual approval path
# This XOR implicitly handles the condition: 
# - Path A if (Amount < 1000 AND NOT Resubmitted)
# - Path B if (Amount >= 1000 OR Resubmitted)
main_approval_logic = gen.xor(path_auto_approved_with_notification, path_manual_approval_full)

# Final model: initial steps followed by the main approval logic
# The sequence ensures that new employee handling (if any) completes before the main approval logic begins.
final_model = gen.partial_order(dependencies=[
    (act_emp_submit, act_sys_confirm_submission),
    (act_sys_confirm_submission, opt_new_employee_handling),
    (opt_new_employee_handling, main_approval_logic) 
])
