gen = ModelGenerator()
submit_report = gen.activity('Submit expense report')
check_amount = gen.activity('Check amount')
auto_approve = gen.activity('Auto-approve')
manual_review = gen.activity('Manual review')
transfer_funds = gen.activity('Transfer funds')
send_notice = gen.activity('Send approval notice')

# Exclusive choice based on amount
approval_choice = gen.xor(auto_approve, manual_review)

# Partial order for the process
final_model = gen.partial_order(
    dependencies=[(submit_report, check_amount), (check_amount, approval_choice),
                 (approval_choice, transfer_funds), (transfer_funds, send_notice)]
)