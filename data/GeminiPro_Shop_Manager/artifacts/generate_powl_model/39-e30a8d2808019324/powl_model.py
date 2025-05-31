gen = ModelGenerator()

# Define Activities for the Main Purchasing Flow
login_activity = gen.activity("Login (Authentication Team)")
add_items_activity = gen.activity("Add Items (Product Management Team)")
select_reward_activity = gen.activity("Select Reward (Rewards Team)")
process_payment_activity = gen.activity("Process Payment (Payment Processing Team)")
deliver_item_activity = gen.activity("Deliver Item (Logistics/Delivery Team)")

# Model the optional 'Select Reward' step
# The customer can either perform the 'Select Reward' activity or skip it (None).
optional_select_reward = gen.xor(select_reward_activity, None)

# Define the sequence of the main purchasing flow using a partial order.
# The activities are performed one after another in the specified order.
final_model = gen.partial_order(dependencies=[
    (login_activity, add_items_activity),
    (add_items_activity, optional_select_reward),
    (optional_select_reward, process_payment_activity),
    (process_payment_activity, deliver_item_activity)
])