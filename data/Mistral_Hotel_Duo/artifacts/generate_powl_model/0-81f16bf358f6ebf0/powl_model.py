gen = ModelGenerator()

# Process Owner 0: Room Service Manager
room_service_manager = gen.activity('Room Service Manager')
take_order = gen.activity('Take guest orders via phone')
submit_to_kitchen = gen.activity('Submit food orders to kitchen')
pass_to_sommelier = gen.activity('Pass alcoholic beverage orders to sommelier')
assign_to_waiter = gen.activity('Assign orders to available waiters')
check_waiter_availability = gen.activity('Check waiter availability')

# Process Owner 1: Kitchen
kitchen = gen.activity('Kitchen')
prepare_food = gen.activity('Prepare food based on orders')
gather_ingredients = gen.activity('Gather ingredients')
cook_plate = gen.activity('Cook and plate dishes')
notify_waiter = gen.activity('Notify waiter when food is ready')

# Process Owner 2: Sommelier
sommelier = gen.activity('Sommelier')
prepare_beverages = gen.activity('Prepare alcoholic beverages')
retrieve_wine = gen.activity('Select and retrieve wines from the cellar')
prepare_cocktails = gen.activity('Prepare cocktails')

# Process Owner 3: Waiter
waiter = gen.activity('Waiter')
prepare_service_cart = gen.activity('Prepare the service cart')
prepare_non_alcoholic_beverages = gen.activity('Prepare non-alcoholic beverages')
deliver_orders = gen.activity('Deliver orders to guest rooms')
debit_account = gen.activity('Debit guest accounts')

# Process Owner 4: Guest
guest = gen.activity('Guest')
enjoy_meal = gen.activity('Enjoy the meal')
decide_tipping = gen.activity('Decide whether to tip the waiter based on service quality')

# Define the order of activities for Room Service Manager
room_service_manager_poset = gen.partial_order(dependencies=[
    (take_order, submit_to_kitchen),
    (submit_to_kitchen, assign_to_waiter),
    (take_order, pass_to_sommelier),
    (pass_to_sommelier, assign_to_waiter),
    (take_order, check_waiter_availability),
    (check_waiter_availability, assign_to_waiter)
])

# Define the order of activities for Kitchen
kitchen_poset = gen.partial_order(dependencies=[
    (prepare_food, gather_ingredients),
    (gather_ingredients, cook_plate),
    (cook_plate, notify_waiter)
])

# Define the order of activities for Sommelier
sommelier_poset = gen.partial_order(dependencies=[
    (prepare_beverages, retrieve_wine),
    (retrieve_wine, prepare_cocktails)
])

# Define the order of activities for Waiter
waiter_poset = gen.partial_order(dependencies=[
    (prepare_service_cart, prepare_non_alcoholic_beverages),
    (prepare_non_alcoholic_beverages, deliver_orders),
    (deliver_orders, debit_account)
])

# Define the order of activities for Guest
guest_poset = gen.partial_order(dependencies=[
    (enjoy_meal, decide_tipping)
])

# Combine all the partial orders
final_model = gen.partial_order(dependencies=[
    (room_service_manager_poset, kitchen_poset),
    (room_service_manager_poset, sommelier_poset),
    (room_service_manager_poset, waiter_poset),
    (kitchen_poset, waiter_poset),
    (sommelier_poset, waiter_poset),
    (waiter_poset, guest_poset)
])
