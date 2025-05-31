"""
Process model for an e-commerce flow.
"""
gen = ModelGenerator()

# 1. User Authentication
auth = gen.activity('User Authentication')

# 2. Add Items to Cart (can be repeated)
# This represents the phase where a user can add multiple items.
# The activity 'Add Item to Cart' can be performed one or more times.
add_item_activity = gen.activity('Add Item to Cart')
add_items_phase = gen.loop(do=add_item_activity, redo=None)

# 3. Optional Reward Selection
reward_selection_activity = gen.activity('Reward Selection')
optional_reward_selection = gen.xor(reward_selection_activity, None)

# 4. Payment Processing
payment_processing = gen.activity('Payment Processing')

# 5. Item Delivery
item_delivery = gen.activity('Item Delivery')

# Define the overall process flow as a sequence
final_model = gen.partial_order(dependencies=[
    (auth, add_items_phase),
    (add_items_phase, optional_reward_selection),
    (optional_reward_selection, payment_processing),
    (payment_processing, item_delivery)
])
