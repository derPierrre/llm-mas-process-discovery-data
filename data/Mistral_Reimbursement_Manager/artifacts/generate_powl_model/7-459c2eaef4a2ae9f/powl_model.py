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
reject_report_missing_receipts = gen.activity('Reject report due to missing receipts')
reject_report_policy_violations = gen.activity('Reject report due to policy violations')
reject_report_unclear_descriptions = gen.activity('Reject report due to unclear descriptions')
send_rejection_explanation_missing_receipts = gen.activity('Send rejection explanation for missing receipts')
send_rejection_explanation_policy_violations = gen.activity('Send rejection explanation for policy violations')
send_rejection_explanation_unclear_descriptions = gen.activity('Send rejection explanation for unclear descriptions')

# Financial Team Processing
initiate_transfer = gen.activity('Initiate money transfer')
send_approval_notice = gen.activity('Send approval notice with transfer details')
send_rejection_notice = gen.activity('Send rejection notice')

# Conditional Paths
auto_approval_path = gen.partial_order(dependencies=[(check_amount, auto_approve), (auto_approve, initiate_transfer.copy()), (initiate_transfer.copy(), send_approval_notice.copy())])

manual_approval_path = gen.partial_order(dependencies=[(route_to_approver, review_report)])
manual_approval_choice = gen.xor(approve_report.copy(), reject_report_missing_receipts, reject_report_policy_violations, reject_report_unclear_descriptions)
manual_approval_full = gen.partial_order(dependencies=[(review_report.copy(), manual_approval_choice)])

manual_approval_approved = gen.partial_order(dependencies=[(approve_report, initiate_transfer), (initiate_transfer, send_approval_notice)])
manual_approval_rejected_missing_receipts = gen.partial_order(dependencies=[(reject_report_missing_receipts, send_rejection_explanation_missing_receipts), (send_rejection_explanation_missing_receipts, send_rejection_notice)])
manual_approval_rejected_policy_violations = gen.partial_order(dependencies=[(reject_report_policy_violations, send_rejection_explanation_policy_violations), (send_rejection_explanation_policy_violations, send_rejection_notice)])
manual_approval_rejected_unclear_descriptions = gen.partial_order(dependencies=[(reject_report_unclear_descriptions, send_rejection_explanation_unclear_descriptions), (send_rejection_explanation_unclear_descriptions, send_rejection_notice)])

# Combine Manual Approval Paths
combined_manual_approval = gen.xor(manual_approval_approved, manual_approval_rejected_missing_receipts, manual_approval_rejected_policy_violations, manual_approval_rejected_unclear_descriptions)
full_manual_approval_path = gen.partial_order(dependencies=[(manual_approval_full, combined_manual_approval)])

# Combine Auto and Manual Approval Paths
approval_choice = gen.xor(auto_approval_path, full_manual_approval_path)

# Full Process
full_process = gen.partial_order(dependencies=[(submit_report, confirm_notification), (confirm_notification, check_amount.copy()), (check_amount.copy(), approval_choice)])

final_model = full_process