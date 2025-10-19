from flask import Flask, render_template, request  # <-- add request here
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("homepage.html", current_year=datetime.now().year)


# -----------------------------
# SIGN IN PAGE
# -----------------------------
@app.route("/signin", methods=["GET", "POST"])
def signIn_route():
    if request.method == "POST":  # <-- use request here, not app.request
        email = request.form.get("email")
        password = request.form.get("password")
        # TODO: Validate login credentials here
        print(f"Login attempt from {email}")
        # For now, just reload the same page
    return render_template("signIn.html", current_year=datetime.now().year)

# -----------------------------
# SIGN UP PAGE
# -----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signUp_route():
    if request.method == "POST":  # <-- same fix
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        # TODO: Save user data or handle registration logic
        print(f"New signup: {username} ({email})")
    return render_template("signUp.html", current_year=datetime.now().year)

# -----------------------------
# RUN THE APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
