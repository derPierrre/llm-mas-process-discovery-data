"""
This POWL model describes the room service process at The Evanstonian.

Process Summary:
1.  The Room Service Manager (RSM) takes a guest's order.
2.  The RSM then sends the food component of the order to the Kitchen and decides whether to send an alcoholic beverage component to the Sommelier.
3.  After these dispatches, the RSM assigns the complete order to a Room Service Waiter.
4.  The Kitchen Staff prepare the food upon receiving the order.
5.  If an alcoholic beverage order was sent, the Sommelier prepares it.
6.  The Waiter, upon assignment, prepares their service cart, gathers silverware, and optionally prepares non-alcoholic beverages.
7.  Once the food is ready from the kitchen and the waiter has finished their initial preparations, the waiter collects the food.
8.  If alcoholic beverages were prepared by the Sommelier and the waiter has finished their initial preparations, the waiter collects the alcoholic beverages.
9.  After all necessary items (food, optional alcoholic beverages, optional non-alcoholic beverages, silverware) are collected and on the cart, the Waiter delivers the order to the guest.
10. Finally, the Waiter debits the guest's account.
"""
gen = ModelGenerator()

# --- Define Activities --- 
# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order = gen.activity("RSM: Send food order to Kitchen")
rsm_C_send_alco_order = gen.activity("RSM: Send alcoholic beverage order to Sommelier") # This is RSM's action of sending
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 2: Sommelier
sommelier_F_prepare_alco_bev = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
waiter_I_prepare_non_alco_bev = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
waiter_K_collect_alco_bev_from_sommelier = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices --- 

# RSM's choice to send an alcoholic beverage order to the Sommelier or not.
rsm_C_optional_send_alco_order = gen.xor(rsm_C_send_alco_order, None)

# Waiter's choice to prepare non-alcoholic beverages or not.
waiter_I_optional_prep_non_alco_bev = gen.xor(waiter_I_prepare_non_alco_bev, None)

# Waiter's collection of alcoholic beverages is conditional on them being ordered and prepared.
# This XOR represents whether alcoholic beverages are collected (because they were ordered and prepared) or not (because they weren't).
# The actual act of collection (waiter_K_collect_alco_bev_from_sommelier) will only be triggered if sommelier_F_prepare_alco_bev happens.
waiter_K_optional_collect_alco_bev = gen.xor(waiter_K_collect_alco_bev_from_sommelier, None)

# --- Define Sub-Process Blocks --- 

# Waiter's initial concurrent preparation tasks (done after order assignment).
waiter_initial_preparation_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_I_optional_prep_non_alco_bev,)
])

# --- Main Process Flow --- 
# Defined as a single partial order with dependencies between activities and choice blocks.
final_model = gen.partial_order(dependencies=[
    # 1. RSM takes order. Then, RSM sends food order and (optionally) alcoholic beverage order concurrently.
    (rsm_A_take_order, rsm_B_send_food_order),
    (rsm_A_take_order, rsm_C_optional_send_alco_order),

    # 2. RSM assigns order to waiter after sending food order AND after deciding on/sending alcoholic beverage order.
    (rsm_B_send_food_order, rsm_D_assign_order_to_waiter),
    (rsm_C_optional_send_alco_order, rsm_D_assign_order_to_waiter),

    # 3. Kitchen prepares food after receiving the order from RSM.
    (rsm_B_send_food_order, kitchen_E_prepare_food),

    # 4. Sommelier prepares alcoholic beverages IF the order was sent by RSM.
    #    (If rsm_C_send_alco_order is chosen in the XOR, it triggers sommelier_F_prepare_alco_bev).
    (rsm_C_send_alco_order, sommelier_F_prepare_alco_bev),

    # 5. Waiter performs initial preparations after the order is assigned.
    (rsm_D_assign_order_to_waiter, waiter_initial_preparation_block),

    # 6. Waiter collects food from kitchen after food is prepared AND waiter's initial prep is done.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_preparation_block, waiter_J_collect_food_from_kitchen),

    # 7. Waiter collects alcoholic beverages IF Sommelier prepared them AND waiter's initial prep is done.
    #    The actual collection (waiter_K_collect_alco_bev_from_sommelier) is linked to sommelier_F_prepare_alco_bev.
    #    The waiter_K_optional_collect_alco_bev XOR node handles the optionality for the delivery step.
    (sommelier_F_prepare_alco_bev, waiter_K_collect_alco_bev_from_sommelier),
    (waiter_initial_preparation_block, waiter_K_collect_alco_bev_from_sommelier),

    # 8. Waiter delivers order after collecting food AND after (optionally) collecting alcoholic beverages.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (waiter_K_optional_collect_alco_bev, waiter_L_deliver_order_to_guest), # Depends on the XOR node

    # 9. Waiter debits guest account after delivering the order.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
