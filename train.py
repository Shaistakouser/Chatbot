from flask import Flask, render_template, request, jsonify, session
import re

app = Flask(__name__)
app.secret_key = "happy_memories_secret_key"

# Complete Knowledge Base for Happy Memories
CAFE_MENU = {
    "starters": [
        "Avocado Toast Tartine (V)", "Crispy Truffle Fries (V)", "Loaded Street Corn Dip (V)",
        "Crispy Calamari", "Spicy Garlic Edamame (VG, GF)", "Baked Spinach & Artichoke Dip (V)"
    ],
    "mains": [
        "The Rustic Café Burger", "Pesto Chicken Panini", "Harvest Grain Bowl (VG, GF)",
        "Caprese Flatbread (V)", "Smoked Salmon Bagel Board", "Wild Mushroom & Herb Risotto (V, GF)", "Crispy Fish Tacos"
    ],
    "drinks": [
        "Iced Honey Lavender Latte", "Matcha Mint Lemonade", "Berry Hibiscus Cooler",
        "Classic Cold Brew", "Golden Turmeric Chai", "Spiced Apple Cider Float", "Cucumber Basil Sparkler (VG)"
    ],
    "desserts": [
        "Warm Chocolate Lava Cake", "Classic New York Cheesecake", "Salted Caramel Blondie",
        "Lemon Raspberry Tiramisu", "Matcha Green Tea Crepe Cake", "Warm Berry Crisp"
    ],
    "dietary": (
        "🌿 *Dietary Guide*:\n"
        "• **(V) Vegetarian:** Avocado Toast, Truffle Fries, Street Corn Dip, Spinach & Artichoke Dip, Caprese Flatbread, Mushroom Risotto\n"
        "• **(VG) Vegan:** Spicy Garlic Edamame, Harvest Grain Bowl, Cucumber Basil Sparkler\n"
        "• **(GF) Gluten-Free:** Edamame, Harvest Grain Bowl, Mushroom Risotto"
    ),
    "info": (
        "ℹ️ *Cafe Info*:\n"
        "🕒 Hours: Mon–Sat: 7:30 AM – 6:00 PM\n"
        "📶 Wi-Fi Password: LatteLove2026\n"
        "📍 Policy: Walk-in only!"
    )
}

@app.route("/")
def home():
    if "cart" not in session:
        session["cart"] = []
    if "pending_item" not in session:
        session["pending_item"] = None
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip().lower()
    
    if "cart" not in session:
        session["cart"] = []
    if "pending_item" not in session:
        session["pending_item"] = None

    reply = ""
    all_items = CAFE_MENU["starters"] + CAFE_MENU["mains"] + CAFE_MENU["drinks"] + CAFE_MENU["desserts"]

    # 1. VIEW CART COMMAND
    if user_msg in ["cart", "view cart", "my order"]:
        cart = session["cart"]
        if not cart:
            reply = "🛒 Your cart is currently empty! Type an item name to add something."
        else:
            items_list = "\n".join([f"• {item['qty']}x {item['name']}" for item in cart])
            reply = f"🛒 **Your Current Order:**\n{items_list}\n\nType *'checkout'* to place your order!"

    # 2. CLEAR CART COMMAND
    elif user_msg in ["clear cart", "empty cart", "reset"]:
        session["cart"] = []
        session["pending_item"] = None
        session.modified = True
        reply = "🗑️ Your cart has been cleared!"

    # 3. CHECKOUT COMMAND
    elif user_msg in ["checkout", "place order", "done"]:
        cart = session["cart"]
        if not cart:
            reply = "Your cart is empty! Add some items before checking out. 🥐"
        else:
            items_list = "\n".join([f"• {item['qty']}x {item['name']}" for item in cart])
            reply = f"🎉 **Order Placed Successfully!**\n\n{items_list}\n\nYour order has been sent to the counter. Please pay and pick up when your name is called at Happy Memories! ☕💛"
            session["cart"] = []
            session["pending_item"] = None
            session.modified = True

    # 4. IF WE ARE WAITING FOR A QUANTITY NUMBER
    elif session["pending_item"]:
        # Try to extract a number from the user's message
        numbers = re.findall(r'\d+', user_msg)
        if numbers:
            qty = int(numbers[0])
            item = session["pending_item"]
            
            # Add to cart
            session["cart"].append({"name": item, "qty": qty})
            session["pending_item"] = None
            session.modified = True
            
            reply = f"✅ Added **{qty}x {item}** to your order!\n\nType *'cart'* to view items or *'checkout'* when ready."
        else:
            reply = f"Please enter a valid number for how many **{session['pending_item']}** you'd like (e.g., '2'):"

    # 5. CHECK IF USER TYPED AN ITEM NAME (with or without quantity)
    else:
        matched_item = None
        for item in all_items:
            clean_name = item.lower().split('(')[0].strip()
            if clean_name in user_msg or user_msg in clean_name:
                matched_item = item
                break

        if matched_item:
            # Check if user included a quantity in the same message (e.g., "2 fish tacos")
            numbers = re.findall(r'\d+', user_msg)
            if numbers:
                qty = int(numbers[0])
                session["cart"].append({"name": matched_item, "qty": qty})
                session.modified = True
                reply = f"✅ Added **{qty}x {matched_item}** to your order!\n\nType *'cart'* to view your items or *'checkout'* when ready."
            else:
                # No quantity provided yet, set as pending and ask!
                session["pending_item"] = matched_item
                session.modified = True
                reply = f"How many **{matched_item}** would you like? (Please type a number)"
        
        # 6. BROWSE CATEGORIES & INFO
        elif any(word in user_msg for word in ["starter", "small bite", "appetizer"]):
            reply = "🌟 *Starters & Small Bites*:\n" + "\n".join([f"• {i}" for i in CAFE_MENU["starters"]]) + "\n\n*(Type any item name to order it!)*"
        elif any(word in user_msg for word in ["main", "comfort", "burger", "panini", "bowl", "flatbread", "risotto", "tacos", "bagel", "food"]):
            reply = "🥪 *Mains & All-Day Comforts*:\n" + "\n".join([f"• {i}" for i in CAFE_MENU["mains"]]) + "\n\n*(Type any item name to order it!)*"
        elif any(word in user_msg for word in ["drink", "coffee", "latte", "chai", "cooler", "lemonade", "beverage"]):
            reply = "🥤 *Refreshments & Drinks*:\n" + "\n".join([f"• {i}" for i in CAFE_MENU["drinks"]]) + "\n\n*(Type any item name to order it!)*"
        elif any(word in user_msg for word in ["dessert", "sweet", "cake", "cheesecake", "tiramisu", "blondie", "crisp"]):
            reply = "🍰 *Desserts*:\n" + "\n".join([f"• {i}" for i in CAFE_MENU["desserts"]]) + "\n\n*(Type any item name to order it!)*"
        elif any(word in user_msg for word in ["diet", "vegan", "vegetarian", "gluten", "gf", "vg"]):
            reply = CAFE_MENU["dietary"]
        elif any(word in user_msg for word in ["wifi", "password", "hour", "time", "location", "info"]):
            reply = CAFE_MENU["info"]
        else:
            reply = (
                "Welcome to **Happy Memories**! ☕✨ Type any item name (like *'crispy fish tacos'*) to start your order, or type *'cart'* to view your items!"
            )
        
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000, debug=True)