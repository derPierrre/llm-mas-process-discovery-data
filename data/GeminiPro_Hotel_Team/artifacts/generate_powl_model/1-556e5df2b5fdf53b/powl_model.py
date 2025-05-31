gen = ModelGenerator()

# Step 1: Guest Feels Hungry and Reviews Menu
guest_reviews_menu = gen.activity("Guest feels hungry and reviews menu")

# Step 2: Guest Places Order
guest_places_order = gen.activity("Guest places order to Room Service Manager")

# Step 3: Order Taking and Coordination (Room Service Manager)
rsm_takes_order = gen.activity("RSM takes guest's order")
rsm_coords_kitchen = gen.activity("RSM coordinates with Kitchen Staff (drops off order ticket)")

# Conditional Sommelier Coordination by RSM
rsm_coords_sommelier_action = gen.activity("RSM coordinates with Sommelier (if alcoholic beverages ordered)")
rsm_optional_coord_sommelier = gen.xor(rsm_coords_sommelier_action, None)

rsm_assigns_waiter = gen.activity("RSM assigns order to a Room Service Waiter")

# Sequence of RSM activities
rsm_activities_po = gen.partial_order(dependencies=[
    (rsm_takes_order, rsm_coords_kitchen),
    (rsm_coords_kitchen, rsm_optional_coord_sommelier),
    (rsm_optional_coord_sommelier, rsm_assigns_waiter)
])

# Step 4 (Parallel Preparations) & Step 5 (Order Collection)
# Preparation Activities
kitchen_prep_food = gen.activity("Kitchen Staff prepares food items and places on pick-up counter")

sommelier_prep_alc_action = gen.activity("Sommelier selects wine or prepares alcoholic drinks")
optional_sommelier_prep = gen.xor(sommelier_prep_alc_action, None) # If applicable

waiter_prep_cart_non_alc = gen.activity("Waiter prepares service cart and any non-alcoholic drinks")

# Collection Activities by Waiter
waiter_collects_food = gen.activity("Waiter picks up prepared food from kitchen's pick-up counter")

waiter_collects_alc_action = gen.activity("Waiter collects alcoholic beverages from Sommelier")
optional_waiter_collect_alc = gen.xor(waiter_collects_alc_action, None) # If applicable

# Combined Partial Order for Preparations and Collections (Updated)
# The waiter can collect food and alcoholic beverages (if applicable) in any order or in parallel,
# once the cart is prepared and the respective items are ready.
prep_and_collection_po = gen.partial_order(dependencies=[
    (kitchen_prep_food, waiter_collects_food),                # Food must be prepared before collection
    (optional_sommelier_prep, optional_waiter_collect_alc),  # Alcoholic drinks must be prepared (if applicable) before collection (if applicable)
    (waiter_prep_cart_non_alc, waiter_collects_food),         # Cart must be prepared before food collection
    (waiter_prep_cart_non_alc, optional_waiter_collect_alc) # Cart must be prepared before alcoholic beverage collection (if applicable)
    # No direct order between waiter_collects_food and optional_waiter_collect_alc
])

# Step 6: Delivery to Guest
waiter_delivers_order = gen.activity("Waiter delivers the complete order to the guest's room")

# Step 7: Guest Consumes Meal
guest_consumes_meal = gen.activity("Guest enjoys meal and decides whether to leave a tip")

# Step 8: Billing
waiter_debits_account = gen.activity("Waiter debits guest's account for the order")

# Overall Process Sequence
final_model = gen.partial_order(dependencies=[
    (guest_reviews_menu, guest_places_order),
    (guest_places_order, rsm_activities_po),
    (rsm_activities_po, prep_and_collection_po),
    (prep_and_collection_po, waiter_delivers_order),
    (waiter_delivers_order, guest_consumes_meal),
    (guest_consumes_meal, waiter_debits_account)
])