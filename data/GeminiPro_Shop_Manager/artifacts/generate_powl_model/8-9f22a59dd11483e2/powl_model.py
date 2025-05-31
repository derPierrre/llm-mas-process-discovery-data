gen = ModelGenerator()

# Main Purchasing Flow Activities
auth = gen.activity('Customer logs in (Authentication Team)')
add_items = gen.activity('Customer selects items and adds them to the cart (Product Management Team)')
select_reward_activity = gen.activity('Customer selects a reward based on cart value (Rewards Team)')
optional_select_reward = gen.xor(select_reward_activity, None)
process_payment = gen.activity('Customer makes payment, reward factored in (Payment Processing Team)')
item_delivery_main = gen.activity('Initial Order is delivered to the customer (Logistics/Delivery Team)')

# Sequence of Main Purchasing Flow
main_flow_sequence = gen.partial_order(dependencies=[
    (auth, add_items),
    (add_items, optional_select_reward),
    (optional_select_reward, process_payment),
    (process_payment, item_delivery_main)
])

# Returns/Exchange Flow Activities
initiate_exchange = gen.activity('Customer Initiates Exchange Request (Returns/Exchange Management Team receives it)')
verify_return_label = gen.activity('Return Verification & Label Generation (Returns/Exchange Management Team)')
customer_returns_item = gen.activity('Customer Returns Item')
monitor_inspect_return = gen.activity('Return Shipment Monitoring & Item Inspection (Returns/Exchange Management Team)')

# Activities for successful inspection outcome within the exchange flow
notify_if_successful = gen.activity('Notify Logistics for Replacement Delivery if inspection successful (Returns/Exchange Management Team)')
replacement_item_delivery_exchange = gen.activity('Replacement Item Delivery for exchange (Logistics/Delivery Team)')

# Path for successful inspection and replacement, this is a sequence if inspection is successful
successful_exchange_branch = gen.partial_order(dependencies=[
    (notify_if_successful, replacement_item_delivery_exchange)
])

# Conditional part: replacement (notification and delivery) happens only if inspection is successful for the current attempt.
# If inspection is not successful, this branch (successful_exchange_branch) is skipped for the current exchange attempt.
post_inspection_choice = gen.xor(successful_exchange_branch, None)

# Sequence of a single Exchange Cycle/Attempt
# This represents one full attempt to exchange an item, from initiation to potential replacement delivery.
one_exchange_attempt = gen.partial_order(dependencies=[
    (initiate_exchange, verify_return_label),
    (verify_return_label, customer_returns_item),
    (customer_returns_item, monitor_inspect_return),
    (monitor_inspect_return, post_inspection_choice) 
])

# Loop for the Exchange Flow: "This exchange cycle ... can be repeated"
# This means if the exchange process is started, 'one_exchange_attempt' is performed at least once, 
# and then can be repeated if further exchanges are needed for the original order context.
exchange_loop = gen.loop(do=one_exchange_attempt, redo=None)

# The entire Returns/Exchange Flow (which includes the loop of attempts) is optional 
# and can be initiated only after Item Delivery of the main purchase.
optional_exchange_process = gen.xor(exchange_loop, None)

# Final Model: Main purchasing flow followed by the optional returns/exchange process
final_model = gen.partial_order(dependencies=[
    (main_flow_sequence, optional_exchange_process)
])