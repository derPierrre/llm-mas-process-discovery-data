gen = ModelGenerator()
authentication = gen.activity('Authentication (Process Owner 0)')
shopping = gen.activity('Shopping/Add Items to Cart (Process Owner 1)')
payment = gen.activity('Payment (Process Owner 2)')
rewards = gen.activity('Rewards (Process Owner 3)')
delivery = gen.activity('Delivery (Process Owner 4)')
returns_exchanges = gen.activity('Returns/Exchanges (Process Owner 5)')
logistics = gen.activity('Logistics (Process Owner 4)')

# Define the sequential flow
dependencies = [
    (authentication, shopping),
    (shopping, payment),
    (payment, rewards),
    (rewards, delivery),
    (delivery, returns_exchanges),
    (returns_exchanges, logistics)
]

final_model = gen.partial_order(dependencies=dependencies)