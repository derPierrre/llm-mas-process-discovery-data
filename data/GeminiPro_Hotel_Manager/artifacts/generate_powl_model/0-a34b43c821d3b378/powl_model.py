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

# Stream 1: Food Preparation (RSM dispatches, Kitchen prepares)
branch_food = gen.partial_order(dependencies=[(A1_RsmSendFood, A4_KitchenPrepFood)])

# Stream 2: Waiter Cart Preparation (RSM assigns, Waiter prepares)
branch_waiter_prep = gen.partial_order(dependencies=[(A3_RsmAssignWaiter, A6_WaiterPrepCart)])

# Stream 3: Sommelier Actions (Conditional: RSM forwards, Sommelier prepares)
# This entire branch is conditional on alcoholic beverages being ordered.
sommelier_actions_sequence = gen.partial_order(dependencies=[(A2_RsmFwdAlco, A5_SommelierPrepAlco)])
branch_sommelier_conditional = gen.xor(sommelier_actions_sequence, None)

# Phase of concurrent preparation activities. These branches are initiated after the order is received and dispatched by RSM.
# The RSM's dispatch actions (A1, A2-conditional, A3) are the starting points of these branches.
concurrent_prep_phase = gen.partial_order(dependencies=[
    (branch_food,),
    (branch_waiter_prep,),
    (branch_sommelier_conditional,)
])

# Optional Tipping
optional_tip = gen.xor(A10_GuestTip, None)

# Define the overall process flow as a sequence of phases
# 1. Order Reception
# 2. Concurrent Dispatch & Preparation Phase
# 3. Collection by Waiter
# 4. Delivery by Waiter
# 5. Payment by Waiter
# 6. Optional Tip by Guest

final_model = gen.partial_order(dependencies=[
    (A0_RsmRcvOrder, concurrent_prep_phase),  # Order reception leads to the concurrent preparation phase
    (concurrent_prep_phase, A7_WaiterCollectItems), # Collection happens after all preparations are complete
    (A7_WaiterCollectItems, A8_WaiterDeliverOrder),
    (A8_WaiterDeliverOrder, A9_WaiterDebitAccount),
    (A9_WaiterDebitAccount, optional_tip)
])
