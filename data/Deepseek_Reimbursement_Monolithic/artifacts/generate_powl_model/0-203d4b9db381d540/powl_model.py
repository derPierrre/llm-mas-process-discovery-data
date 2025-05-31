gen = ModelGenerator()

# Activities
submit_report = gen.activity('Submit expense report')
notify_employee = gen.activity('Send confirmation email')
create_account = gen.activity('Create employee account')
auto_approve = gen.activity('Automatically approve report')
manual_approve = gen.activity('Manually approve report')
transfer_money = gen.activity('Transfer reimbursement')
notify_approval = gen.activity('Notify employee of approval')

# Conditional approval paths
approval_choice = gen.xor(auto_approve, manual_approve)

# Process flow
poset = gen.partial_order(
    dependencies=[
        (submit_report, notify_employee),
        (notify_employee, create_account),
        (create_account, approval_choice),
        (approval_choice, transfer_money),
        (transfer_money, notify_approval)
    ]
)

final_model = poset