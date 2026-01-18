from flask import Flask, render_template, request, redirect, session, flash, jsonify
import sqlite3
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

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
    # Users table (multi-user support)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # Expenses table
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

# Call init_db() when app starts
init_db()

# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db()
        existing = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            flash("Username already exists!", "error")
            conn.close()
            return redirect("/register")

        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash("User Registered! Please login.", "success")
        return redirect("/")
    return render_template("register.html")

# ---------------- Login ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()

        if user:
            session.clear()  # Clear previous sessions
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect("/dashboard")
        else:
            flash("Invalid Credentials", "error")
    return render_template("login.html")

# ---------------- Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect("/")
    return render_template("dashboard.html", username=session['username'])

# ---------------- Add Expense ----------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Please login first."})

    user_id = session['user_id']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                 (user_id, amount, category, date))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Expense Added!"})

# ---------------- Get Expenses ----------------
@app.route("/get_expenses")
def get_expenses():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(exp) for exp in expenses])

# ---------------- Get Total Expense ----------------
@app.route("/get_total")
def get_total():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"total": 0})

    conn = get_db()
    total = conn.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return jsonify({"total": total["total"] if total["total"] else 0})

# ---------------- AI Tips ----------------
@app.route("/ai_tips")
def ai_tips():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"tip": "Please login first."})

    conn = get_db()
    category = conn.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id=?
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()

    if category:
        tip = f"Tip: You spend the most on '{category['category']}'. Consider saving more here!"
    else:
        tip = "Tip: Add some expenses first to get AI suggestions."

    return jsonify({"tip": tip})

# ---------------- Free AI Chat using DialoGPT ----------------
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

@app.route("/chat", methods=["POST"])
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"response": "User not logged in."})

    user_message = request.json.get("message", "").lower()
    if not user_message:
        return jsonify({"response": "Please type a message."})

    conn = get_db()
    # Get total spent per category
    expenses = conn.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id=?
        GROUP BY category
    """, (user_id,)).fetchall()
    conn.close()

    # Convert to dict for easy lookup
    expense_dict = {exp['category'].lower(): exp['total'] for exp in expenses}

    # Categories from user message
    categories_in_message = [cat for cat in expense_dict.keys() if cat in user_message]

    if categories_in_message:
        cat = categories_in_message[0]
        spent = expense_dict[cat]
        response = f"You spent ₹{spent} on {cat}. To reduce it, consider budgeting, cutting unnecessary purchases, or finding cheaper alternatives."
    else:
        # General tip
        if expense_dict:
            # Most spent category
            most_spent = max(expense_dict, key=expense_dict.get)
            spent = expense_dict[most_spent]
            response = f"You spent the most on {most_spent} (₹{spent}). Try to monitor this category to save more."
        else:
            response = "No expenses recorded yet. Add some expenses to get useful tips!"

    return jsonify({"response": response})

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run()