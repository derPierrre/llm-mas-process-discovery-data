gen = ModelGenerator()

# Step 1: Employee submits expense report
submit_expense = gen.activity('Submit expense report')

# Step 2: System checks amount and routes it
check_amount = gen.activity('Check amount and route')
auto_approve = gen.activity('Automatically approve')
manual_review = gen.activity('Manual approver reviews')

# Step 3: Manual approver reviews if needed
# Step 4: Financial team handles payout
financial_payout = gen.activity('Financial team handles payout')

# Loop for rejected reports
reject = gen.activity('Reject report')
resubmit = gen.activity('Resubmit expense report')
loop_reject_resubmit = gen.loop(do=reject, redo=resubmit)

# Combine the steps
# System routes to either auto-approve or manual review
route_choice = gen.xor(auto_approve, manual_review)

# Partial order for the main process
poset_main = gen.partial_order(
    dependencies=[
        (submit_expense, check_amount),
        (check_amount, route_choice),
        (route_choice, financial_payout)
    ]
)

# Combine the main process with the loop for rejections
final_model = gen.partial_order(
    dependencies=[
        (poset_main, loop_reject_resubmit)
    ]
)