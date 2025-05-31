gen = ModelGenerator()

sys_admin = gen.activity('System Administrator')

# Step 1
submit_report = gen.activity('Submit expense report')

# Step 2
check_amount = gen.activity('Check amount')
auto_approve = gen.activity('Auto-approve report')
manual_approver = gen.activity('Manual Approver')

# Step 3
manual_approval = gen.activity('Manual approval')
manual_rejection = gen.activity('Manual rejection')

# Step 4
finance_team = gen.activity('Finance Team')
process_report = gen.activity('Process approved report')
direct_deposit = gen.activity('Initiate direct deposit')

# Step 5
notify_approval = gen.activity('Notify employee of approval')
notify_rejection = gen.activity('Notify employee of rejection')

# Choice for amount check
choice_amount = gen.xor(auto_approve, manual_approver)

# Choice for manual review
choice_manual_review = gen.xor(manual_approval.copy(), manual_rejection)

# Partial order for the process
final_model = gen.partial_order(
    dependencies=[
        (submit_report, check_amount),
        (check_amount, choice_amount),
        (choice_amount, choice_manual_review),
        (manual_approval, process_report),
        (process_report, direct_deposit),
        (direct_deposit, notify_approval),
        (manual_rejection, notify_rejection)
    ]
)