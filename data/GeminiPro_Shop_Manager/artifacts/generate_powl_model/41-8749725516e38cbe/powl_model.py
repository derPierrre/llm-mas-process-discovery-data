gen = ModelGenerator()

# Define Activities for the Returns/Exchange Flow
initiate_exchange_request = gen.activity("Customer Initiates Exchange Request (Received by Returns/Exchange Management Team)")
return_verification_label_generation = gen.activity("Return Verification & Label Generation (Returns/Exchange Management Team)")
customer_returns_item_activity = gen.activity("Customer Returns Item (Customer activity)")
shipment_monitoring_inspection = gen.activity("Return Shipment Monitoring & Item Inspection (Returns/Exchange Management Team)")
notification_for_replacement = gen.activity("Notification for Replacement Delivery (Returns/Exchange Management Team notifies Logistics/Delivery Team if inspection is successful)")
replacement_item_delivery_activity = gen.activity("Replacement Item Delivery (Logistics/Delivery Team)")

# Define the sub-flow for actions taken if inspection is successful
# This includes Notification and Replacement Item Delivery
successful_inspection_branch = gen.partial_order(dependencies=[
    (notification_for_replacement, replacement_item_delivery_activity)
])

# Model the conditional execution of the successful inspection branch
# If inspection is not successful, this branch is skipped for the current exchange attempt.
conditional_replacement_steps = gen.xor(successful_inspection_branch, None)

# Define a single cycle of the Returns/Exchange process
# This includes all steps from initiation to potential replacement delivery.
one_exchange_cycle = gen.partial_order(dependencies=[
    (initiate_exchange_request, return_verification_label_generation),
    (return_verification_label_generation, customer_returns_item_activity),
    (customer_returns_item_activity, shipment_monitoring_inspection),
    (shipment_monitoring_inspection, conditional_replacement_steps)
])

# Model the repetition of the entire exchange cycle
# The loop(do=one_exchange_cycle, redo=None) means the cycle is performed at least once
# if the exchange process is initiated, and can then be repeated.
final_model = gen.loop(do=one_exchange_cycle, redo=None)
