
"""
This POWL model describes the room service process at The Evanstonian.

Process Breakdown:
1.  RSM Takes Order: The process begins with the Room Service Manager (RSM) taking the guest's order.
2.  RSM Dispatch Initiation (Concurrent): Concurrently, the RSM initiates two streams:
    a.  Food Order: Sends the food order to the Kitchen.
    b.  Alcoholic Beverage Decision: Decides whether alcoholic beverages are part of the order. This is an XOR choice.
        i.  If YES: RSM sends the order to the Sommelier.
        ii. If NO: This path is skipped.
3.  Preparation Sub-Processes (Conditional & Concurrent):
    a.  Kitchen Prepares Food: Triggered by the RSM sending the food order.
    b.  Sommelier Prepares Beverages: Triggered ONLY IF the RSM sent an alcoholic beverage order.
4.  RSM Assigns Order to Waiter: This occurs after the RSM has sent the food order AND has resolved the alcoholic beverage decision (i.e., sent the order or decided against it).
5.  Waiter's Initial Preparations (Concurrent Tasks): Upon assignment, the waiter performs several tasks concurrently:
    a.  Prepares service cart.
    b.  Gathers silverware.
    c.  Optionally prepares non-alcoholic beverages (an XOR choice for the waiter).
    These tasks must complete before the waiter can collect items.
6.  Waiter Collects Items (Conditional & Concurrent Dependencies):
    a.  Collects Food: Depends on BOTH the Kitchen having prepared the food AND the waiter having completed their initial preparations.
    b.  Collects Alcoholic Beverages (Optional Action): This is an XOR choice for the waiter.
        i.  If YES (Waiter Collects Alco): This action depends on BOTH the Sommelier having prepared the beverages (which means they must have been ordered) AND the waiter having completed their initial preparations.
        ii. If NO (Waiter Skips Alco Collection): This path is taken if alco wasn't ordered/prepared, or if the waiter skips for other reasons (though the prompt implies collection if prepared).
7.  Waiter Delivers Order: Depends on the waiter having collected the food AND the alcoholic beverage collection process being resolved (either collected or skipped/not applicable).
8.  Waiter Debits Account: Occurs after successful delivery.
"""
gen = ModelGenerator()

# --- Define Individual Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order_to_kitchen = gen.activity("RSM: Send food order to Kitchen")
# RSM's action of sending alco order; its execution is decided by an XOR later.
rsm_C_send_alco_order_to_sommelier_ACT = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 2: Sommelier
# Sommelier's action; its execution depends on RSM sending the order.
sommelier_F_prepare_alco_bev_ACT = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
# Waiter's action of prepping non-alco; its execution is decided by an XOR later.
waiter_I_prepare_non_alco_bev_ACT = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
# Waiter's action of collecting alco; its execution is decided by an XOR and other conditions.
waiter_K_collect_alco_bev_from_sommelier_ACT = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices (XOR constructs) and Intermediate Blocks --- 

# RSM's decision block for sending alcoholic beverage order.
# If rsm_C_send_alco_order_to_sommelier_ACT is chosen, it then triggers Sommelier prep.
rsm_choice_send_alco_order = gen.xor(rsm_C_send_alco_order_to_sommelier_ACT, None)

# Waiter's optional preparation of non-alcoholic beverages.
waiter_choice_prep_non_alco_bev = gen.xor(waiter_I_prepare_non_alco_bev_ACT, None)

# Waiter's initial concurrent preparation tasks. This block must complete before item collection.
waiter_initial_prep_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_choice_prep_non_alco_bev,) # Depends on the XOR node for non-alco bevs
])

# Waiter's optional collection of alcoholic beverages.
# The actual activity waiter_K_collect_alco_bev_from_sommelier_ACT has preconditions (Sommelier prep, Waiter init prep).
# If those preconditions aren't met, this XOR will effectively result in 'None'.
waiter_choice_collect_alco_bev = gen.xor(waiter_K_collect_alco_bev_from_sommelier_ACT, None)

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # 1. RSM takes order. Then, concurrently, RSM sends food order AND makes alco bev decision.
    (rsm_A_take_order, rsm_B_send_food_order_to_kitchen),
    (rsm_A_take_order, rsm_choice_send_alco_order), # RSM decides if alco order is sent

    # 2. Kitchen prepares food after receiving the order from RSM.
    (rsm_B_send_food_order_to_kitchen, kitchen_E_prepare_food),

    # 3. Sommelier prepares alcoholic beverages IF RSM sent the order.
    #    This dependency is on the actual activity within the XOR choice.
    (rsm_C_send_alco_order_to_sommelier_ACT, sommelier_F_prepare_alco_bev_ACT),

    # 4. RSM assigns order to waiter after sending food order AND after the alco bev decision process is resolved.
    (rsm_B_send_food_order_to_kitchen, rsm_D_assign_order_to_waiter),
    (rsm_choice_send_alco_order, rsm_D_assign_order_to_waiter), # Assignment waits for food dispatch and alco decision resolution

    # 5. Waiter performs initial preparations after the order is assigned.
    (rsm_D_assign_order_to_waiter, waiter_initial_prep_block),

    # 6. Waiter collects food from kitchen after food is prepared AND waiter's initial prep is done.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_prep_block, waiter_J_collect_food_from_kitchen),

    # 7. Preconditions for the actual waiter_K_collect_alco_bev_from_sommelier_ACT activity.
    #    This activity is wrapped in the waiter_choice_collect_alco_bev XOR.
    #    If sommelier_F_prepare_alco_bev_ACT does not occur (because rsm_C was not chosen), then this dependency ensures waiter_K cannot occur.
    (sommelier_F_prepare_alco_bev_ACT, waiter_K_collect_alco_bev_from_sommelier_ACT),
    (waiter_initial_prep_block, waiter_K_collect_alco_bev_from_sommelier_ACT),

    # 8. Waiter delivers order after collecting food AND after the alco bev collection choice is resolved.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (waiter_choice_collect_alco_bev, waiter_L_deliver_order_to_guest), # Delivery waits for food and the alco collection choice resolution

    # 9. Waiter debits guest account after delivering the order.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
