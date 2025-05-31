gen = ModelGenerator()

# Activities
A0_RsmRcvOrder = gen.activity("RSM: Receives guest order")

# RSM's dispatch/assignment activities that initiate parallel preparations
A1_RsmSendFood = gen.activity("RSM: Sends food items to Kitchen")
A2_RsmFwdAlco = gen.activity("RSM: Forwards alcoholic beverage order to Sommelier")
A3_RsmAssignWaiter = gen.activity("RSM: Assigns Waiter to order")

# Preparation activities by respective staff
A4_KitchenPrepFood = gen.activity("Kitchen: Prepares food items")
A5_SommelierPrepAlco = gen.activity("Sommelier: Prepares alcoholic beverages")
A6_WaiterPrepCart = gen.activity("Waiter: Prepares service cart and non-alcoholic beverages")

# Waiter's subsequent actions
A7_WaiterCollectItems = gen.activity("Waiter: Collects all prepared items")
A8_WaiterDeliverOrder = gen.activity("Waiter: Delivers complete order to guest's room")
A9_WaiterDebitAccount = gen.activity("Waiter: Debits guest's account")

# Guest's optional action
A10_GuestTip = gen.activity("Guest: Gives tip to Waiter (Optional)")

# Define the parallel preparation branches
# Branch 1: Food dispatch by RSM and Preparation by Kitchen
food_preparation_branch = gen.partial_order(dependencies=[(A1_RsmSendFood, A4_KitchenPrepFood)])

# Branch 2: Alcoholic Beverage dispatch by RSM and Preparation by Sommelier (Conditional)
# This sequence (dispatch + prep) is conditional
sommelier_preparation_sequence = gen.partial_order(dependencies=[(A2_RsmFwdAlco, A5_SommelierPrepAlco)])
conditional_sommelier_branch = gen.xor(sommelier_preparation_sequence, None) # This branch is optional

# Branch 3: Waiter Assignment by RSM and Cart/Non-Alco Bev Preparation by Waiter
waiter_cart_preparation_branch = gen.partial_order(dependencies=[(A3_RsmAssignWaiter, A6_WaiterPrepCart)])

# Phase of concurrent preparation activities.
# These branches are initiated by the RSM (as their first step) and proceed in parallel.
concurrent_preparation_phase = gen.partial_order(dependencies=[
    (food_preparation_branch,),
    (conditional_sommelier_branch,),
    (waiter_cart_preparation_branch,)
])

# Optional Tipping by Guest
optional_tipping = gen.xor(A10_GuestTip, None)

# Define the overall process flow as a sequence of major stages
final_model = gen.partial_order(dependencies=[
    (A0_RsmRcvOrder, concurrent_preparation_phase),  # Order reception leads to the concurrent dispatch and preparation phase
    (concurrent_preparation_phase, A7_WaiterCollectItems), # Collection happens after all preparations are complete
    (A7_WaiterCollectItems, A8_WaiterDeliverOrder),
    (A8_WaiterDeliverOrder, A9_WaiterDebitAccount),
    (A9_WaiterDebitAccount, optional_tipping)
])
