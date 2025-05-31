gen = ModelGenerator()

# Step 1: Employee Submission
submit_report = gen.activity('Submit expense report')
confirm_notification = gen.activity('Send confirmation notification')

# Step 2: System Processing
check_amount = gen.activity('Check expense amount')

# Automatic Approval Path
auto_approve = gen.activity('Auto approve report')

# Manual Approval Path
route_to_approver = gen.activity('Route to manual approver')
manual_approval = gen.activity('Manual approval')

# Step 3: Manual Approval
review_report = gen.activity('Review expense report')
approve_report = gen.activity('Approve report')
reject_report = gen.activity('Reject report')
send_rejection_explanation = gen.activity('Send rejection explanation')

# Financial Team Processing
initiate_transfer = gen.activity('Initiate money transfer')
send_approval_notice = gen.activity('Send approval notice with transfer details')
send_rejection_notice = gen.activity('Send rejection notice')

# Conditional Paths
auto_approval_path = gen.partial_order(dependencies=[(check_amount, auto_approve), (auto_approve, initiate_transfer), (initiate_transfer, send_approval_notice)])

manual_approval_path = gen.partial_order(dependencies=[(route_to_approver, review_report)])
manual_approval_choice = gen.xor(approve_report, reject_report)
manual_approval_full = gen.partial_order(dependencies=[(review_report, manual_approval_choice)])

manual_approval_approved = gen.partial_order(dependencies=[(approve_report, initiate_transfer), (initiate_transfer, send_approval_notice)])
manual_approval_rejected = gen.partial_order(dependencies=[(reject_report, send_rejection_explanation), (send_rejection_explanation, send_rejection_notice)])

# Combine Manual Approval Paths
combined_manual_approval = gen.xor(manual_approval_approved, manual_approval_rejected)
full_manual_approval_path = gen.partial_order(dependencies=[(manual_approval_full, combined_manual_approval)])

# Combine Auto and Manual Approval Paths
approval_choice = gen.xor(auto_approval_path, full_manual_approval_path)

# Full Process
full_process = gen.partial_order(dependencies=[(submit_report, confirm_notification), (confirm_notification, check_amount.copy()), (check_amount.copy(), approval_choice)])

final_model = full_process