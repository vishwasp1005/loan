from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import sqlite3
import pandas as pd
import os
import sys

print("=" * 50)
print("🚀 FLASK APP STARTING")
print(f"📂 Working directory: {os.getcwd()}")
print(f"📂 Files available: {os.listdir('.')}")
print(f"🔧 PORT from environment: {os.environ.get('PORT', 'NOT SET')}")
print("=" * 50)
sys.stdout.flush()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "loan_secret_key_123"

print("🚀 Starting Flask app...")
print(f"📂 Current directory: {os.getcwd()}")
print(f"📂 Files in directory: {os.listdir('.')}")

# -------------------------------------------------
# LOAD ML MODEL SAFELY
# -------------------------------------------------
try:
    model = joblib.load("loan_model.pkl")
    print("✅ Model loaded successfully!")
except Exception as e:
    model = None
    print(f"⚠️ MODEL FAILED TO LOAD: {e}")


# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DB_NAME = "database.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # USERS TABLE
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        # DEFAULT ADMIN
        c.execute("SELECT * FROM users WHERE username=?", ("admin",))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      ("admin", "12345"))

        # HISTORY TABLE - NOW WITH USERNAME TO TRACK USER DATA
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                age REAL,
                income REAL,
                loan_amount REAL,
                credit_score REAL,
                dti_ratio REAL,
                education TEXT,
                employment TEXT,
                prediction INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

init_db()


# -------------------------------------------------
# LOGIN HELPERS
# -------------------------------------------------
def login_required():
    return "user" in session


def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None


# -------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if login_required():
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if validate_user(username, password):
            session["user"] = username
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if login_required():
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Validate inputs
        if not username or not password:
            return render_template("signup.html", error="Username and password are required!")
        
        if len(username) < 3:
            return render_template("signup.html", error="Username must be at least 3 characters!")
        
        if len(password) < 5:
            return render_template("signup.html", error="Password must be at least 5 characters!")

        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))

            conn.commit()
            conn.close()
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            # This specifically catches duplicate username errors
            return render_template("signup.html", error="Username already exists!")
        except Exception as e:
            # Catch any other errors
            return render_template("signup.html", error=f"An error occurred: {str(e)}")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
@app.route("/")
def home():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("home.html")


# -------------------------------------------------
# PREDICT FORM (GET)
# -------------------------------------------------
@app.route("/predict", methods=["GET"])
def predict_page():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("predict.html")


# -------------------------------------------------
# PREDICT RESULT (POST) - NOW SAVES USERNAME
# -------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if not login_required():
        return redirect(url_for("login"))

    try:
        # Get current logged-in user
        username = session.get("user")
        
        age = float(request.form["age"])
        income = float(request.form["income"])
        loan_amount = float(request.form["loan_amount"])
        credit_score = float(request.form["credit_score"])
        dti_ratio = float(request.form["dti_ratio"])
        education = request.form["education"]
        employment = request.form["employment"]

        # Prepare ML input
        data = pd.DataFrame([{
            "Age": age,
            "Income": income,
            "LoanAmount": loan_amount,
            "CreditScore": credit_score,
            "DTIRatio": dti_ratio,
            "Education": education,
            "EmploymentType": employment
        }])

        prediction = int(model.predict(data)[0])

        # SAVE TO DB WITH USERNAME
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO history (username, age, income, loan_amount, credit_score, dti_ratio, education, employment, prediction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, age, income, loan_amount, credit_score, dti_ratio, education, employment, prediction))

        conn.commit()
        conn.close()

        return render_template("result.html", prediction=prediction)

    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------------------------
# DASHBOARD - NOW SHOWS ONLY USER'S OWN DATA
# -------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    # Get current logged-in user
    username = session.get("user")

    conn = sqlite3.connect(DB_NAME)
    
    # Only get history for current user
    df = pd.read_sql_query("SELECT * FROM history WHERE username = ?", conn, params=(username,))
    
    conn.close()

    safe = len(df[df["prediction"] == 0])
    danger = len(df[df["prediction"] == 1])
    total = len(df)

    return render_template(
        "dashboard.html",
        history=df.to_dict(orient="records"),
        safe=safe,
        danger=danger,
        total=total
    )

@app.route("/about")
def about():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("about.html")


@app.route("/contact")
def contact():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("contact.html")


@app.route("/send_message", methods=["POST"])
def send_message():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    print("📩 New Contact Message")
    print("Name:", name)
    print("Email:", email)
    print("Message:", message)

    return render_template("contact.html", sent=True)



# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting server on port {port}...")
    sys.stdout.flush()
    app.run(host="0.0.0.0", port=port, debug=False)
