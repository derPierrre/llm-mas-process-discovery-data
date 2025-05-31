"""
POWL Model for The Evanstonian Room Service Process
"""
gen = ModelGenerator()

# --- Define all individual activities ---
# Room Service Manager (RSM) Activities
act_take_order = gen.activity("Take guest's order, including special requests")
act_rsm_submit_food_kitchen = gen.activity("RSM submits food portion of order to Kitchen")
act_rsm_submit_alc_sommelier = gen.activity("RSM submits alcoholic beverage portion of order to Sommelier")
act_rsm_assign_waiter = gen.activity("RSM assigns available Waiter to handle delivery")

# Kitchen Activities
act_kitchen_receive_food = gen.activity("Kitchen receives food order details from RSM")
act_kitchen_review_food = gen.activity("Kitchen reviews order ticket")
act_kitchen_prepare_food = gen.activity("Kitchen gathers ingredients and prepares meal")
act_kitchen_quality_check = gen.activity("Kitchen ensures meal is presentable and meets quality standards")
act_kitchen_notify_waiter = gen.activity("Kitchen notifies assigned Waiter that food is ready for pickup")

# Sommelier Activities
act_sommelier_receive_alc = gen.activity("Sommelier receives alcoholic beverage order details from RSM")
act_sommelier_review_alc = gen.activity("Sommelier reviews alcoholic beverage order")
act_sommelier_prepare_alc = gen.activity("Sommelier selects wine or prepares other ordered alcoholic beverages")
act_sommelier_present_alc = gen.activity("Sommelier ensures beverages are properly presented and ready for service")
act_sommelier_notify_waiter = gen.activity("Sommelier notifies assigned Waiter that alcoholic beverages are ready for pickup")

# Waiter Activities
act_waiter_receive_assignment = gen.activity("Waiter receives order assignment from RSM")
act_waiter_prep_cart_tablecloth_silverware = gen.activity("Waiter prepares service cart with tablecloth and appropriate silverware")
act_waiter_prep_non_alc_beverages = gen.activity("Waiter prepares non-alcoholic beverages and places them on cart")
act_waiter_collect_food = gen.activity("Waiter collects prepared food from Kitchen")
act_waiter_collect_alc = gen.activity("Waiter collects prepared alcoholic beverages from Sommelier")
act_waiter_load_cart = gen.activity("Waiter loads all items carefully onto service cart")
act_waiter_deliver_order = gen.activity("Waiter delivers complete order to guest's room")
act_waiter_return_debit_account = gen.activity("Waiter returns to room service station and debits guest's account")

# --- Define sub-processes (sequences of activities as partial orders) ---
kitchen_process_activities = [
    (act_kitchen_receive_food, act_kitchen_review_food),
    (act_kitchen_review_food, act_kitchen_prepare_food),
    (act_kitchen_prepare_food, act_kitchen_quality_check),
    (act_kitchen_quality_check, act_kitchen_notify_waiter)
]
kitchen_process_po = gen.partial_order(dependencies=kitchen_process_activities)

sommelier_process_activities = [
    (act_sommelier_receive_alc, act_sommelier_review_alc),
    (act_sommelier_review_alc, act_sommelier_prepare_alc),
    (act_sommelier_prepare_alc, act_sommelier_present_alc),
    (act_sommelier_present_alc, act_sommelier_notify_waiter)
]
sommelier_process_po = gen.partial_order(dependencies=sommelier_process_activities)

waiter_initial_prep_activities = [
    (act_waiter_receive_assignment, act_waiter_prep_cart_tablecloth_silverware),
    (act_waiter_prep_cart_tablecloth_silverware, act_waiter_prep_non_alc_beverages)
]
waiter_initial_prep_po = gen.partial_order(dependencies=waiter_initial_prep_activities)

waiter_post_collection_activities = [
    (act_waiter_load_cart, act_waiter_deliver_order),
    (act_waiter_deliver_order, act_waiter_return_debit_account)
]
waiter_post_collection_po = gen.partial_order(dependencies=waiter_post_collection_activities)

