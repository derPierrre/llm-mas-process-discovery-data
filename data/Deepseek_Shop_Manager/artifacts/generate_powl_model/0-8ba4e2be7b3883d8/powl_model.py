gen = ModelGenerator()
authentication = gen.activity('Authentication (Process Owner 0)')
add_items = gen.activity('Add items to cart (Process Owner 1)')
checkout_payment = gen.activity('Checkout and payment (Process Owner 2)')
present_rewards = gen.activity('Present rewards (Process Owner 3)')
optional_rewards = gen.xor(present_rewards, None)
prepare_ship = gen.activity('Prepare and ship order (Process Owner 4)')
process_return = gen.activity('Process return/exchange (Process Owner 5)')

# Main process flow
poset_main = gen.partial_order(dependencies=[(authentication, add_items), (add_items, checkout_payment), (checkout_payment, optional_rewards), (optional_rewards, prepare_ship)])

# Return/exchange loop
loop_return = gen.loop(do=process_return, redo=prepare_ship)

# Combine main flow and return loop
final_model = gen.partial_order(dependencies=[(poset_main, loop_return)])