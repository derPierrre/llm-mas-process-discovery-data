gen = ModelGenerator()

# Activities
take_order = gen.activity('Take guest order')
submit_food = gen.activity('Submit food to kitchen')
submit_beverage = gen.activity('Forward beverage details to Sommelier')
prepare_food = gen.activity('Prepare food')
alert_waiter = gen.activity('Alert waiter during busy times')
prepare_beverage = gen.activity('Prepare beverages')
notify_waiter = gen.activity('Notify waiter via internal messaging app')
assign_waiter = gen.activity('Assign waiter')
prepare_cart = gen.activity('Prepare service cart')
pickup_food = gen.activity('Pick up food')
pickup_beverage_copy = gen.activity('Pick up beverages')
deliver_order = gen.activity('Deliver order to guest')
handle_billing = gen.activity('Handle billing')
guest_tip = gen.activity('Guest tips waiter')

# Optional tipping
optional_tip = gen.xor(guest_tip, None)

# Food preparation with optional alert
food_prep_loop = gen.loop(do=prepare_food, redo=alert_waiter)

# Beverage preparation with notification
beverage_prep = gen.partial_order(dependencies=[(prepare_beverage, notify_waiter)])

# Waiter activities
waiter_activities = gen.partial_order(dependencies=[(assign_waiter, prepare_cart), (prepare_cart, pickup_food), (prepare_cart, pickup_beverage_copy), (pickup_food, deliver_order), (pickup_beverage_copy, deliver_order), (deliver_order, handle_billing), (handle_billing, optional_tip)])

# Combining all parts
final_model = gen.partial_order(dependencies=[(take_order, submit_food), (take_order, submit_beverage), (submit_food, food_prep_loop), (submit_beverage, beverage_prep), (food_prep_loop, pickup_food), (beverage_prep, pickup_beverage_copy), (submit_food, assign_waiter), (submit_beverage, assign_waiter), (pickup_food, deliver_order), (pickup_beverage_copy, deliver_order), (deliver_order, handle_billing), (handle_billing, optional_tip)])