from flask import Flask, render_template, request, redirect, session, flash, jsonify
import sqlite3
from datetime import datetime

# ---------------- App Config ----------------
app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_NAME = "expense.db"

# ---------------- Database Helper ----------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- Initialize Database ----------------
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- Rule-Based Insight ----------------
def generate_insights(expenses):
    total = sum(e["amount"] for e in expenses)

    if total > 10000:
        return "⚠️ High spending this month. Try reducing food & shopping expenses."
    elif total > 5000:
        return "📊 Moderate spending. Track daily expenses carefully."
    else:
        return "✅ Great job! Your expenses are under control."

# ---------------- Login ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

        flash("Invalid credentials", "error")

    return render_template("login.html")

# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("All fields required", "error")
            return redirect("/register")

        conn = get_db()
        if conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone():
            flash("Username already exists", "error")
            conn.close()
            return redirect("/register")

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        flash("Registered successfully! Login now.", "success")
        return redirect("/")

    return render_template("register.html")

# ---------------- Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html", username=session["username"])

# ---------------- Add Expense ----------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Login required"})

    try:
        amount = float(request.form["amount"])
    except:
        return jsonify({"status": "error", "message": "Invalid amount"})

    category = request.form["category"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
        (session["user_id"], amount, category, date)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# ---------------- Get Expenses ----------------
@app.route("/get_expenses")
def get_expenses():
    if "user_id" not in session:
        return jsonify([])

    conn = get_db()
    expenses = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return jsonify([dict(e) for e in expenses])

# ---------------- Total Expense ----------------
@app.route("/get_total")
def get_total():
    if "user_id" not in session:
        return jsonify({"total": 0})

    conn = get_db()
    total = conn.execute(
        "SELECT SUM(amount) AS total FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()
    conn.close()

    return jsonify({"total": total["total"] or 0})

# ---------------- AI Tips ----------------
@app.route("/ai_tips")
def ai_tips():
    if "user_id" not in session:
        return jsonify({"tip": "Login first to get AI tips."})

    conn = get_db()
    expenses = conn.execute(
        "SELECT amount FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    tip = generate_insights([dict(e) for e in expenses])
    return jsonify({"tip": tip})

# ---------------- AI Chat ----------------
@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"response": "Please login first."})

    message = request.json.get("message", "").lower()

    conn = get_db()
    data = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id=?
        GROUP BY category
    """, (session["user_id"],)).fetchall()
    conn.close()

    if not data:
        return jsonify({"response": "No expenses found. Add some expenses first."})

    expense_map = {d["category"].lower(): d["total"] for d in data}

    for cat in expense_map:
        if cat in message:
            return jsonify({
                "response": f"You spent ₹{expense_map[cat]} on {cat}. Consider reducing it."
            })

    max_cat = max(expense_map, key=expense_map.get)
    return jsonify({
        "response": f"Your highest spending is on {max_cat} (₹{expense_map[max_cat]})."
    })

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)
