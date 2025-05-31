gen = ModelGenerator()

# Define activities
login = gen.activity('Login')
add_items = gen.activity('Add Items')
select_reward = gen.activity('Select Reward')
select_payment_method = gen.activity('Select Payment Method')
process_payment = gen.activity('Process Payment')
deliver_items = gen.activity('Deliver Items')
process_return = gen.activity('Process Return')
deliver_replacement = gen.activity('Deliver Replacement')

# Define partial order dependencies
poset = gen.partial_order(dependencies=[
    (login, add_items),
    (add_items, select_reward),
    (select_reward, select_payment_method),
    (select_payment_method, process_payment),
    (process_payment, deliver_items),
    (deliver_items, process_return),
    (process_return, deliver_replacement)
])

# Assign the final model
final_model = poset