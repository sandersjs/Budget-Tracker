import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = os.path.join("data", "expenses.json")

# Ensure data directory and file exist
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_expenses():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

def calculate_summary(expenses):
    summary_data = {}
    for e in expenses:
        category = e["category"]
        summary_data[category] = summary_data.get(category, 0) + float(e["amount"])
    total = sum(summary_data.values())
    return summary_data, total

@app.route("/")
def index():
    expenses = load_expenses()
    total = sum(float(e["amount"]) for e in expenses)
    return render_template("index.html", total=total, expenses=expenses)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    expenses = load_expenses()
    message = None

    if request.method == "POST":
        item = request.form.get("item")
        amount = request.form.get("amount")
        category = request.form.get("category")

        new_expense = {
            "item": item,
            "amount": amount,
            "category": category
        }

        expenses.append(new_expense)
        save_expenses(expenses)

        message = f"Expense '{item}' added successfully!"

    summary_data, total = calculate_summary(expenses)
    return render_template("page1.html", message=message, expenses=expenses, summary=summary_data, total=total)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_expense(index):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        deleted = expenses.pop(index)
        save_expenses(expenses)
        message = f"Deleted expense '{deleted['item']}'"
    else:
        message = "Expense not found."
    summary_data, total = calculate_summary(expenses)
    return render_template("page1.html", message=message, expenses=expenses, summary=summary_data, total=total)

@app.route("/summary")
def summary():
    expenses = load_expenses()
    summary_data, total = calculate_summary(expenses)
    return render_template("page2.html", summary=summary_data, total=total)

@app.route("/reset", methods=["POST"])
def reset():
    save_expenses([])  # Clear all expenses
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)