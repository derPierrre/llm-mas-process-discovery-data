gen = ModelGenerator()

# Define activities
manager_takes_order = gen.activity('Room Service Manager takes guest order')
manager_submits_food_order = gen.activity('Room Service Manager submits food order to kitchen')
manager_handles_beverage_order = gen.activity('Room Service Manager handles beverage order with sommelier')
manager_assigns_order = gen.activity('Room Service Manager assigns completed orders to waiter')

kitchen_receives_order = gen.activity('Kitchen Staff receives room service order')
kitchen_prepares_food = gen.activity('Kitchen Staff prepares food')
kitchen_hands_off_meal = gen.activity('Kitchen Staff hands off prepared meals to waiter')

sommelier_fulfills_beverage_order = gen.activity('Sommelier fulfills beverage order')
sommelier_retrieves_wine = gen.activity('Sommelier retrieves wine from cellar')
sommelier_prepares_beverages = gen.activity('Sommelier prepares other alcoholic beverages')
sommelier_prepares_order = gen.activity('Sommelier prepares orders for waiters to pick up')

waiter_prepares_cart = gen.activity('Room Service Waiter prepares the service cart')
waiter_handles_non_alcoholic_drinks = gen.activity('Room Service Waiter handles non-alcoholic drinks')
waiter_delivers_order = gen.activity('Room Service Waiter delivers the order')
waiter_debits_account = gen.activity('Room Service Waiter debits the guest account')

guest_decides_tip = gen.activity('Guest decides whether or not to tip the waiter')

# Define sub-processes
manager_process = gen.partial_order(dependencies=[
    (manager_takes_order, manager_submits_food_order),
    (manager_takes_order, manager_handles_beverage_order),
    (manager_submits_food_order, manager_assigns_order),
    (manager_handles_beverage_order, manager_assigns_order)
])

kitchen_process = gen.partial_order(dependencies=[
    (kitchen_receives_order, kitchen_prepares_food),
    (kitchen_prepares_food, kitchen_hands_off_meal)
])

sommelier_process = gen.partial_order(dependencies=[
    (sommelier_fulfills_beverage_order, sommelier_retrieves_wine),
    (sommelier_fulfills_beverage_order, sommelier_prepares_beverages),
    (sommelier_retrieves_wine, sommelier_prepares_order),
    (sommelier_prepares_beverages, sommelier_prepares_order)
])

waiter_process = gen.partial_order(dependencies=[
    (waiter_prepares_cart, waiter_handles_non_alcoholic_drinks),
    (waiter_handles_non_alcoholic_drinks, waiter_delivers_order),
    (waiter_delivers_order, waiter_debits_account)
])

# Combine all sub-processes
final_model = gen.partial_order(dependencies=[
    (manager_process, kitchen_process),
    (manager_process, sommelier_process),
    (kitchen_process, waiter_process),
    (sommelier_process, waiter_process),
    (waiter_process, gues_decides_tip)
])
