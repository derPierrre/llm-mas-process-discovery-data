gen = ModelGenerator()

# Define Activities for the Returns/Exchange Flow
initiate_exchange_request = gen.activity("Customer Initiates Exchange Request (Received by Returns/Exchange Management Team)")
return_verification_label_generation = gen.activity("Return Verification & Label Generation (Returns/Exchange Management Team)")
customer_returns_item_activity = gen.activity("Customer Returns Item (Customer activity)")
shipment_monitoring_inspection = gen.activity("Return Shipment Monitoring & Item Inspection (Returns/Exchange Management Team)")
notification_for_replacement = gen.activity("Notification for Replacement Delivery (Returns/Exchange Management Team notifies Logistics/Delivery Team if inspection is successful)")
replacement_item_delivery_activity = gen.activity("Replacement Item Delivery (Logistics/Delivery Team)")

# Define the sub-flow for actions taken if inspection is successful.
# This includes Notification for Replacement Delivery followed by Replacement Item Delivery.
successful_inspection_branch = gen.partial_order(dependencies=[
    (notification_for_replacement, replacement_item_delivery_activity)
])

# Model the conditional execution of the successful inspection branch.
# After 'Return Shipment Monitoring & Item Inspection', if the inspection is successful,
# the 'successful_inspection_branch' occurs. Otherwise, it's skipped (None).
conditional_replacement_steps = gen.xor(successful_inspection_branch, None)

# Define a single cycle of the Returns/Exchange process.
# This sequence includes all steps from initiation up to the potential replacement delivery (which is conditional).
one_exchange_cycle = gen.partial_order(dependencies=[
    (initiate_exchange_request, return_verification_label_generation),
    (return_verification_label_generation, customer_returns_item_activity),
    (customer_returns_item_activity, shipment_monitoring_inspection),
    (shipment_monitoring_inspection, conditional_replacement_steps) # The conditional steps follow inspection
])

# Model the repetition of the entire exchange cycle.
# The loop(do=one_exchange_cycle, redo=None) means that if the exchange process is started,
# 'one_exchange_cycle' is performed at least once, and then it can be repeated if the customer
# needs to exchange an item multiple times for the same initial order context.
final_model = gen.loop(do=one_exchange_cycle, redo=None)
