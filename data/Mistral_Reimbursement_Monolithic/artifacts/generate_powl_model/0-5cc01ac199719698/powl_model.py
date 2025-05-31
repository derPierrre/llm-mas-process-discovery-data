gen = ModelGenerator()

# Define activities
submit_report = gen.activity('Submit expense report')
send_notification = gen.activity('Send confirmation notification')
create_account = gen.activity('Create account')
check_amount = gen.activity('Check amount')
auto_approve = gen.activity('Auto approve')
route_to_approver = gen.activity('Route to approver')
manual_approval = gen.activity('Manual approval')
reject = gen.activity('Reject')
send_rejection_notice = gen.activity('Send rejection notice')
resubmit_report = gen.activity('Resubmit report')
initiate_transfer = gen.activity('Initiate direct deposit transfer')
send_approval_notice = gen.activity('Send approval notice')
log_amount_rectification = gen.activity('Log amount rectification request')

# Define partial orders
initial_process = gen.partial_order(dependencies=[(submit_report, send_notification), (submit_report, create_account), (submit_report, check_amount)])

approval_process = gen.partial_order(dependencies=[(check_amount, auto_approve), (check_amount, route_to_approver), (route_to_approver, manual_approval), (route_to_approver, reject)])

rejection_process = gen.partial_order(dependencies=[(reject, send_rejection_notice), (send_rejection_notice, resubmit_report)])

final_process = gen.partial_order(dependencies=[(initial_process, approval_process), (approval_process, initiate_transfer), (initiate_transfer, send_approval_notice), (send_approval_notice, log_amount_rectification), (approval_process, rejection_process)])

# Define the final model
final_model = final_process