gen = ModelGenerator()

# Activities
order_placement = gen.activity('Order Placement')
split_order = gen.activity('Split Order into Food and Beverages')
food_preparation = gen.activity('Food Preparation')
plate_food = gen.activity('Plate Food')
notify_waiter_food = gen.activity('Notify Waiter (Food)')
beverage_preparation = gen.activity('Beverage Preparation')
place_beverages = gen.activity('Place Beverages for Pickup')
prepare_cart = gen.activity('Prepare Service Cart')
collect_items = gen.activity('Collect Food and Beverages')
ensure_readiness = gen.activity('Ensure Readiness for Delivery')
delivery = gen.activity('Delivery to Guest')
guest_interaction = gen.activity('Guest Interaction')
payment_processing = gen.activity('Payment Processing')

# Parallel tasks for food and beverage preparation
food_flow = gen.partial_order(dependencies=[(food_preparation, plate_food), (plate_food, notify_waiter_food)])
beverage_flow = gen.partial_order(dependencies=[(beverage_preparation, place_beverages)])
parallel_preparation = gen.partial_order(dependencies=[(food_flow,), (beverage_flow,)])

# Order assembly and delivery flow
order_assembly = gen.partial_order(dependencies=[(prepare_cart, collect_items), (collect_items, ensure_readiness)])
delivery_flow = gen.partial_order(dependencies=[(ensure_readiness.copy(), delivery), (delivery, guest_interaction), (guest_interaction, payment_processing)])

# Combine all flows
final_model = gen.partial_order(dependencies=[(order_placement, split_order), (split_order, parallel_preparation), (parallel_preparation, order_assembly), (order_assembly, delivery_flow)])