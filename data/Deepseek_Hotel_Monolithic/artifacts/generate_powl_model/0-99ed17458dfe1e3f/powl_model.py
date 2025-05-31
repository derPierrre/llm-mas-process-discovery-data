gen = ModelGenerator()
place_order = gen.activity('Place order')
prepare_food = gen.activity('Prepare food')
prepare_beverages = gen.activity('Prepare beverages')
prepare_cart = gen.activity('Prepare cart')
deliver_order = gen.activity('Deliver order')
tip_waiter = gen.activity('Tip waiter')

# Parallel preparation of food and beverages
parallel_prep = gen.partial_order(dependencies=[(prepare_food,), (prepare_beverages,)])

# Waiter prepares cart while food and beverages are being prepared
poset_1 = gen.partial_order(dependencies=[(parallel_prep, deliver_order), (prepare_cart, deliver_order)])

# Optional tipping
final_model = gen.partial_order(dependencies=[(place_order, poset_1), (poset_1, tip_waiter)])