
"""
This POWL model describes the room service process at The Evanstonian.

Process Breakdown:
1.  RSM Takes Order: The process starts when the Room Service Manager (RSM) takes a guest's order.
2.  Concurrent RSM Actions & Kitchen Prep:
    a.  RSM sends food order to Kitchen. Kitchen Staff then prepare food.
    b.  RSM initiates optional alcoholic beverage handling (AlcoHandlingXOR). This involves:
        i.  A sequence: RSM sends alcoholic beverage order to Sommelier, then Sommelier prepares alcoholic beverages (rsm_sommelier_alco_sequence).
        ii. This sequence is optional (AlcoHandlingXOR = xor(rsm_sommelier_alco_sequence, None)).
3.  RSM Assigns Order to Waiter: This occurs after RSM has sent the food order AND the AlcoHandlingXOR is resolved (i.e., alco sequence completed or skipped).
4.  Waiter Initial Preparations: Upon assignment, the Waiter concurrently:
    a.  Prepares service cart.
    b.  Gathers silverware.
    c.  Optionally prepares non-alcoholic beverages (waiter_opt_non_alco_XOR).
    This block is `waiter_initial_prep_block`.
5.  Waiter Collects Food: Depends on Kitchen having prepared food AND Waiter having completed `waiter_initial_prep_block`.
6.  Waiter Optionally Collects Alcoholic Beverages (waiter_opt_alco_collect_XOR):
    This choice (to collect actual alco or skip) is presented to the waiter.
    It can only be initiated after the AlcoHandlingXOR is resolved (so the status of sommelier prep is known) AND the waiter has completed `waiter_initial_prep_block`.
    If alcoholic beverages were not prepared (AlcoHandlingXOR resolved to None), the waiter would choose to skip collection within waiter_opt_alco_collect_XOR.
7.  Waiter Delivers Order: Depends on Waiter having collected food AND `waiter_opt_alco_collect_XOR` being resolved (alco collected or skipped).
8.  Waiter Debits Account: Occurs after delivery.
"""
gen = ModelGenerator()

# --- Define Individual Activities --- 

# Process Owner 0: Room Service Manager (RSM)
rsm_A_take_order = gen.activity("RSM: Take guest order and note details")
rsm_B_send_food_order_to_kitchen = gen.activity("RSM: Send food order to Kitchen")
rsm_D_assign_order_to_waiter = gen.activity("RSM: Assign order to Waiter")

# Activities for the RSM/Sommelier alcohol handling path
act_rsm_sends_alco_order = gen.activity("RSM: Send alcoholic beverage order to Sommelier")
act_sommelier_prepares_alco = gen.activity("Sommelier: Prepare alcoholic beverages")

# Process Owner 1: Kitchen Staff
kitchen_E_prepare_food = gen.activity("Kitchen: Prepare food")

# Process Owner 3: Room Service Waiter
waiter_G_prepare_service_cart = gen.activity("Waiter: Prepare service cart (tablecloth)")
waiter_H_gather_silverware = gen.activity("Waiter: Gather silverware")
act_waiter_prepare_non_alco = gen.activity("Waiter: Prepare non-alcoholic beverages")
waiter_J_collect_food_from_kitchen = gen.activity("Waiter: Collect food from Kitchen")
act_waiter_collects_alco = gen.activity("Waiter: Collect alcoholic beverages from Sommelier")
waiter_L_deliver_order_to_guest = gen.activity("Waiter: Deliver order to guest")
waiter_M_debit_guest_account = gen.activity("Waiter: Debit guest account")

# --- Define Optional Choices & Sub-Processes (Sequences/PartialOrders within XORs) --- 

# 1. RSM & Sommelier Alcohol Handling Path (Optional Sequence)
# This sequence (RSM sends -> Sommelier prepares) is encapsulated here.
rsm_sommelier_alco_sequence = gen.partial_order(dependencies=[
    (act_rsm_sends_alco_order, act_sommelier_prepares_alco)
])
# This XOR represents the choice of performing the alcohol handling sequence or skipping it.
AlcoHandlingXOR = gen.xor(rsm_sommelier_alco_sequence, None)

# 2. Waiter's Non-Alcoholic Beverage Preparation (Optional Activity)
waiter_opt_non_alco_XOR = gen.xor(act_waiter_prepare_non_alco, None)

# 3. Waiter's Initial Preparation Block (Concurrent Tasks, including an optional one)
waiter_initial_prep_block = gen.partial_order(dependencies=[
    (waiter_G_prepare_service_cart,),
    (waiter_H_gather_silverware,),
    (waiter_opt_non_alco_XOR,) # The XOR for non-alco prep is part of these concurrent tasks
])

# 4. Waiter's Alcoholic Beverage Collection (Optional Activity)
# This XOR represents the choice for the waiter to collect alcohol or skip.
# The possibility to *actually* collect depends on prior steps, resolved by dependencies on this XOR node.
waiter_opt_alco_collect_XOR = gen.xor(act_waiter_collects_alco, None)

# --- Main Process Flow (Defined as a single Partial Order) --- 
final_model = gen.partial_order(dependencies=[
    # RSM takes order, then concurrently sends food and initiates the (optional) alcohol handling process.
    (rsm_A_take_order, rsm_B_send_food_order_to_kitchen),
    (rsm_A_take_order, AlcoHandlingXOR),

    # Kitchen prepares food after receiving the order.
    (rsm_B_send_food_order_to_kitchen, kitchen_E_prepare_food),

    # RSM assigns order to waiter after food order sent AND the AlcoHandlingXOR is resolved.
    (rsm_B_send_food_order_to_kitchen, rsm_D_assign_order_to_waiter),
    (AlcoHandlingXOR, rsm_D_assign_order_to_waiter),

    # Waiter performs initial preparations after assignment.
    (rsm_D_assign_order_to_waiter, waiter_initial_prep_block),

    # Waiter collects food after kitchen prep AND own initial prep.
    (kitchen_E_prepare_food, waiter_J_collect_food_from_kitchen),
    (waiter_initial_prep_block, waiter_J_collect_food_from_kitchen),

    # The choice for the waiter to collect alcohol (waiter_opt_alco_collect_XOR) is enabled after:
    #   a) The RSM/Sommelier alcohol handling process (AlcoHandlingXOR) is resolved (i.e., alco prepared or confirmed not ordered).
    #   b) The waiter's initial preparations (waiter_initial_prep_block) are complete.
    # If AlcoHandlingXOR resolved to None (no alco prepared), the waiter would choose None in waiter_opt_alco_collect_XOR.
    (AlcoHandlingXOR, waiter_opt_alco_collect_XOR),
    (waiter_initial_prep_block, waiter_opt_alco_collect_XOR),

    # Waiter delivers order after collecting food AND the choice to collect alcohol (waiter_opt_alco_collect_XOR) is resolved.
    (waiter_J_collect_food_from_kitchen, waiter_L_deliver_order_to_guest),
    (waiter_opt_alco_collect_XOR, waiter_L_deliver_order_to_guest),

    # Waiter debits account after delivery.
    (waiter_L_deliver_order_to_guest, waiter_M_debit_guest_account)
])