# --- Path 1: Order does NOT include alcoholic beverages ---
# Create copies for this path to ensure distinct instances
act_take_order_p1 = act_take_order.copy()
act_rsm_submit_food_kitchen_p1 = act_rsm_submit_food_kitchen.copy()
act_rsm_assign_waiter_p1 = act_rsm_assign_waiter.copy()
kitchen_process_po_p1 = kitchen_process_po.copy()
waiter_initial_prep_po_p1 = waiter_initial_prep_po.copy()
act_waiter_collect_food_p1 = act_waiter_collect_food.copy()
waiter_post_collection_po_p1 = waiter_post_collection_po.copy()

process_no_alc_dependencies = [
    # RSM sequence
    (act_take_order_p1, act_rsm_submit_food_kitchen_p1),
    (act_rsm_submit_food_kitchen_p1, act_rsm_assign_waiter_p1),
    # RSM triggers other processes
    (act_rsm_submit_food_kitchen_p1, kitchen_process_po_p1), # Food submission triggers Kitchen process
    (act_rsm_assign_waiter_p1, waiter_initial_prep_po_p1),   # Waiter assignment triggers Waiter initial prep
    # Waiter collects food (after kitchen ready and own prep done)
    (kitchen_process_po_p1, act_waiter_collect_food_p1), # Kitchen must notify (end of kitchen_process_po_p1)
    (waiter_initial_prep_po_p1, act_waiter_collect_food_p1),
    # Waiter final steps
    (act_waiter_collect_food_p1, waiter_post_collection_po_p1)
]
process_no_alc = gen.partial_order(dependencies=process_no_alc_dependencies)

# --- Path 2: Order DOES include alcoholic beverages ---
# Create copies for this path
act_take_order_p2 = act_take_order.copy()
act_rsm_submit_food_kitchen_p2 = act_rsm_submit_food_kitchen.copy()
act_rsm_submit_alc_sommelier_p2 = act_rsm_submit_alc_sommelier.copy() # Specific to this path
sommelier_process_po_p2 = sommelier_process_po.copy() # Specific to this path
act_rsm_assign_waiter_p2 = act_rsm_assign_waiter.copy()
kitchen_process_po_p2 = kitchen_process_po.copy()
waiter_initial_prep_po_p2 = waiter_initial_prep_po.copy()
act_waiter_collect_food_p2 = act_waiter_collect_food.copy()
act_waiter_collect_alc_p2 = act_waiter_collect_alc.copy() # Specific to this path
waiter_post_collection_po_p2 = waiter_post_collection_po.copy()

process_with_alc_dependencies = [
    # RSM sequence
    (act_take_order_p2, act_rsm_submit_food_kitchen_p2),
    (act_rsm_submit_food_kitchen_p2, act_rsm_submit_alc_sommelier_p2),
    (act_rsm_submit_alc_sommelier_p2, act_rsm_assign_waiter_p2),
    # RSM triggers other processes
    (act_rsm_submit_food_kitchen_p2, kitchen_process_po_p2),    # Food submission triggers Kitchen process
    (act_rsm_submit_alc_sommelier_p2, sommelier_process_po_p2), # Alcoholic bev submission triggers Sommelier process
    (act_rsm_assign_waiter_p2, waiter_initial_prep_po_p2),      # Waiter assignment triggers Waiter initial prep
    # Waiter collects food (after kitchen ready and own prep done)
    (kitchen_process_po_p2, act_waiter_collect_food_p2),
    (waiter_initial_prep_po_p2, act_waiter_collect_food_p2),
    # Waiter collects alcoholic beverages (after sommelier ready and own prep done)
    (sommelier_process_po_p2, act_waiter_collect_alc_p2),
    (waiter_initial_prep_po_p2, act_waiter_collect_alc_p2),
    # Waiter final steps (loading cart depends on collecting both food and alcohol)
    (act_waiter_collect_food_p2, waiter_post_collection_po_p2),
    (act_waiter_collect_alc_p2, waiter_post_collection_po_p2)
]
process_with_alc = gen.partial_order(dependencies=process_with_alc_dependencies)

# --- Final model: Exclusive choice based on alcoholic beverages ---
final_model = gen.xor(process_no_alc, process_with_alc)
