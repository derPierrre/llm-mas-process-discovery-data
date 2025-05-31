gen = ModelGenerator()

# Activities
A0_GuestPlacesOrder = gen.activity("Guest: Places order") # Added to explicitly start the process
A1_RsmReceivesOrder = gen.activity("RSM: Receives guest order")

# RSM's dispatch/assignment activities that initiate parallel preparations
A2_RsmSendFoodToKitchen = gen.activity("RSM: Sends food items to Kitchen")
A3_RsmFwdAlcoToSommelier = gen.activity("RSM: Forwards alcoholic beverage order to Sommelier")
A4_RsmAssignWaiter = gen.activity("RSM: Assigns Waiter to order")

# Preparation activities by respective staff
A5_KitchenPreparesFood = gen.activity("Kitchen: Prepares food items")
A6_SommelierPreparesAlco = gen.activity("Sommelier: Prepares alcoholic beverages")
A7_WaiterPreparesCart = gen.activity("Waiter: Prepares service cart and non-alcoholic beverages")

# Waiter's subsequent actions
A8_WaiterCollectsItems = gen.activity("Waiter: Collects all prepared items")
A9_WaiterDeliversOrder = gen.activity("Waiter: Delivers complete order to guest's room")
A10_WaiterDebitsAccount = gen.activity("Waiter: Debits guest's account")

# Guest's optional action
A11_GuestGivesTip = gen.activity("Guest: Gives tip to Waiter (Optional)")

# Define the parallel preparation branches
# Branch 1: Food dispatch by RSM and Preparation by Kitchen
food_preparation_branch = gen.partial_order(dependencies=[(A2_RsmSendFoodToKitchen, A5_KitchenPreparesFood)])

# Branch 2: Alcoholic Beverage dispatch by RSM and Preparation by Sommelier (Conditional)
# This sequence (dispatch + prep) is conditional
sommelier_preparation_sequence = gen.partial_order(dependencies=[(A3_RsmFwdAlcoToSommelier, A6_SommelierPreparesAlco)])
conditional_sommelier_branch = gen.xor(sommelier_preparation_sequence, None) # This branch is optional

# Branch 3: Waiter Assignment by RSM and Cart/Non-Alco Bev Preparation by Waiter
waiter_cart_preparation_branch = gen.partial_order(dependencies=[(A4_RsmAssignWaiter, A7_WaiterPreparesCart)])

# Phase of concurrent RSM dispatch actions leading to parallel preparations.
# The RSM's actions A2, A3, A4 are themselves concurrent after A1.
rsm_dispatch_concurrent_actions = gen.partial_order(dependencies=[
    (food_preparation_branch,),
    (conditional_sommelier_branch,),
    (waiter_cart_preparation_branch,)
])

# Optional Tipping by Guest
optional_tipping = gen.xor(A11_GuestGivesTip, None)

# Define the overall process flow as a sequence of major stages
final_model = gen.partial_order(dependencies=[
    (A0_GuestPlacesOrder, A1_RsmReceivesOrder),
    (A1_RsmReceivesOrder, rsm_dispatch_concurrent_actions), 
    (rsm_dispatch_concurrent_actions, A8_WaiterCollectsItems), # Collection happens after all preparations are complete
    (A8_WaiterCollectsItems, A9_WaiterDeliversOrder),
    (A9_WaiterDeliversOrder, A10_WaiterDebitsAccount),
    (A10_WaiterDebitsAccount, optional_tipping)
])
