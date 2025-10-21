import os
from flask import *
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from ORM.Customer import Customer
from ORM.Pizza import Pizza
from ORM.Product import Product
from ORM.OrderProduct import OrderProduct
from ORM.OrderPizza import OrderPizza
from ORM.Order import Order
from ORM.DiscountCode import DiscountCode
from ORM.UsedDiscountCode import UsedDiscountCode
from ORM.DeliveryPerson import DeliveryPerson
from ORM import db

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your-secret-key"  # Required for sessions
app.config.update(
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_SAMESITE="Lax",  # or "Strict" if you prefer
) # ensures your session cookie is valid for all routes, not just /.


# Bind the shared db to the app
db.init_app(app)
with app.app_context():
    db.create_all()  # create tables if not exist

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def index():
    customer_id = session.get('customer_id')
    customer = Customer.query.get(customer_id) if customer_id else None

    # Fetch all active pizzas with calculated prices from the PizzaMenu view
    result = db.session.execute(db.text("""
        SELECT pizza_id, name, price, is_vegetarian, is_vegan
        FROM PizzaMenu
        WHERE active = 1
    """))
    
    # Convert to list of dictionaries for easy template access
    pizzas = []
    for row in result:
        pizzas.append({
            'pizza_id': row[0],
            'name': row[1],
            'price': row[2],
            'is_vegetarian': row[3],
            'is_vegan': row[4]
        })

    return render_template(
        "homepage.html",
        current_year=datetime.now().year,
        customer=customer,
        pizzas=pizzas
    )

# -----------------------------
# SIGN IN PAGE
# -----------------------------
@app.route("/signin", methods=["GET", "POST"])
def signIn_route():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # --- Basic validation ---
        if not email or not password:
            return "Both email and password are required", 400

        # --- Check if customer exists ---
        customer = Customer.query.filter_by(email=email).first()

        # --- Validate credentials ---
        if not customer or customer.password != password:
            return redirect(url_for("login_failed_route"))

        # --- Store logged-in customer ID in session ---
        session['customer_id'] = customer.customer_id

        # --- Successful login ---
        session['customer_id'] = customer.customer_id
        session['customer_name'] = f"{customer.first_name} {customer.last_name}"
        return redirect(url_for("index"))

    # GET request
    return render_template("signIn.html", current_year=datetime.now().year)

# -----------------------------
# SIGN UP PAGE
# -----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signUp_route():
    max_birth_date = date.today().isoformat()

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        birth_date_str = request.form.get("birth_date")
        postcode = request.form.get("postcode")

        if not all([first_name, last_name, email, password, birth_date_str, postcode]):
            return "All fields are required", 400

        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid birth date format", 400

        if not postcode.isdigit() or len(postcode) != 5:
            return "Invalid postcode format", 400

        # --- Check for existing email ---
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            return "Email already registered", 400

        # --- Create and save new customer ---
        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            birth_date=birth_date,
            postcode=postcode
        )

        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for("signIn_route"))

    return render_template("signUp.html", current_year=datetime.now().year, max_birth_date=max_birth_date)

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    session.pop('cart', None)
    return redirect(url_for("index"))

# -----------------------------
# LOGIN FAILED PAGE
# -----------------------------
@app.route("/login_failed")
def login_failed_route():
    return render_template("login_failed.html", current_year=datetime.now().year)

# -----------------------------
# ADD TO CART
# -----------------------------

@app.route("/add_to_cart/<int:pizza_id>", methods=["POST"])
def add_to_cart(pizza_id):
    if "customer_id" not in session:
        flash("Please sign in to add pizzas to your cart.", "warning")
        return redirect(url_for("signIn_route"))

    pizza = Pizza.query.get(pizza_id)
    if not pizza or not pizza.active:
        return "Pizza not available", 404

    # Calculate pizza price dynamically from PizzaMenu view
    pizza_data = db.session.execute(db.text("""
        SELECT price, name
        FROM PizzaMenu
        WHERE pizza_id = :pizza_id
    """), {"pizza_id": pizza_id}).fetchone()
    
    if not pizza_data:
        return "Pizza not found", 404
    
    pizza_price = round(float(pizza_data[0]), 2)
    pizza_name = pizza_data[1]

    # Initialize session cart if not present
    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    for item in cart:
        if item.get("pizza_id") == pizza_id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "pizza_id": pizza.pizza_id,
            "name": pizza_name,
            "price": pizza_price,
            "quantity": 1
        })

    session["cart"] = cart
    session.modified = True

    flash(f"Added {pizza_name} to your cart!", "success")
    return redirect(url_for("index"))


# -----------------------------
# CLEAR CART/REMOVE PAGE
# -----------------------------
@app.route("/clear_cart")
def clear_cart():
    session.pop("cart", None)
    flash("Your cart has been cleared.", "info")
    return redirect(url_for("cart_summary_route"))

