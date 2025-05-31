gen = ModelGenerator()

# Activities
place_order = gen.activity('Place order')
submit_food_order = gen.activity('Submit food order to Kitchen Staff')
submit_beverage_order = gen.activity('Submit beverage order to Sommelier')
prepare_food = gen.activity('Prepare food')
prepare_beverage = gen.activity('Prepare beverage')
collect_items_food = gen.activity('Collect and assemble food order')
collect_items_beverage = gen.activity('Collect and assemble beverage order')
collect_items_combined = gen.activity('Collect and assemble combined order')
deliver_order = gen.activity('Deliver order to guest')
handle_billing = gen.activity('Handle billing')
guest_tip = gen.activity('Guest tips waiter')
optional_tip = gen.xor(guest_tip, None)

# Conditional paths
food_only = gen.partial_order(dependencies=[(submit_food_order, prepare_food), (prepare_food, collect_items_food)])
beverage_only = gen.partial_order(dependencies=[(submit_beverage_order, prepare_beverage), (prepare_beverage, collect_items_beverage)])
combined_order = gen.partial_order(dependencies=[(submit_food_order, prepare_food), (submit_beverage_order, prepare_beverage), (prepare_food, collect_items_combined), (prepare_beverage, collect_items_combined)])

# Choice between paths
order_type = gen.xor(food_only, beverage_only, combined_order)

# Final process flow
final_flow = gen.partial_order(dependencies=[(place_order, order_type), (collect_items_food, deliver_order), (collect_items_beverage, deliver_order), (collect_items_combined, deliver_order), (deliver_order, handle_billing), (handle_billing, optional_tip)])

final_model = final_flow