gen = ModelGenerator()

# Define Activities based on the provided list, including responsible teams
customer_login = gen.activity("Customer Login (Authentication Team)")
add_items_to_cart = gen.activity("Add Items to Cart (Product Management Team)")
select_reward_activity = gen.activity("Select Reward (Rewards Team)")
process_payment_activity = gen.activity("Process Payment (Payment Processing Team)")
item_delivery_activity = gen.activity("Item Delivery (Logistics/Delivery Team)")

# Model the optional 'Select Reward' step
# This uses an xor to represent that the 'select_reward_activity' can either happen or be skipped (None).
optional_select_reward = gen.xor(select_reward_activity, None)

# Define the sequence of the main purchasing flow using a partial order
# The dependencies define the sequential order of the activities.
final_model = gen.partial_order(dependencies=[
    (customer_login, add_items_to_cart),
    (add_items_to_cart, optional_select_reward),
    (optional_select_reward, process_payment_activity),
    (process_payment_activity, item_delivery_activity)
])