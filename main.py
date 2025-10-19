import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from ORM.Customer import Customer
from ORM import db

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind the shared db to the app
db.init_app(app)
with app.app_context():
    db.create_all() # create tables if not exist

@app.route("/")
def index():
    return render_template("homepage.html", current_year=datetime.now().year)

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

        # --- Successful login ---
        return redirect(url_for("index"))

    # --- GET request: show login page ---
    return render_template("signIn.html", current_year=datetime.now().year)


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

        # --- Basic validations ---
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
            password=password,  # (plain for now — later use hash)
            birth_date=birth_date,
            postcode=postcode
        )

        db.session.add(new_customer)
        db.session.commit()

        # --- Redirect to sign-in page ---
        return redirect(url_for("signIn_route"))

    return render_template(
        "signUp.html",
        current_year=datetime.now().year,
        max_birth_date=max_birth_date
    )

@app.route("/login_failed")
def login_failed_route():
    return render_template("login_failed.html", current_year=datetime.now().year)

@app.route("/cart")
def cart_summary_route():
    cart_items = [
        {"name": "Margherita", "quantity": 2, "price": 10},
        {"name": "Pepperoni", "quantity": 1, "price": 12}
    ]
    total_price = sum(item["quantity"] * item["price"] for item in cart_items)
    return render_template("cart_summary.html", cart_items=cart_items,
                           total_price=total_price, current_year=datetime.now().year)

@app.route("/place_order", methods=["POST"])
def place_order_route():
    order_success = True  # change logic if needed
    customer_name = "John Doe"
    if order_success:
        return render_template("order_success.html", customer_name=customer_name,
                               current_year=datetime.now().year)
    return render_template("order_failed.html", current_year=datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True)
