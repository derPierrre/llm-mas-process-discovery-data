
"""
This POWL model describes the room service process at The Evanstonian.

Process Breakdown:
1.  RSM Takes Order: The process starts when the Room Service Manager (RSM) takes a guest's order.
2.  RSM Concurrent Dispatch Initiation: After taking the order, the RSM initiates two main lines of action concurrently:
    a.  Food Order Processing: RSM sends the food order to the Kitchen, and the Kitchen Staff prepare the food.
    b.  Alcoholic Beverage Processing (Optional): This is an optional path. If alcoholic beverages are ordered:
        i.  RSM sends the order to the Sommelier.
        ii. Sommelier prepares the beverages.
        This entire sequence (RSM sends -> Sommelier prepares) is a single optional sub-process.
3.  RSM Assigns Order to Waiter: This happens after the RSM has sent the food order AND the optional alcoholic beverage processing path has either completed (if taken) or been skipped (i.e., the choice is resolved).
4.  Waiter's Initial Preparations: Upon assignment, the waiter performs several tasks concurrently:
    a.  Prepares service cart.
    b.  Gathers silverware.
    c.  Optionally prepares non-alcoholic beverages (this is a choice for the waiter).
    This block of tasks must complete before the waiter can collect items.
5.  Waiter Collects Items:
    a.  Collects Food: Depends on BOTH the Kitchen having prepared the food AND the waiter having completed their initial preparations.
    b.  Optionally Collects Alcoholic Beverages: This is a choice for the waiter. The actual act of collecting alcoholic beverages can ONLY occur IF the Sommelier has prepared them (i.e., the optional alcoholic beverage processing path was taken and completed) AND the waiter has completed their initial preparations.
6.  Waiter Delivers Order: Depends on the waiter having collected the food AND the choice/action of collecting alcoholic beverages being resolved (either collected, skipped, or not applicable).
7.  Waiter Debits Account: Occurs after successful delivery.
"""
gen = ModelGenerator()

# --- Define Individual Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order_to_kitchen = gen.activity("RSM: Send food order to Kitchen")
rsm_C_ACT_send_alco_order_to_sommelier = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 2: Sommelier
sommelier_F_ACT_prepare_alco_bev = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
waiter_I_ACT_prepare_non_alco_bev = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
waiter_K_ACT_collect_alco_bev_from_sommelier = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Sub-Processes and Optional Choices (XORs) --- 

# 1. Alcoholic Beverage Handling Sub-Process (Optional)
# This entire path (RSM sends -> Sommelier prepares) is optional.
alco_handling_path = gen.partial_order(dependencies=[
    (rsm_C_ACT_send_alco_order_to_sommelier, sommelier_F_ACT_prepare_alco_bev)
])
optional_alco_handling_XOR = gen.xor(alco_handling_path, None)

# 2. Waiter's Non-Alcoholic Beverage Preparation (Optional)
waiter_optional_non_alco_prep_XOR = gen.xor(waiter_I_ACT_prepare_non_alco_bev, None)

# 3. Waiter's Initial Preparation Block (Concurrent Tasks)
waiter_initial_prep_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_optional_non_alco_prep_XOR,)
])

# 4. Waiter's Alcoholic Beverage Collection Sub-Process (Optional AND Conditional)
# This path (Waiter collects) is optional for the waiter.
# Crucially, the activity waiter_K_ACT_collect_alco_bev_from_sommelier itself
# will have dependencies on alco_handling_path (among others) defined in the main PO.
# This ensures it only happens if alcohol was prepared.
waiter_optional_alco_collect_XOR = gen.xor(waiter_K_ACT_collect_alco_bev_from_sommelier, None)

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # RSM takes order, then concurrently sends food and initiates optional alcohol handling.
    (rsm_A_take_order, rsm_B_send_food_order_to_kitchen),
    (rsm_A_take_order, optional_alco_handling_XOR),

    # Kitchen prepares food after receiving order.
    (rsm_B_send_food_order_to_kitchen, kitchen_E_prepare_food),

    # RSM assigns order to waiter after food order sent AND alcohol handling choice is resolved.
    (rsm_B_send_food_order_to_kitchen, rsm_D_assign_order_to_waiter),
    (optional_alco_handling_XOR, rsm_D_assign_order_to_waiter),

    # Waiter performs initial preparations after assignment.
    (rsm_D_assign_order_to_waiter, waiter_initial_prep_block),

    # Waiter collects food after kitchen prep AND own initial prep.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_prep_block, waiter_J_collect_food_from_kitchen),

    # Dependencies for the ACTUAL activity of waiter collecting alcohol (waiter_K_ACT_collect_alco_bev_from_sommelier).
    # This activity is a child of waiter_optional_alco_collect_XOR.
    # It can only occur if alco_handling_path (Sommelier prep) completed AND waiter did initial prep.
    # If alco_handling_path was skipped (via its XOR), it never completes, so K_ACT cannot start.
    (alco_handling_path, waiter_K_ACT_collect_alco_bev_from_sommelier),
    (waiter_initial_prep_block, waiter_K_ACT_collect_alco_bev_from_sommelier),

    # Waiter delivers order after collecting food AND the choice to collect alcohol is resolved.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (waiter_optional_alco_collect_XOR, waiter_L_deliver_order_to_guest),

    # Waiter debits account after delivery.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