# -----------------------------
# CART SUMMARY PAGE
# -----------------------------
@app.route("/cart")
def cart_summary_route():
    cart = session.get("cart", [])
    total_price = round(sum(item["quantity"] * item["price"] for item in cart), 2)

    return render_template(
        "cart_summary.html",
        cart_items=cart,
        total_price=total_price,
        current_year=datetime.now().year
    )

# -----------------------------
# ADD PRODUCTS PAGE
# -----------------------------

@app.route("/add_product_to_cart/<int:product_id>", methods=["POST"])
def add_product_to_cart(product_id):
    if "customer_id" not in session:
        flash("Please sign in to add products to your cart.", "warning")
        return redirect(url_for("signIn_route"))

    product = Product.query.get(product_id)
    if not product or not product.active:
        return "Product not available", 404

    quantity = int(request.form.get("quantity", 1))
    if quantity <= 0:
        quantity = 1

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    # Check if product already in cart
    for item in cart:
        if item.get("product_id") == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({
            "product_id": product.product_id,
            "name": product.name,
            "price": float(product.cost),
            "quantity": quantity
        })

    session["cart"] = cart
    session.modified = True

    flash(f"Added {product.name} x{quantity} to your cart!", "success")
    return redirect(url_for("products_page"))

@app.route("/products")
def products_page():
    customer_id = session.get("customer_id")
    customer = Customer.query.get(customer_id) if customer_id else None

    # Fetch all active products (drinks/snacks)
    products = Product.query.filter_by(active=True).all()

    return render_template(
        "products_page.html",
        products=products,
        current_year=datetime.now().year,
        customer=customer
    )

# -----------------------------
# CHECKOUT PAGE
# -----------------------------
@app.route("/checkout")
def checkout_page():
    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))
    
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please sign in to checkout.", "warning")
        return redirect(url_for("signIn_route"))
    
    customer = Customer.query.get(customer_id)
    today = date.today()
    is_birthday = (customer.birth_date.month == today.month and customer.birth_date.day == today.day)
    
    # Calculate totals
    subtotal = 0.0
    pizza_items = []
    drink_items = []
    other_items = []
    
    for item in cart:
        item_total = item.get("quantity", 1) * item.get("price", 0)
        subtotal += item_total

        # Check if it's a pizza
        if 'pizza_id' in item and item.get('pizza_id') is not None:
            pizza_items.append(item)
        # Check if it's a product (drink or snack)
        elif 'product_id' in item and item.get('product_id') is not None:
            product = Product.query.get(item['product_id'])
            if product and product.category == 'drink':
                drink_items.append(item)
            else:
                other_items.append(item)
    
    # Calculate discounts
    discounts = []
    total_discount = 0.0
    
    # 1. BIRTHDAY DISCOUNT: Free cheapest pizza + free cheapest drink
    if is_birthday and (pizza_items or drink_items):
        if pizza_items:
            cheapest_pizza = min(pizza_items, key=lambda x: x['price'])
            pizza_discount = round(cheapest_pizza['price'], 2)
            total_discount += pizza_discount
            discounts.append({
                'type': 'birthday_pizza',
                'description': '🎂 Birthday Gift: Free Pizza',
                'amount': pizza_discount
            })

        if drink_items:
            cheapest_drink = min(drink_items, key=lambda x: x['price'])
            drink_discount = round(cheapest_drink['price'], 2)
            total_discount += drink_discount
            discounts.append({
                'type': 'birthday_drink',
                'description': '🎂 Birthday Gift: Free Drink',
                'amount': drink_discount
            })
    
    # 2. LOYALTY DISCOUNT: 10% off after every 10 pizzas
    loyalty_query = db.session.execute(
        text("SELECT total_pizzas_bought, eligible_for_loyalty_discount FROM CustomerLoyalty WHERE customer_id = :cid"),
        {"cid": customer_id}
    ).fetchone()
    
    if loyalty_query and loyalty_query[1]:  # eligible_for_loyalty_discount
        total_pizzas = loyalty_query[0]
        # Calculate how many times customer has earned 10% discount
        times_earned = total_pizzas // 10
        if times_earned > 0:
            loyalty_discount = subtotal * 0.10
            total_discount += loyalty_discount
            discounts.append({
                'type': 'loyalty',
                'description': f'� Loyalty Reward ({total_pizzas} pizzas bought): 10% off',
                'amount': loyalty_discount
            })
    
    # 3. DISCOUNT CODE (only if not already applied and valid)
    discount_code = session.get("discount_code")
    if discount_code:
        code_obj = DiscountCode.query.get(discount_code)
        if code_obj:
            # Check if it's single-use and already used
            if code_obj.single_use:
                already_used = UsedDiscountCode.query.filter_by(
                    customer_id=customer_id,
                    code=discount_code
                ).first()
                if already_used:
                    flash(f"Discount code '{discount_code}' has already been used.", "warning")
                    session.pop("discount_code", None)
                    discount_code = None
                    code_obj = None
            
            if code_obj:
                if code_obj.percent_off:
                    code_discount = (float(code_obj.percent_off) / 100.0) * subtotal
                elif code_obj.amount_off:
                    code_discount = min(float(code_obj.amount_off), subtotal)
                else:
                    code_discount = 0.0
                
                if code_discount > 0:
                    total_discount += code_discount
                    discounts.append({
                        'type': 'code',
                        'description': f'💳 {code_obj.description}',
                        'amount': code_discount
                    })
    
    final_total = max(0, subtotal - total_discount)
    
    # Calculate estimated delivery time
    # Find delivery person for customer's postcode
    delivery_person = DeliveryPerson.query.filter_by(postcode=customer.postcode).first()
    
    estimated_delivery_minutes = 0  # Base delivery time
    if delivery_person and delivery_person.last_delivery_at:
        # Calculate cooldown remaining
        time_since_last = (datetime.now() - delivery_person.last_delivery_at).total_seconds() / 60
        cooldown_remaining = max(0, 30 - time_since_last)
        estimated_delivery_minutes += cooldown_remaining
    
    estimated_delivery_time = datetime.now() + timedelta(minutes=estimated_delivery_minutes)
    
    return render_template(
        "checkout.html",
        cart_items=cart,
        subtotal=round(subtotal, 2),
        discounts=discounts,
        total_discount=round(total_discount, 2),
        total_price=round(final_total, 2),
        discount_code=discount_code,
        is_birthday=is_birthday,
        estimated_delivery_minutes=int(estimated_delivery_minutes),
        estimated_delivery_time=estimated_delivery_time.strftime("%H:%M"),
        current_year=datetime.now().year
    )

