from flask import *
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
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Example login validation
        # Replace this with your actual user-check logic
        if email != "test@example.com" or password != "secret":
            # Redirect to the login_failed page if login fails
            return redirect(url_for("login_failed_route"))

        # Redirect to homepage on successful login
        return redirect(url_for("index"))

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
# LOGIN FAILED PAGE
# -----------------------------
@app.route("/login_failed")
def login_failed_route():
    return render_template("login_failed.html", current_year=datetime.now().year)


# -----------------------------
# RUN THE APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
