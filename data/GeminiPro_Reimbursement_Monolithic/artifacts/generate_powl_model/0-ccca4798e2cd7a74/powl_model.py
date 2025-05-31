"""
Process Owner 0: Submits expense reports, can request corrections before approval/rejection, receives final notification.
Process Owner 1 (System Admin): Creates accounts for new employees (initial step), manages automated approval logic (<€1000 auto-approved, >=€1000 routed to manual approvers).
Process Owner 2 (Manual Approver): Manually approves/rejects reports >=€1000.

Flow:
1. Optional: If new employee, PO1 creates account.
2. PO0 submits expense report.
3. PO0 receives submission confirmation.
4. Main processing cycle (can be repeated if PO0 requests correction):
   a. System (managed by PO1) evaluates report amount.
   b. If <€1000: System auto-approves, PO0 gets approval notification.
   c. If >=€1000: PO2 manually reviews.
      i. PO2 approves: PO0 gets approval notification.
      ii. PO2 rejects: PO0 gets rejection notification.
   d. If PO0 requests correction (before final approval/rejection of this cycle), the main processing cycle (4a-c) repeats.
"""
gen = ModelGenerator()

# Define activities based on Process Owner roles and actions
po0_submit_report = gen.activity('PO0 submits expense report')
po1_create_account = gen.activity('PO1 creates account for new employee')
po0_receive_confirmation = gen.activity('PO0 receives submission confirmation from system')

sys_eval_amount = gen.activity('System evaluates report amount for routing') # System logic managed by PO1

sys_auto_approve = gen.activity('System automatically approves report (<€1000)') # System action
po2_manual_review = gen.activity('PO2 manually reviews report (>=€1000)')
po2_manual_approve = gen.activity('PO2 manually approves report')
po2_manual_reject = gen.activity('PO2 manually rejects report')

po0_request_correction = gen.activity('PO0 requests correction during review') # PO0 action

po0_notify_approved = gen.activity('PO0 receives approval notification and payment details') # PO0 receives
po0_notify_rejected = gen.activity('PO0 receives rejection notification and reasons') # PO0 receives

# Step 1: Optional account creation for new employees
# This happens before submission if the employee is new.
optional_account_creation = gen.xor(po1_create_account, None)

# Define the paths for outcomes leading to notifications (this will be the 'do' part of the loop)
# Path for auto-approval
auto_approve_with_notification_path = gen.partial_order(dependencies=[
    (sys_auto_approve, po0_notify_approved)
])

# Path for manual approval - requires a copy of the notification activity if it's the same
po0_notify_approved_copy_for_manual = po0_notify_approved.copy()
manual_approve_with_notification_path = gen.partial_order(dependencies=[
    (po2_manual_approve, po0_notify_approved_copy_for_manual)
])

# Path for manual rejection
manual_reject_with_notification_path = gen.partial_order(dependencies=[
    (po2_manual_reject, po0_notify_rejected)
])

# Branch for manual review leading to either manual approval or rejection path
manual_review_branch_with_outcomes = gen.partial_order(dependencies=[
    (po2_manual_review, gen.xor(manual_approve_with_notification_path, manual_reject_with_notification_path))
])

# The core evaluation and decision process that leads to a notification if not corrected
# This is the 'do' part of the correction loop
evaluation_to_final_notification_do_part = gen.partial_order(dependencies=[
    (sys_eval_amount, gen.xor(auto_approve_with_notification_path, manual_review_branch_with_outcomes))
])

# Step 4: The correction loop. 
# The 'do' part is the full evaluation leading to notification.
# The 'redo' part is PO0 requesting a correction, which restarts the 'do' part.
correction_cycle_loop = gen.loop(do=evaluation_to_final_notification_do_part, redo=po0_request_correction)

# Define the overall process flow using a partial order
# Sequence: Optional Account Creation -> Submit Report -> Receive Confirmation -> Correction Cycle
final_model = gen.partial_order(dependencies=[
    (optional_account_creation, po0_submit_report),
    (po0_submit_report, po0_receive_confirmation),
    (po0_receive_confirmation, correction_cycle_loop)
])
