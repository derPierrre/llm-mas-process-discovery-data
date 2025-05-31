
"""
This POWL model describes the room service process at The Evanstonian.

Process Breakdown:
1.  RSM Takes Order: The process starts.
2.  Concurrent RSM Actions & Kitchen Prep:
    a.  RSM sends food order to Kitchen. Kitchen Staff then prepare food.
    b.  RSM decides on alcoholic beverages (Optional Path - AlcoHandling):
        i.  RSM sends alcoholic beverage order to Sommelier.
        ii. Sommelier prepares alcoholic beverages.
    This entire AlcoHandling path (i.i and i.ii) is optional.
3.  RSM Assigns Order to Waiter: This occurs after RSM has sent the food order AND the AlcoHandling optional path is resolved (i.e., completed or skipped).
4.  Waiter Initial Preparations: Upon assignment, the Waiter concurrently:
    a.  Prepares service cart.
    b.  Gathers silverware.
    c.  Optionally prepares non-alcoholic beverages (XOR choice for waiter).
    This block is `waiter_initial_prep_block`.
5.  Waiter Collects Food: Depends on Kitchen having prepared food AND Waiter having completed `waiter_initial_prep_block`.
6.  Waiter Optionally Collects Alcoholic Beverages:
    This is an optional activity for the waiter (`act_waiter_collects_alco`).
    It can only occur IF the Sommelier actually prepared beverages (i.e., the AlcoHandling path was taken and `act_sommelier_prepares_alco` completed) AND the waiter has completed `waiter_initial_prep_block`.
    This is modeled as `optional_waiter_collects_alco_XOR = xor(act_waiter_collects_alco, None)`.
    The dependencies for `act_waiter_collects_alco` will be set in the main partial order.
7.  Waiter Delivers Order: Depends on Waiter having collected food AND the `optional_waiter_collects_alco_XOR` being resolved (alco collected or skipped).
8.  Waiter Debits Account: Occurs after delivery.
"""
gen = ModelGenerator()

# --- Define Individual Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order_to_kitchen = gen.activity("RSM: Send food order to Kitchen")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Activities for the optional alcohol handling path initiated by RSM
act_rsm_sends_alco_order = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
act_sommelier_prepares_alco = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
waiter_I_ACT_prepare_non_alco_bev = gen.activity("Waiter: Prepare non-alcoholic beverages") # Actual activity
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
act_waiter_collects_alco = gen.activity("Waiter: Collect alcoholic beverages from Sommelier") # Actual activity
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices & Sub-Processes --- 

# 1. RSM & Sommelier Alcohol Handling Path (Optional)
# This sequence (RSM sends -> Sommelier prepares) is optional.
rsm_sommelier_alco_handling_sequence = gen.partial_order(dependencies=[
    (act_rsm_sends_alco_order, act_sommelier_prepares_alco)
])
optional_rsm_sommelier_alco_handling_XOR = gen.xor(rsm_sommelier_alco_handling_sequence, None)
# If this XOR resolves to rsm_sommelier_alco_handling_sequence, then act_sommelier_prepares_alco has completed.

# 2. Waiter's Non-Alcoholic Beverage Preparation (Optional)
waiter_optional_non_alco_prep_XOR = gen.xor(waiter_I_ACT_prepare_non_alco_bev, None)

# 3. Waiter's Initial Preparation Block (Concurrent Tasks)
waiter_initial_prep_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_optional_non_alco_prep_XOR,) # This XOR node is part of the concurrent tasks
])

# 4. Waiter's Alcoholic Beverage Collection (Optional)
# This XOR node represents whether the waiter collects alcohol or not.
# The actual activity act_waiter_collects_alco will have its preconditions defined in the main PO.
optional_waiter_collects_alco_XOR = gen.xor(act_waiter_collects_alco, None)

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # RSM takes order, then concurrently sends food and initiates optional alcohol handling by RSM/Sommelier.
    (rsm_A_take_order, rsm_B_send_food_order_to_kitchen),
    (rsm_A_take_order, optional_rsm_sommelier_alco_handling_XOR), # RSM decides if alco order process starts

    # Kitchen prepares food after receiving order.
    (rsm_B_send_food_order_to_kitchen, kitchen_E_prepare_food),

    # RSM assigns order to waiter after food order sent AND alcohol handling choice (by RSM/Sommelier) is resolved.
    (rsm_B_send_food_order_to_kitchen, rsm_D_assign_order_to_waiter),
    (optional_rsm_sommelier_alco_handling_XOR, rsm_D_assign_order_to_waiter),

    # Waiter performs initial preparations after assignment.
    (rsm_D_assign_order_to_waiter, waiter_initial_prep_block),

    # Waiter collects food after kitchen prep AND own initial prep.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_prep_block, waiter_J_collect_food_from_kitchen),

    # Dependencies for the ACTUAL activity of waiter collecting alcohol (act_waiter_collects_alco).
    # This activity is a child of optional_waiter_collects_alco_XOR.
    # It can only occur if act_sommelier_prepares_alco (part of rsm_sommelier_alco_handling_sequence) completed
    # AND waiter_initial_prep_block completed.
    (act_sommelier_prepares_alco, act_waiter_collects_alco),
    (waiter_initial_prep_block, act_waiter_collects_alco),

    # Waiter delivers order after collecting food AND the choice to collect alcohol (optional_waiter_collects_alco_XOR) is resolved.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (optional_waiter_collects_alco_XOR, waiter_L_deliver_order_to_guest),

    # Waiter debits account after delivery.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
