from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import pandas as pd
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

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
# DATABASE CONNECTION (PostgreSQL)
# -------------------------------------------------
def get_db_connection():
    """Get PostgreSQL connection from Railway environment variable"""
    try:
        # Railway automatically provides DATABASE_URL
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("⚠️ DATABASE_URL not found, using local PostgreSQL")
            database_url = "postgresql://localhost/loanshield"
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None


def init_db():
    """Initialize PostgreSQL tables"""
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Cannot initialize database - no connection")
            return
            
        c = conn.cursor()

        # USERS TABLE
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # DEFAULT ADMIN
        c.execute("SELECT * FROM users WHERE username=%s", ("admin",))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                      ("admin", "12345"))

        # HISTORY TABLE
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
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
        print("✅ PostgreSQL database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

init_db()


# -------------------------------------------------
# LOGIN HELPERS
# -------------------------------------------------
def login_required():
    return "user" in session


def validate_user(username, password):
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                  (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"❌ Login validation error: {e}")
        return False


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
            conn = get_db_connection()
            if not conn:
                return render_template("signup.html", error="Database connection error!")
                
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                      (username, password))

            conn.commit()
            conn.close()
            print(f"✅ New user registered: {username}")
            return redirect(url_for("login"))

        except psycopg2.IntegrityError:
            return render_template("signup.html", error="Username already exists!")
        except Exception as e:
            print(f"❌ Signup error: {e}")
            return render_template("signup.html", error=f"An error occurred: {str(e)}")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------------------------------
# HOME PAGE - WITH REAL STATS
# -------------------------------------------------
@app.route("/")
def home():
    if not login_required():
        return redirect(url_for("login"))
    
    try:
        conn = get_db_connection()
        if conn:
            c = conn.cursor()
            
            # Get total predictions
            c.execute("SELECT COUNT(*) FROM history")
            total_predictions = c.fetchone()[0]
            
            # Get total users
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            
            conn.close()
            
            # Average response time (static for now, could be measured)
            avg_response_time = "< 1s"
            
            return render_template("home.html", 
                                 total_predictions=total_predictions,
                                 total_users=total_users,
                                 avg_response_time=avg_response_time)
        else:
            return render_template("home.html", 
                                 total_predictions=0,
                                 total_users=0,
                                 avg_response_time="< 1s")
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return render_template("home.html", 
                             total_predictions=0,
                             total_users=0,
                             avg_response_time="< 1s")


# -------------------------------------------------
# PREDICT FORM (GET)
# -------------------------------------------------
@app.route("/predict", methods=["GET"])
def predict_page():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("predict.html")


# -------------------------------------------------
# PREDICT RESULT (POST)
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

        # Store prediction details in session for PDF generation
        session['last_prediction'] = {
            'age': age,
            'income': income,
            'loan_amount': loan_amount,
            'credit_score': credit_score,
            'dti_ratio': dti_ratio,
            'education': education,
            'employment': employment,
            'prediction': prediction
        }

        # SAVE TO DB WITH USERNAME
        conn = get_db_connection()
        if conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO history (username, age, income, loan_amount, credit_score, dti_ratio, education, employment, prediction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, age, income, loan_amount, credit_score, dti_ratio, education, employment, prediction))

            conn.commit()
            conn.close()
            print(f"✅ Prediction saved for user: {username}")

        return render_template("result.html", prediction=prediction)

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return f"Error: {str(e)}"


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    # Get current logged-in user
    username = session.get("user")

    try:
        conn = get_db_connection()
        if not conn:
            return render_template("dashboard.html", history=[], safe=0, danger=0, total=0)
        
        # Get history for current user using DictCursor for easy conversion
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM history WHERE username = %s ORDER BY created_at DESC", (username,))
        rows = c.fetchall()
        conn.close()

        # Convert to list of dicts
        history = [dict(row) for row in rows]
        
        # Calculate stats
        safe = sum(1 for row in history if row['prediction'] == 0)
        danger = sum(1 for row in history if row['prediction'] == 1)
        total = len(history)

        print(f"📊 Dashboard for {username}: {total} predictions ({safe} safe, {danger} danger)")

        return render_template(
            "dashboard.html",
            history=history,
            safe=safe,
            danger=danger,
            total=total
        )
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return render_template("dashboard.html", history=[], safe=0, danger=0, total=0)


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
