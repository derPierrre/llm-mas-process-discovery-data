gen = ModelGenerator()

# Define activities
customer_login = gen.activity('Customer Login')
add_to_cart = gen.activity('Add Items to Cart')
select_payment = gen.activity('Select Payment Method')
select_reward = gen.activity('Select Reward')
delivery = gen.activity('Delivery')
return_exchange = gen.activity('Return/Exchange')

# Define partial order dependencies
final_model = gen.partial_order(
    dependencies=[
        (customer_login, add_to_cart),
        (add_to_cart, select_payment),
        (select_payment, select_reward),
        (select_reward, delivery),
        (delivery, return_exchange)
    ]
)