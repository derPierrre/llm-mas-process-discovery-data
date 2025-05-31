gen = ModelGenerator()

# Activities
A0_RsmRcvOrder = gen.activity("RSM: Receives guest order")
A1_RsmSendFood = gen.activity("RSM: Sends food items to Kitchen")
A2_RsmFwdAlco = gen.activity("RSM: Forwards alcoholic beverage order to Sommelier")
A3_RsmAssignWaiter = gen.activity("RSM: Assigns Waiter to order")
A4_KitchenPrepFood = gen.activity("Kitchen: Prepares food items")
A5_SommelierPrepAlco = gen.activity("Sommelier: Prepares alcoholic beverages")
A6_WaiterPrepCart = gen.activity("Waiter: Prepares service cart and non-alcoholic beverages")
A7_WaiterCollectItems = gen.activity("Waiter: Collects food, beverages, and service items")
A8_WaiterDeliverOrder = gen.activity("Waiter: Delivers complete order to guest")
A9_WaiterDebitAccount = gen.activity("Waiter: Debits guest's account")
A10_GuestTip = gen.activity("Guest: Gives tip (Optional)")

# Branch 1: Food Dispatch by RSM and Preparation by Kitchen
food_branch = gen.partial_order(dependencies=[(A1_RsmSendFood, A4_KitchenPrepFood)])

# Branch 2: Alcoholic Beverage Dispatch by RSM and Preparation by Sommelier (Conditional)
sommelier_actions_sequence = gen.partial_order(dependencies=[(A2_RsmFwdAlco, A5_SommelierPrepAlco)])
sommelier_conditional_branch = gen.xor(sommelier_actions_sequence, None)

# Branch 3: Waiter Assignment by RSM and Cart/Non-Alco Bev Preparation by Waiter
waiter_prep_branch = gen.partial_order(dependencies=[(A3_RsmAssignWaiter, A6_WaiterPrepCart)])

# Phase of concurrent dispatch by RSM (as initial steps of branches) and subsequent preparations by respective staff.
# These branches are initiated following the RSM receiving the order and can proceed in parallel.
concurrent_prep_phase = gen.partial_order(dependencies=[
    (food_branch,),
    (sommelier_conditional_branch,),
    (waiter_prep_branch,)
])

# Optional Tipping by Guest
optional_tip = gen.xor(A10_GuestTip, None)

# Overall process flow, modeled as a sequence of key stages
final_model = gen.partial_order(dependencies=[
    (A0_RsmRcvOrder, concurrent_prep_phase),  # Order reception leads to the concurrent preparation phase
    (concurrent_prep_phase, A7_WaiterCollectItems), # Collection happens after all preparations are complete
    (A7_WaiterCollectItems, A8_WaiterDeliverOrder),
    (A8_WaiterDeliverOrder, A9_WaiterDebitAccount),
    (A9_WaiterDebitAccount, optional_tip)
])
