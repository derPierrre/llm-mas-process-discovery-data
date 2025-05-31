gen = ModelGenerator()

# Step 1: The guest calls room service to place an order for food and/or drinks.
place_order = gen.activity('Place order')

# Step 2: Room service takes the order and coordinates with the kitchen for food and the sommelier for drinks.
coordinate_kitchen = gen.activity('Coordinate with kitchen')
coordinate_sommelier = gen.activity('Coordinate with sommelier')

# Step 3: The kitchen prepares the food, and the sommelier prepares the drinks.
prepare_food = gen.activity('Prepare food')
prepare_drinks = gen.activity('Prepare drinks')

# Step 4: Room service coordinates the delivery with the waiter.
coordinate_delivery = gen.activity('Coordinate delivery')

# Step 5: The waiter delivers the food and drinks to the guest's room.
deliver_items = gen.activity('Deliver items')

# Step 6: The guest decides whether to tip the waiter.
tip_waiter = gen.activity('Tip waiter')
skip_tip = gen.activity('Skip tip')
choice_tip = gen.xor(tip_waiter, skip_tip)

# Step 7: The waiter returns with the bill for the guest to sign.
bring_bill = gen.activity('Bring bill')

# Step 8: The guest signs the bill, and the process ends.
sign_bill = gen.activity('Sign bill')

# Combine all steps into a partial order.
final_model = gen.partial_order(
    dependencies=[
        (place_order, coordinate_kitchen),
        (place_order, coordinate_sommelier),
        (coordinate_kitchen, prepare_food),
        (coordinate_sommelier, prepare_drinks),
        (prepare_food, coordinate_delivery),
        (prepare_drinks, coordinate_delivery),
        (coordinate_delivery, deliver_items),
        (deliver_items, choice_tip),
        (choice_tip, bring_bill),
        (bring_bill, sign_bill)
    ]
)