# -----------------------------
# APPLY DISCOUNT CODE
# -----------------------------
@app.route("/apply_discount", methods=["POST"])
def apply_discount():
    code_input = request.form.get("discount_code", "").strip().upper()
    
    if not code_input:
        flash("Please enter a discount code.", "warning")
        return redirect(url_for("checkout_page"))
    
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please sign in first.", "warning")
        return redirect(url_for("signIn_route"))
    
    # Check if code exists
    discount_code = DiscountCode.query.get(code_input)
    if not discount_code:
        flash("Invalid discount code.", "error")
        return redirect(url_for("checkout_page"))
    
    # Check if it's a single-use code and has been used
    if discount_code.single_use:
        already_used = UsedDiscountCode.query.filter_by(
            customer_id=customer_id,
            code=code_input
        ).first()
        if already_used:
            flash(f"You have already used this discount code.", "error")
            return redirect(url_for("checkout_page"))
    
    # Apply the discount code
    session["discount_code"] = code_input
    session.modified = True
    flash(f"Discount code '{code_input}' applied successfully!", "success")
    return redirect(url_for("checkout_page"))

# -----------------------------
# REMOVE DISCOUNT CODE
# -----------------------------
@app.route("/remove_discount", methods=["POST"])
def remove_discount():
    session.pop("discount_code", None)
    session.modified = True
    flash("Discount code removed.", "info")
    return redirect(url_for("checkout_page"))



