gen = ModelGenerator()

# Define activities
login = gen.activity("Customer initiates login")
authenticate = gen.activity("Authenticate customer")
add_items = gen.activity("Customer adds items to cart")
calculate_total = gen.activity("Calculate total purchase amount")
process_payment_activity = gen.activity("Process payment")
select_reward_activity = gen.activity("Select Reward")
prepare_shipping = gen.activity("Prepare order for shipping")
deliver_order = gen.activity("Deliver order to customer")

# Model optional "Select Reward"
optional_select_reward = gen.xor(select_reward_activity, None)

# Define the partial order for the main flow
final_model = gen.partial_order(dependencies=[
    (login, authenticate),
    (authenticate, add_items),
    (add_items, calculate_total),
    (calculate_total, process_payment_activity),
    (calculate_total, optional_select_reward),
    (process_payment_activity, prepare_shipping),
    (prepare_shipping, deliver_order)
])