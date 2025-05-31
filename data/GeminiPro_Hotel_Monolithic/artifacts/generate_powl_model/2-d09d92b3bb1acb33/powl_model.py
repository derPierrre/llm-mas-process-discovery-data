
"""
This POWL model describes the room service process at The Evanstonian.

Process Summary:
1.  The Room Service Manager (RSM) takes a guest's order.
2.  The RSM then sends the food component of the order to the Kitchen and concurrently decides whether to send an alcoholic beverage order to the Sommelier.
3.  The Kitchen Staff prepare the food upon receiving the order.
4.  If an alcoholic beverage order was sent by the RSM, the Sommelier prepares it.
5.  After sending the food order and making the decision/sending the alcoholic beverage order, the RSM assigns the complete order to a Room Service Waiter.
6.  The Waiter, upon assignment, concurrently prepares their service cart, gathers silverware, and optionally prepares non-alcoholic beverages.
7.  Once the food is ready from the kitchen and the waiter has finished their initial preparations, the waiter collects the food.
8.  If alcoholic beverages were prepared by the Sommelier and the waiter has finished their initial preparations, the waiter collects the alcoholic beverages. This collection is optional.
9.  After all necessary items (food, and any collected alcoholic/non-alcoholic beverages, silverware) are ready, the Waiter delivers the order to the guest.
10. Finally, the Waiter debits the guest's account.
"""
gen = ModelGenerator()

# --- Define Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order = gen.activity("RSM: Send food order to Kitchen")
act_rsm_send_alco = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 2: Sommelier
act_sommelier_prep_alco = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
act_waiter_prep_non_alco = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
act_waiter_collect_alco = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices (XOR constructs) --- 

# RSM's choice to send an alcoholic beverage order to the Sommelier or not.
choice_rsm_sends_alco = gen.xor(act_rsm_send_alco, None)

# Waiter's choice to prepare non-alcoholic beverages or not.
choice_waiter_prep_non_alco = gen.xor(act_waiter_prep_non_alco, None)

# Waiter's choice/action to collect alcoholic beverages (which depends on them being prepared).
choice_waiter_collects_alco = gen.xor(act_waiter_collect_alco, None)

# --- Define Sub-Process Blocks (Partial Orders for concurrency) --- 

# Waiter's initial concurrent preparation tasks (done after order assignment).
# This block completes when cart & silverware are ready, and non-alco bev decision/prep is done.
waiter_initial_tasks = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (choice_waiter_prep_non_alco,) # Depends on the XOR node, meaning this task group waits for the choice to be made and action (if any) completed.
])

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # 1. RSM takes order. Then, RSM starts sending food order AND concurrently makes the decision about alcoholic beverages.
    (rsm_A_take_order, rsm_B_send_food_order),
    (rsm_A_take_order, choice_rsm_sends_alco), # RSM initiates food dispatch and alco decision concurrently

    # 2. Kitchen Staff prepares food upon receiving the order from RSM.
    (rsm_B_send_food_order, kitchen_E_prepare_food),

    # 3. If RSM chose to send the alcoholic beverage order (act_rsm_send_alco is performed), then Sommelier prepares them.
    (act_rsm_send_alco, act_sommelier_prep_alco), # Sommelier acts only if RSM sent the order

    # 4. RSM assigns order to waiter after sending food order AND after the alcoholic beverage decision/dispatch process is resolved.
    (rsm_B_send_food_order, rsm_D_assign_order_to_waiter),
    (choice_rsm_sends_alco, rsm_D_assign_order_to_waiter), # Assignment waits for food dispatch and alco choice completion

    # 5. Waiter performs initial preparations after the order is assigned.
    (rsm_D_assign_order_to_waiter, waiter_initial_tasks),

    # 6. Waiter collects food from kitchen after food is prepared AND waiter's initial prep is done.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_tasks, waiter_J_collect_food_from_kitchen),

    # 7. Waiter collects alcoholic beverages IF Sommelier prepared them AND waiter's initial prep is done.
    #    act_waiter_collect_alco is the activity within choice_waiter_collects_alco.
    #    This ensures act_waiter_collect_alco only runs if its preconditions (sommelier prep, waiter initial tasks) are met.
    (act_sommelier_prep_alco, act_waiter_collect_alco),
    (waiter_initial_tasks, act_waiter_collect_alco),

    # 8. Waiter delivers order after collecting food AND after the optional alcoholic beverage collection process is resolved (collected or skipped).
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (choice_waiter_collects_alco, waiter_L_deliver_order_to_guest), # Delivery waits for food and the alco collection choice completion

    # 9. Waiter debits guest account after delivering the order.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
