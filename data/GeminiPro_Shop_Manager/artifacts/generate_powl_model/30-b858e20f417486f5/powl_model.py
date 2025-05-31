gen = ModelGenerator()

# Define Activities for the Main Purchasing Flow
login = gen.activity("Login (Authentication Team)")
add_items = gen.activity("Add Items (Product Management Team)")
select_reward_activity = gen.activity("Select Reward (Rewards Team)")
process_payment = gen.activity("Process Payment (Payment Processing Team)")
deliver_item = gen.activity("Deliver Item (Logistics/Delivery Team)")

# Model the optional 'Select Reward' step
# This uses an xor to represent that 'select_reward_activity' can either happen or be skipped (None).
optional_select_reward = gen.xor(select_reward_activity, None)

# Define the sequence of the main purchasing flow using a partial order
# The dependencies define the strict sequential order of the activities.
final_model = gen.partial_order(dependencies=[
    (login, add_items),
    (add_items, optional_select_reward),
    (optional_select_reward, process_payment),
    (process_payment, deliver_item)
])