import os
from flask import *
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from ORM.Customer import Customer
from ORM.Pizza import Pizza
from ORM.Product import Product
from ORM.OrderProduct import OrderProduct
from ORM.OrderPizza import OrderPizza
from ORM.Order import Order
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

    # Fetch all active pizzas
    pizzas = Pizza.query.filter_by(active=True).all()

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

    # Calculate pizza price dynamically
    # Example: sum of ingredient costs + base price
    base_price = 5  # You can adjust this
    total_cost = base_price
    for pi in pizza.ingredients:
        # Assume cost is per gram
        total_cost += (pi.grams / 100.0) * pi.ingredient.cost  # convert grams to 100g units

    pizza_price = round(total_cost, 2)  # round to 2 decimals

    # Initialize session cart if not present
    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    for item in cart:
        if item["pizza_id"] == pizza_id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "pizza_id": pizza.pizza_id,
            "name": pizza.name,
            "price": pizza_price,
            "quantity": 1
        })

    session["cart"] = cart
    session.modified = True

    flash(f"Added {pizza.name} to your cart!", "success")
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
    total_price = sum(item["quantity"] * item["price"] for item in cart)

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
    total_price = sum(item["quantity"] * item["price"] for item in cart)

    # Always define discount
    discount = 0.0

    customer_id = session.get("customer_id")
    if customer_id:
        customer = Customer.query.get(customer_id)
        today = date.today()
        if customer.birth_date.month == today.month and customer.birth_date.day == today.day:
            discount = 0.10 * total_price

    return render_template(
        "checkout.html",
        cart_items=cart,
        total_price=round(total_price - discount, 2),
        discount=round(discount, 2),
        current_year=datetime.now().year
    )



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
        total_amount = 0.0

        # 1️⃣ Create Order (commit later)
        new_order = Order(
            customer_id=customer_id,
            postcode_snapshot=customer.postcode,
            total_amount=0.0,  # placeholder, calculate after items added
            status='pending',
            order_time=datetime.now()
        )
        db.session.add(new_order)
        db.session.flush()  # Get new_order.order_id without committing

        # 2️⃣ Add pizzas to OrderPizza
        for item in cart:
            if 'pizza_id' in item:
                # Recalculate pizza price dynamically
                pizza = Pizza.query.get(item['pizza_id'])
                if not pizza or not pizza.active:
                    continue  # skip unavailable pizzas

                base_price = 5
                pizza_price = base_price
                for pi in pizza.ingredients:
                    pizza_price += (pi.grams / 100.0) * pi.ingredient.cost
                pizza_price = round(pizza_price, 2)

                quantity = max(1, int(item.get('quantity', 1)))

                order_pizza = OrderPizza(
                    order_id=new_order.order_id,
                    pizza_id=pizza.pizza_id,
                    quantity=quantity,
                    unit_price=pizza_price,
                    name_snapshot=pizza.name
                )
                total_amount += pizza_price * quantity
                db.session.add(order_pizza)

        # 3️⃣ Add products to OrderProduct
        for item in cart:
            if 'product_id' in item:
                product = Product.query.get(item['product_id'])
                if not product or not product.active:
                    continue  # skip unavailable products

                quantity = max(1, int(item.get('quantity', 1)))
                unit_price = float(item.get('price', product.cost))

                order_product = OrderProduct(
                    order_id=new_order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    name_snapshot=product.name
                )
                total_amount += unit_price * quantity
                db.session.add(order_product)

        # 4️⃣ Update total_amount and commit transaction
        today = date.today()
        if customer.birth_date.month == today.month and customer.birth_date.day == today.day:
            total_amount *= 0.9  # Apply 10% discount
            flash("Happy Birthday! You got 10% off your order.", "success")

        new_order.total_amount = round(total_amount, 2)
        db.session.commit()

        # 5️⃣ Clear cart session
        session.pop("cart", None)
        session.modified = True

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

