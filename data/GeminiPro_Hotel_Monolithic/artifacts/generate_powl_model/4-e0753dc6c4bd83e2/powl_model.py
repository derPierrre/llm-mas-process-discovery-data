
"""
This POWL model describes the room service process at The Evanstonian.

Process Breakdown:
1.  RSM Takes Order: The process begins with the Room Service Manager (RSM) taking the guest's order.
2.  RSM Dispatch Initiation (Concurrent): After taking the order, the RSM initiates two streams concurrently:
    a.  Food Order: Sends the food order to the Kitchen.
    b.  Alcoholic Beverage Decision: An XOR choice. If alcoholic beverages are ordered, the RSM sends the order to the Sommelier; otherwise, this path is skipped.
3.  Preparation Sub-Processes (Conditional & Concurrent):
    a.  Kitchen Prepares Food: Triggered after the RSM sends the food order.
    b.  Sommelier Prepares Beverages: Triggered ONLY IF the RSM actually sent an alcoholic beverage order (i.e., the 'yes' path of the XOR was taken).
4.  RSM Assigns Order to Waiter: This occurs after the RSM has both sent the food order AND the alcoholic beverage decision/dispatch process has been resolved (i.e., the XOR choice is complete).
5.  Waiter's Initial Preparations (Concurrent Tasks in a block): Upon assignment, the waiter performs several tasks concurrently:
    a.  Prepares service cart.
    b.  Gathers silverware.
    c.  Optionally prepares non-alcoholic beverages (an XOR choice for the waiter). This choice block is part of these initial tasks.
    This entire block of initial preparations must complete before the waiter can proceed to collect items.
6.  Waiter Collects Items (Dependencies on prior steps):
    a.  Collects Food: Depends on BOTH the Kitchen having prepared the food AND the waiter having completed their entire initial preparations block.
    b.  Optionally Collects Alcoholic Beverages (XOR choice): The waiter decides to collect alcoholic beverages. The actual activity of collecting alcoholic beverages can only occur IF the Sommelier has prepared them AND the waiter has completed their initial preparations block. The XOR node itself represents the choice outcome.
7.  Waiter Delivers Order: Depends on the waiter having collected the food AND the optional alcoholic beverage collection choice having been resolved (i.e., collected or skipped/not applicable).
8.  Waiter Debits Account: Occurs after successful delivery.
"""
gen = ModelGenerator()

# --- Define Individual Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order_to_kitchen = gen.activity("RSM: Send food order to Kitchen")
# Activity for RSM sending alco order; its execution is determined by an XOR.
rsm_C_ACT_send_alco_order_to_sommelier = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 2: Sommelier
# Activity for Sommelier preparing alco; its execution depends on RSM's action.
sommelier_F_ACT_prepare_alco_bev = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
# Activity for Waiter preparing non-alco; its execution is determined by an XOR.
waiter_I_ACT_prepare_non_alco_bev = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
# Activity for Waiter collecting alco; its execution is determined by an XOR and other conditions.
waiter_K_ACT_collect_alco_bev_from_sommelier = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices (XOR constructs) and Intermediate Blocks --- 

# RSM's decision block for sending alcoholic beverage order.
rsm_XOR_choice_send_alco_order = gen.xor(rsm_C_ACT_send_alco_order_to_sommelier, None)

# Waiter's optional preparation of non-alcoholic beverages.
waiter_XOR_choice_prep_non_alco_bev = gen.xor(waiter_I_ACT_prepare_non_alco_bev, None)

# Waiter's initial concurrent preparation tasks. This block must complete before item collection.
waiter_initial_prep_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_XOR_choice_prep_non_alco_bev,) # Depends on the XOR node for non-alco bevs
])

# Waiter's optional collection of alcoholic beverages.
# The XOR node represents the outcome of this choice for subsequent steps.
waiter_XOR_choice_collect_alco_bev = gen.xor(waiter_K_ACT_collect_alco_bev_from_sommelier, None)

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # 1. RSM takes order.
    (rsm_A_take_order, rsm_B_send_food_order_to_kitchen), # Take order then send food
    (rsm_A_take_order, rsm_XOR_choice_send_alco_order), # Concurrently, take order then decide on alco

    # 2. Kitchen prepares food after receiving the order from RSM.
    (rsm_B_send_food_order_to_kitchen, kitchen_E_prepare_food),

    # 3. Sommelier prepares alcoholic beverages IF RSM ACTUALLY sent the order.
    #    Dependency is on the activity *within* the XOR.
    (rsm_C_ACT_send_alco_order_to_sommelier, sommelier_F_ACT_prepare_alco_bev),

    # 4. RSM assigns order to waiter after sending food order AND after the alco bev decision (XOR) is resolved.
    (rsm_B_send_food_order_to_kitchen, rsm_D_assign_order_to_waiter),
    (rsm_XOR_choice_send_alco_order, rsm_D_assign_order_to_waiter),

    # 5. Waiter performs initial preparations (block) after the order is assigned.
    (rsm_D_assign_order_to_waiter, waiter_initial_prep_block),

    # 6. Waiter collects food from kitchen after food is prepared AND waiter's initial prep block is done.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_prep_block, waiter_J_collect_food_from_kitchen),

    # 7. Preconditions for the waiter's *activity* of collecting alcoholic beverages.
    #    This activity is an option within the waiter_XOR_choice_collect_alco_bev.
    #    It can only happen if Sommelier prepared them AND waiter's initial prep is done.
    (sommelier_F_ACT_prepare_alco_bev, waiter_K_ACT_collect_alco_bev_from_sommelier),
    (waiter_initial_prep_block, waiter_K_ACT_collect_alco_bev_from_sommelier),

    # 8. Waiter delivers order after collecting food AND after the alco bev collection XOR choice is resolved.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (waiter_XOR_choice_collect_alco_bev, waiter_L_deliver_order_to_guest),

    # 9. Waiter debits guest account after delivering the order.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
