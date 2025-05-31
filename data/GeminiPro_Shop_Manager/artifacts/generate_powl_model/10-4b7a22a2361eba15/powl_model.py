gen = ModelGenerator()

# Main Purchasing Flow Activities
auth = gen.activity('Customer logs in (Authentication Team)')
add_items = gen.activity('Customer selects items and adds them to the cart (Product Management Team)')
select_reward_activity = gen.activity('Customer selects a reward based on cart value (Rewards Team)')
# Step 3: Select Reward is optional
optional_select_reward = gen.xor(select_reward_activity, None)
process_payment = gen.activity('Customer makes payment. The selected reward (if any) is factored into the payment (Payment Processing Team)')
item_delivery = gen.activity('Order is delivered to the customer (Logistics/Delivery Team)')

# Sequence of Main Purchasing Flow
# The flow is sequential from Authentication to Item Delivery
final_model = gen.partial_order(dependencies=[
    (auth, add_items),
    (add_items, optional_select_reward),
    (optional_select_reward, process_payment),
    (process_payment, item_delivery)
])