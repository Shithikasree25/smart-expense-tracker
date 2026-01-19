from flask import Flask, render_template, request, jsonify, redirect, session
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- HOME / DASHBOARD ----------------
@app.route("/")
def dashboard():
    if "user" not in session:
        session["user"] = "User"  # temporary login
    return render_template("dashboard.html", username=session["user"])

# ---------------- ADD EXPENSE ----------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    amount = request.form.get("amount")
    category = request.form.get("category")
    print("Expense added:", amount, category)
    return redirect("/")

# ---------------- AI TIPS ----------------
@app.route("/ai_tips")
def ai_tips():
    tips = [
        "Save at least 20% of your income every month.",
        "Avoid impulse purchases.",
        "Track expenses daily for better control.",
        "Cut unnecessary subscriptions."
    ]
    return jsonify({"tip": random.choice(tips)})

# ---------------- AI CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").lower()

    if "save" in message:
        reply = "Saving regularly improves financial stability."
    elif "expense" in message:
        reply = "Categorizing expenses helps find spending patterns."
    elif "budget" in message:
        reply = "Set a monthly budget and stick to it."
    else:
        reply = "Ask me about saving, budgeting, or expenses."

    return jsonify({"response": reply})

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
