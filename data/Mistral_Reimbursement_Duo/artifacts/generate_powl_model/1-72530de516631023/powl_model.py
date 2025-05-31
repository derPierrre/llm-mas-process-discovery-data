gen = ModelGenerator()

# Define activities
expense_submission = gen.activity('Submit expense report')
confirmation_notification = gen.activity('Send confirmation notification')
create_account = gen.activity('Create account in system')
auto_approval = gen.activity('Automatically approve expense')
manual_review = gen.activity('Manual review of expense')
approve_expense = gen.activity('Approve expense')
reject_expense = gen.activity('Reject expense')
initiate_deposit = gen.activity('Initiate direct deposit')
send_approval_notice = gen.activity('Send approval notice with transfer details')
request_rectification = gen.activity('Request rectification of amount')

# Define sub-processes
first_submission_check = gen.xor(create_account, None)

manual_review_choice = gen.xor(approve_expense, reject_expense)
manual_review_copy = manual_review.copy()

expense_review_process = gen.partial_order(dependencies=[(manual_review_copy, manual_review_choice)])

expense_approval_choice = gen.xor(auto_approval, expense_review_process)

approval_process = gen.partial_order(dependencies=[(approve_expense, initiate_deposit), (initiate_deposit, send_approval_notice)])

full_process = gen.partial_order(dependencies=[(first_submission_check, expense_approval_choice), (expense_approval_choice, approval_process), (approval_process, request_rectification)])
initial_process = gen.partial_order(dependencies=[(expense_submission, confirmation_notification), (confirmation_notification, full_process)])

final_model = initial_process