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
tip = gen.activity('Tip')

# Subprocesses
kitchen_process = gen.partial_order(dependencies=[(submit_food_order.copy(), prepare_food)])
sommelier_process = gen.partial_order(dependencies=[(submit_alcohol_order.copy(), prepare_alcohol)])
waiter_process = gen.partial_order(dependencies=[(prepare_cart, prepare_non_alcoholic_drinks)])

# Main process
main_process = gen.partial_order(dependencies=[(receive_order, submit_food_order), (receive_order, submit_alcohol_order), (receive_order, assign_order_to_waiter), (assign_order_to_waiter, waiter_process), (kitchen_process, waiter_process), (sommelier_process, waiter_process), (waiter_process, tip)])

# Final model
final_model = main_process