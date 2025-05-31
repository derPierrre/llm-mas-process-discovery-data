 
# POWL Model for Online Shopping Process

gen = ModelGenerator()

# PO0: Authentication
login_activity = gen.activity("Customer Login")

# PO1: Product Management - Add Items
# Customers can repeatedly add/modify items in their cart.
# This phase must be completed before payment.
add_modify_cart_activity = gen.activity("Add/Modify Cart Items")
# Loop implies doing the activity at least once, then optionally repeating.
add_items_loop = gen.loop(do=add_modify_cart_activity, redo=None)

# PO2: Payment Processing
# Happens after "Add Items" is complete. Customer chooses one payment method.
immediate_payment_activity = gen.activity("Process Immediate Payment")
installment_agreement_activity = gen.activity("Set Up Installment Agreement")
payment_choice = gen.xor(immediate_payment_activity, installment_agreement_activity)

# PO3: Rewards
# Happens after "Add Items" is complete, independently of payment. Optional.
select_reward_activity = gen.activity("Select Reward")
# xor with None makes it skippable.
optional_reward_selection = gen.xor(select_reward_activity, None)

# PO4: Logistics/Delivery (Initial Order)
# Happens after both payment and rewards are sorted out.
initial_delivery_activity = gen.activity("Deliver Initial Order")

# PO5 & PO4: Returns/Exchange Management
# This entire process is optional and happens after initial delivery.
# It can repeat if multiple exchanges occur.
process_return_request_activity = gen.activity("Process Return/Exchange Request") # PO5
exchange_delivery_activity = gen.activity("Deliver Exchanged Item") # PO4

# Sequence of one return and its corresponding exchange delivery
return_and_exchange_delivery_sequence = gen.partial_order(
    dependencies=[(process_return_request_activity, exchange_delivery_activity)]
)

# The return-and-exchange-delivery can happen 1 to N times if a return is initiated.
# If a customer wants to return, they process the request, then get a delivery. This can be repeated.
return_exchange_cycle = gen.loop(do=return_and_exchange_delivery_sequence, redo=None)

# The entire return/exchange process (which can be a cycle) is optional.
optional_return_exchange_process = gen.xor(return_exchange_cycle, None)

# Main Process Flow: Combining all parts
# Dependencies:
# 1. Login must occur first.
# 2. Add Items loop must occur after Login.
# 3. Payment Choice must occur after Add Items loop.
# 4. Optional Reward Selection must occur after Add Items loop (concurrently with Payment).
# 5. Initial Delivery must occur after BOTH Payment Choice AND Optional Reward Selection.
# 6. Optional Return/Exchange Process must occur after Initial Delivery.

final_model = gen.partial_order(dependencies=[
    (login_activity, add_items_loop),
    (add_items_loop, payment_choice),
    (add_items_loop, optional_reward_selection),
    (payment_choice, initial_delivery_activity),
    (optional_reward_selection, initial_delivery_activity),
    (initial_delivery_activity, optional_return_exchange_process)
])
