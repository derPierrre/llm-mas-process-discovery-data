gen = ModelGenerator()

# Activities
take_order = gen.activity('Take guest order')
submit_food = gen.activity('Submit food to kitchen')
submit_beverage = gen.activity('Forward beverage details to Sommelier')
prepare_food = gen.activity('Prepare food')
alert_waiter = gen.activity('Alert waiter during busy times')
prepare_beverage = gen.activity('Prepare beverages')
notify_waiter = gen.activity('Notify waiter via internal messaging app')
assign_waiter_1 = gen.activity('Assign waiter')
assign_waiter_2 = gen.activity('Assign waiter')
prepare_cart = gen.activity('Prepare service cart')
pickup_food_1 = gen.activity('Pick up food')
pickup_food_2 = gen.activity('Pick up food')
pickup_beverage_1 = gen.activity('Pick up beverages')
pickup_beverage_2 = gen.activity('Pick up beverages')
deliver_order_1 = gen.activity('Deliver order to guest')
deliver_order_2 = gen.activity('Deliver order to guest')
handle_billing_1 = gen.activity('Handle billing')
handle_billing_2 = gen.activity('Handle billing')
guest_tip = gen.activity('Guest tips waiter')

# Optional tipping
optional_tip_1 = gen.xor(guest_tip, None)
optional_tip_2 = gen.xor(guest_tip.copy(), None)

# Food preparation with optional alert
food_prep_loop = gen.loop(do=prepare_food, redo=alert_waiter)

# Beverage preparation with notification
beverage_prep = gen.partial_order(dependencies=[(prepare_beverage, notify_waiter)])

# Waiter activities
waiter_activities = gen.partial_order(dependencies=[(assign_waiter_1, prepare_cart), (prepare_cart, pickup_food_1), (prepare_cart, pickup_beverage_1), (pickup_food_1, deliver_order_1), (pickup_beverage_1, deliver_order_1), (deliver_order_1, handle_billing_1), (handle_billing_1, optional_tip_1)])

# Combining all parts
final_model = gen.partial_order(dependencies=[(take_order, submit_food), (take_order, submit_beverage), (submit_food, food_prep_loop), (submit_beverage, beverage_prep), (food_prep_loop, pickup_food_2), (beverage_prep, pickup_beverage_2), (submit_food, assign_waiter_2), (submit_beverage, assign_waiter_2), (pickup_food_2, deliver_order_2), (pickup_beverage_2, deliver_order_2), (deliver_order_2, handle_billing_2), (handle_billing_2, optional_tip_2)])