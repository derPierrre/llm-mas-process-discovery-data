gen = ModelGenerator()

# Activities
receive_order = gen.activity('Receive order from guest')
submit_food_order = gen.activity('Submit food order to kitchen')
submit_alcohol_order = gen.activity('Submit alcohol order to sommelier')
assign_order_to_waiter = gen.activity('Assign order to waiter')

prepare_food = gen.activity('Prepare food')
prepare_alcohol = gen.activity('Prepare alcohol')

prepare_cart = gen.activity('Prepare cart')
prepare_non_alcoholic_drinks = gen.activity('Prepare non-alcoholic drinks')
load_cart_kitchen = gen.activity('Load cart')
load_cart_sommelier = gen.activity('Load cart')
load_cart_waiter = gen.activity('Load cart')
tip = gen.activity('Tip')

# Subprocesses
kitchen_process = gen.partial_order(dependencies=[(submit_food_order.copy(), prepare_food), (prepare_food, load_cart_kitchen)])
sommelier_process = gen.partial_order(dependencies=[(submit_alcohol_order.copy(), prepare_alcohol), (prepare_alcohol, load_cart_sommelier)])
waiter_process = gen.partial_order(dependencies=[(prepare_cart, prepare_non_alcoholic_drinks), (prepare_non_alcoholic_drinks, load_cart_waiter)])

# Main process
main_process = gen.partial_order(dependencies=[(receive_order, submit_food_order), (receive_order, submit_alcohol_order), (receive_order, assign_order_to_waiter), (assign_order_to_waiter, waiter_process), (kitchen_process, load_cart_kitchen), (sommelier_process, load_cart_sommelier), (waiter_process, load_cart_waiter), (load_cart_kitchen, tip), (load_cart_sommelier, tip), (load_cart_waiter, tip)])

# Final model
final_model = main_process