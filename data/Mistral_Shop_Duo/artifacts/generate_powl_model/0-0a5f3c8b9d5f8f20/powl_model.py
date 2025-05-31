gen = ModelGenerator()

# Define activities
authenticate_customer = gen.activity('Authenticate Customer')
select_items = gen.activity('Select Items')
setup_payment = gen.activity('Setup Payment')
process_payment = gen.activity('Process Payment')
create_installment = gen.activity('Create Installment Agreement')
present_rewards = gen.activity('Present Rewards')
select_reward = gen.activity('Select Reward')
deliver_items = gen.activity('Deliver Items')
process_return = gen.activity('Process Return')
arrange_replacement_delivery = gen.activity('Arrange Replacement Delivery')
deliver_replacement = gen.activity('Deliver Replacement')

# Define submodels
payment_choice = gen.xor(process_payment, create_installment)

# Define partial order dependencies
poset = gen.partial_order(dependencies=[
    (authenticate_customer, select_items),
    (select_items, setup_payment),
    (setup_payment, payment_choice),
    (payment_choice, present_rewards),
    (present_rewards, select_reward),
    (select_reward, deliver_items),
    (deliver_items, process_return),
    (process_return, arrange_replacement_delivery),
    (arrange_replacement_delivery, deliver_replacement)
])

# Final model
final_model = poset