# -----------------------------
# PLACE ORDER PAGE
# -----------------------------
@app.route("/place_order", methods=["POST"])
def place_order_route():
    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))

    customer_id = session.get("customer_id")
    if not customer_id:
        flash("You must sign in to place an order.", "warning")
        return redirect(url_for("signIn_route"))

    customer = Customer.query.get(customer_id)
    customer_name = f"{customer.first_name} {customer.last_name}"

    try:
        subtotal = 0.0
        discount_code = session.get("discount_code")
        today = date.today()
        is_birthday = (customer.birth_date.month == today.month and customer.birth_date.day == today.day)

        # 1️⃣ Create Order (commit later)
        new_order = Order(
            customer_id=customer_id,
            postcode_snapshot=customer.postcode,
            total_amount=0.0,  # placeholder, calculate after items added
            status='pending',
            order_time=datetime.now(),
            discount_code=discount_code  # Save discount code if applied
        )
        db.session.add(new_order)
        db.session.flush()  # Get new_order.order_id without committing

        # Track items for birthday discount
        pizza_prices = []
        drink_prices = []

        # 2️⃣ Add pizzas to OrderPizza
        for item in cart:
            if 'pizza_id' in item:
                pizza = Pizza.query.get(item['pizza_id'])
                if not pizza or not pizza.active:
                    continue

                # Use the price from cart (already calculated via PizzaMenu view)
                pizza_price = round(float(item['price']), 2)

                quantity = max(1, int(item.get('quantity', 1)))

                order_pizza = OrderPizza(
                    order_id=new_order.order_id,
                    pizza_id=pizza.pizza_id,
                    quantity=quantity,
                    unit_price=pizza_price,
                    name_snapshot=pizza.name
                )
                subtotal += pizza_price * quantity
                pizza_prices.append(pizza_price)
                db.session.add(order_pizza)

        # 3️⃣ Add products to OrderProduct
        for item in cart:
            if 'product_id' in item:
                product = Product.query.get(item['product_id'])
                if not product or not product.active:
                    continue

                quantity = max(1, int(item.get('quantity', 1)))
                unit_price = round(float(item.get('price', product.cost)), 2)

                order_product = OrderProduct(
                    order_id=new_order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    name_snapshot=product.name
                )
                subtotal += unit_price * quantity

                # Track drinks for birthday discount
                if product.category == 'drink':
                    drink_prices.append(unit_price)

                db.session.add(order_product)

        # 4️⃣ Calculate and apply all discounts
        total_discount = 0.0
        discount_messages = []
        
        # Birthday discount: Free cheapest pizza + free cheapest drink
        if is_birthday:
            if pizza_prices:
                cheapest_pizza = min(pizza_prices)
                total_discount += cheapest_pizza
                discount_messages.append(f"🎂 Birthday Gift: Free Pizza (€{cheapest_pizza:.2f})")
            
            if drink_prices:
                cheapest_drink = min(drink_prices)
                total_discount += cheapest_drink
                discount_messages.append(f"🎂 Birthday Gift: Free Drink (€{cheapest_drink:.2f})")
        
        # Loyalty discount: 10% off after every 10 pizzas
        loyalty_query = db.session.execute(
            text("SELECT total_pizzas_bought, eligible_for_loyalty_discount FROM CustomerLoyalty WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).fetchone()
        
        if loyalty_query and loyalty_query[1]:  # eligible_for_loyalty_discount
            loyalty_discount = round(subtotal * 0.10, 2)
            total_discount += loyalty_discount
            discount_messages.append(f"🌟 Loyalty Reward: 10% off (€{loyalty_discount:.2f})")
        
        # Discount code
        if discount_code:
            code_obj = DiscountCode.query.get(discount_code)
            if code_obj:
                code_discount = 0.0
                if code_obj.percent_off:
                    code_discount = (float(code_obj.percent_off) / 100.0) * subtotal
                    discount_messages.append(f"💳 {code_obj.description}: {code_obj.percent_off}% off (€{code_discount:.2f})")
                elif code_obj.amount_off:
                    code_discount = min(float(code_obj.amount_off), subtotal)
                    discount_messages.append(f"💳 {code_obj.description}: €{code_discount:.2f} off")
                
                total_discount += code_discount
                
                # Track single-use code usage
                if code_obj.single_use:
                    used_code = UsedDiscountCode(
                        customer_id=customer_id,
                        code=discount_code,
                        order_id=new_order.order_id,
                        used_at=datetime.now()
                    )
                    db.session.add(used_code)

        # Apply final amount
        final_amount = max(0, subtotal - total_discount)
        new_order.total_amount = round(final_amount, 2)
        new_order.applied_discount = round(total_discount, 2)
        
        # 5️⃣ Assign delivery person based on postcode
        delivery_person = DeliveryPerson.query.filter_by(postcode=customer.postcode).first()
        
        if delivery_person:
            # Check if delivery person is available (30 minute cooldown)
            if delivery_person.last_delivery_at:
                time_since_last = (datetime.now() - delivery_person.last_delivery_at).total_seconds() / 60
                if time_since_last < 30:
                    # Delivery person is in cooldown, order will wait
                    flash(f"Your delivery will be delayed by {int(30 - time_since_last)} minutes due to driver availability.", "info")
            
            new_order.delivery_person_id = delivery_person.delivery_person_id
            new_order.status = 'preparing'
            
            # Update delivery person's last_delivery_at to current time (start of delivery)
            delivery_person.last_delivery_at = datetime.now()
        else:
            # No delivery person for this postcode
            flash(f"Warning: No delivery person assigned for postcode {customer.postcode}. Order placed as pending.", "warning")
        
        db.session.commit()

        # 6️⃣ Clear cart and discount code from session
        session.pop("cart", None)
        session.pop("discount_code", None)
        session.modified = True

        # Show discount messages
        for msg in discount_messages:
            flash(msg, "success")
        flash("Your order has been placed successfully!", "success")
        return render_template("order_success.html", customer_name=customer_name, current_year=datetime.now().year)

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to place the order. Error: {str(e)}", "danger")
        return redirect(url_for("cart_summary_route"))

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.secret_key = "your-secret-key"
    app.run(debug=True, use_reloader=False)

