gen = ModelGenerator()

# Define Activities for the Returns/Exchange Flow
initiate_request = gen.activity("Initiate Exchange Request: Customer requests an exchange. Handled by Returns/Exchange Management Team")
verify_generate_label = gen.activity("Verify & Generate Label: Returns/Exchange Management Team verifies and provides a return label")
customer_return_item = gen.activity("Return Item: Customer sends back the item")
monitor_inspect_return = gen.activity("Monitor & Inspect Return: Returns/Exchange Management Team monitors the return and inspects the item upon receipt")
notify_for_replacement_activity = gen.activity("Notify for Replacement: If inspection is successful, Returns/Exchange Management Team notifies Logistics/Delivery Team to send a replacement")
deliver_replacement_activity = gen.activity("Deliver Replacement: Logistics/Delivery Team delivers the replacement item")

# Define the sub-flow for actions taken if inspection is successful.
# This includes Notification for Replacement, followed by Delivery of Replacement.
successful_replacement_branch = gen.partial_order(dependencies=[
    (notify_for_replacement_activity, deliver_replacement_activity)
])

# Model the conditional execution of the successful replacement branch.
# After 'Monitor & Inspect Return', if inspection is successful, the 'successful_replacement_branch' occurs.
# Otherwise (e.g., inspection fails for this attempt, or no replacement is warranted), this branch is skipped (None).
post_inspection_decision = gen.xor(successful_replacement_branch, None)

# Define a single, complete cycle of the Returns/Exchange process.
# This sequence includes all steps from initiation up to the potential replacement delivery (which is conditional).
one_exchange_cycle = gen.partial_order(dependencies=[
    (initiate_request, verify_generate_label),
    (verify_generate_label, customer_return_item),
    (customer_return_item, monitor_inspect_return),
    (monitor_inspect_return, post_inspection_decision) # The conditional steps follow inspection
])

# Model the repetition of the entire exchange cycle.
# The loop(do=one_exchange_cycle, redo=None) means that if the exchange process is initiated,
# 'one_exchange_cycle' is performed at least once. It can then be repeated if the customer
# needs further exchanges for the same initial order context.
final_model = gen.loop(do=one_exchange_cycle, redo=None)
