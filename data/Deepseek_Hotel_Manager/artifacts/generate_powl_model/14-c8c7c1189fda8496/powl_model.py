gen = ModelGenerator()

# Activities
place_order = gen.activity('Place order')
submit_food_order_food_only = gen.activity('Submit food order to Kitchen Staff (food only)')
submit_food_order_combined = gen.activity('Submit food order to Kitchen Staff (combined)')
submit_beverage_order_beverage_only = gen.activity('Submit beverage order to Sommelier (beverage only)')
submit_beverage_order_combined = gen.activity('Submit beverage order to Sommelier (combined)')
prepare_food_food_only = gen.activity('Prepare food (food only)')
prepare_food_combined = gen.activity('Prepare food (combined)')
prepare_beverage_beverage_only = gen.activity('Prepare beverage (beverage only)')
prepare_beverage_combined = gen.activity('Prepare beverage (combined)')
collect_items_food_only = gen.activity('Collect and assemble food order (food only)')
collect_items_beverage_only = gen.activity('Collect and assemble beverage order (beverage only)')
collect_items_combined = gen.activity('Collect and assemble combined order')
deliver_order_food_only = gen.activity('Deliver food order to guest (food only)')
deliver_order_beverage_only = gen.activity('Deliver beverage order to guest (beverage only)')
deliver_order_combined = gen.activity('Deliver combined order to guest (combined)')
handle_billing = gen.activity('Handle billing')
guest_tip = gen.activity('Guest tips waiter')
optional_tip = gen.xor(guest_tip, None)

# Conditional paths
food_only = gen.partial_order(dependencies=[(submit_food_order_food_only, prepare_food_food_only), (prepare_food_food_only, collect_items_food_only), (collect_items_food_only, deliver_order_food_only)])
beverage_only = gen.partial_order(dependencies=[(submit_beverage_order_beverage_only, prepare_beverage_beverage_only), (prepare_beverage_beverage_only, collect_items_beverage_only), (collect_items_beverage_only, deliver_order_beverage_only)])
combined_order = gen.partial_order(dependencies=[(submit_food_order_combined, prepare_food_combined), (submit_beverage_order_combined, prepare_beverage_combined), (prepare_food_combined, collect_items_combined), (prepare_beverage_combined, collect_items_combined), (collect_items_combined, deliver_order_combined)])

# Choice between paths
order_type = gen.xor(food_only, beverage_only, combined_order)

# Final process flow
final_flow = gen.partial_order(dependencies=[(place_order, order_type), (deliver_order_food_only, handle_billing), (deliver_order_beverage_only, handle_billing), (deliver_order_combined, handle_billing), (handle_billing, optional_tip)])

final_model = final_flow