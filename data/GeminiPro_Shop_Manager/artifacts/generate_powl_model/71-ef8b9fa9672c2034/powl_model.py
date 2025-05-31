gen = ModelGenerator()

# Define Activities for the Returns/Exchange Flow
initiate_exchange_activity = gen.activity("Initiate Exchange (Returns/Exchange Team)")
verify_label_activity = gen.activity("Verify & Label (Returns/Exchange Team)")
customer_returns_item_activity = gen.activity("Customer Returns Item (Customer)")
inspect_return_activity = gen.activity("Inspect Return (Returns/Exchange Team)")
notify_for_replacement_activity = gen.activity("Notify for Replacement (Returns/Exchange Team to Logistics)")
deliver_replacement_activity = gen.activity("Deliver Replacement (Logistics Team)")

# Define the sub-flow for actions taken if inspection is okay (successful)
# This includes Notification for Replacement, followed by Delivery of Replacement.
successful_inspection_branch = gen.partial_order(dependencies=[
    (notify_for_replacement_activity, deliver_replacement_activity)
])

# Model the conditional execution of the successful inspection branch.
# After 'Inspect Return', if inspection is okay, the 'successful_inspection_branch' occurs.
# Otherwise (e.g., inspection is not okay, or replacement is not warranted for this attempt), this branch is skipped (None).
conditional_replacement_steps = gen.xor(successful_inspection_branch, None)

# Define a single, complete cycle of the Returns/Exchange process.
# This sequence includes all steps from initiation up to the potential replacement delivery (which is conditional on inspection).
one_exchange_cycle = gen.partial_order(dependencies=[
    (initiate_exchange_activity, verify_label_activity),
    (verify_label_activity, customer_returns_item_activity),
    (customer_returns_item_activity, inspect_return_activity),
    (inspect_return_activity, conditional_replacement_steps) # The conditional steps follow inspection
])

# Model the repetition of the entire exchange cycle.
# The loop(do=one_exchange_cycle, redo=None) means that if the exchange process is initiated,
# 'one_exchange_cycle' is performed at least once. It can then be repeated if the customer
# requires another exchange for the same underlying issue or order.
final_model = gen.loop(do=one_exchange_cycle, redo=None)
