gen = ModelGenerator()
submit_report = gen.activity('Submit expense report')
confirm_receipt = gen.activity('Confirm receipt')
check_amount = gen.activity('Check if amount < €1,000')
auto_approve = gen.activity('Auto-approve')
route_to_approver = gen.activity('Route to Manual Approver')
review_report = gen.activity('Review report')
approve = gen.activity('Approve')
reject = gen.activity('Reject')
payment_processing = gen.activity('Payment processing')
notify_employee = gen.activity('Notify employee')

# Conditional branch based on amount
conditional_branch = gen.xor(auto_approve, route_to_approver)

# Manual approval path
manual_approval = gen.xor(approve, reject)
manual_path = gen.partial_order(dependencies=[(route_to_approver.copy(), review_report.copy()), (review_report.copy(), manual_approval), (manual_approval, payment_processing.copy())])

# Auto-approval path
auto_path = gen.partial_order(dependencies=[(auto_approve.copy(), payment_processing.copy())])

# Combine paths
combined_paths = gen.xor(auto_path, manual_path)

# Final sequential process
final_model = gen.partial_order(dependencies=[(submit_report, confirm_receipt), (confirm_receipt, check_amount), (check_amount, conditional_branch), (conditional_branch, combined_paths), (combined_paths, notify_employee)])