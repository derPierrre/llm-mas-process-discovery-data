gen = ModelGenerator()

# Login Process (Process Owner 0)
enter_credentials = gen.activity('Enter credentials')
verify_credentials = gen.activity('Verify credentials')
suspicious_activity_checks = gen.activity('Suspicious activity checks')
login_failure = gen.activity('Retry/reset credentials')
login_success = gen.activity('Credentials verified')
login_choice = gen.xor(login_failure, login_success)
login_poset = gen.partial_order(dependencies=[(enter_credentials, verify_credentials), (verify_credentials, login_choice), (suspicious_activity_checks,)])

# Cart Management (Process Owner 1)
select_items = gen.activity('Select items')
display_details = gen.activity('Display product details')
out_of_stock = gen.activity('Out-of-stock block')
add_items_loop = gen.loop(do=select_items.copy(), redo=None)
payment_team_work = gen.activity('Payment team works on payment methods')
cart_poset = gen.partial_order(dependencies=[(select_items, display_details), (display_details, add_items_loop), (payment_team_work,)])

# Payment Processing (Process Owner 2)
setup_payment = gen.activity('Setup payment methods')
select_payment = gen.activity('Select payment option')
immediate_payment = gen.activity('Immediate payment')
installment_payment = gen.activity('Installment payment')
payment_choice = gen.xor(immediate_payment, installment_payment)
payment_poset = gen.partial_order(dependencies=[(setup_payment, select_payment), (select_payment, payment_choice)])

# Reward Selection (Process Owner 3)
evaluate_order = gen.activity('Evaluate order total for rewards')
select_reward = gen.activity('Select reward')
skip_reward = gen.activity('Skip reward')
reward_choice = gen.xor(select_reward, skip_reward)
reward_poset = gen.partial_order(dependencies=[(evaluate_order, reward_choice)])

# Delivery Coordination (Process Owner 4)
receive_order = gen.activity('Receive completed order')
process_delivery = gen.activity('Process delivery')
special_handling = gen.activity('Special handling for fragile/distant items')
coordinate_returns = gen.activity('Coordinate with returns team')
delivery_poset = gen.partial_order(dependencies=[(receive_order, process_delivery), (process_delivery, special_handling), (special_handling, coordinate_returns)])

# Returns/Exchange Management (Process Owner 5)
verify_return = gen.activity('Verify return request')
inspect_item = gen.activity('Inspect item')
mismatch_damage = gen.activity('Handle mismatch/damage')
coordinate_replacement = gen.activity('Coordinate replacements')
returns_poset = gen.partial_order(dependencies=[(verify_return, inspect_item), (inspect_item, mismatch_damage), (mismatch_damage, coordinate_replacement)])

# Combine parallel activities
parallel_cart_payment = gen.partial_order(dependencies=[(cart_poset,), (payment_poset,)])
parallel_reward_payment = gen.partial_order(dependencies=[(reward_poset,), (payment_poset.copy(),)])

# Final model combining all processes
final_model = gen.partial_order(dependencies=[(login_poset, parallel_cart_payment), (parallel_cart_payment, parallel_reward_payment), (parallel_reward_payment, delivery_poset), (delivery_poset, returns_poset)])