"""
Personal Expense Tracker
Module 02 — Python Mini Project

Features:
- Add an expense with date, category, amount and description
- View all saved expenses
- View total spending
- View category-wise spending
- Delete an expense
- Save data in a local JSON file

Uses only Python's standard library.
"""

import json
import math
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("expenses.json")

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Health",
    "Entertainment",
    "Other",
]


def load_expenses():
    """Load expenses from JSON. Return an empty list if no file exists yet."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            cleaned = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                cleaned.append({
                    "id": int(item.get("id", 0)) if str(item.get("id", 0)).lstrip("-").isdigit() else 0,
                    "date": item.get("date", date.today().isoformat()),
                    "amount": float(item.get("amount", 0) or 0),
                    "category": item.get("category", "Other"),
                    "description": str(item.get("description", "No description")),
                })
            return cleaned
        print("Warning: expense data format is invalid. Starting with an empty list.")
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as error:
        print(f"Warning: could not read saved expenses: {error}")

    return []


def save_expenses(expenses):
    """Save all expenses to the JSON data file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"Could not save expenses: {error}")
        return False


def read_amount():
    """Ask for a positive expense amount."""
    while True:
        raw_amount = input("Enter amount (INR): ").strip()
        try:
            amount = float(raw_amount)
            if not math.isfinite(amount):
                print("Amount must be a finite number.")
                continue
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid number, for example 250 or 250.50.")


def choose_category():
    """Display categories and return the selected category."""
    print("\nExpense categories:")
    for number, category in enumerate(CATEGORIES, start=1):
        print(f"{number}. {category}")

    while True:
        choice = input("Choose a category number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        print(f"Enter a number between 1 and {len(CATEGORIES)}.")


def add_expense(expenses):
    """Collect and save a new expense."""
    print("\n--- Add Expense ---")
    amount = read_amount()
    category = choose_category()
    description = input("Enter a short description: ").strip()

    if not description:
        description = "No description"

    expense_date = input(f"Date (YYYY-MM-DD) [default: {date.today()}]: ").strip()
    if not expense_date:
        expense_date = date.today().isoformat()

    try:
        parsed_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        if parsed_date > date.today():
            print("Future dates are not allowed. Expense was not added.")
            return
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD. Expense was not added.")
        return

    next_id = max((item.get("id", 0) for item in expenses), default=0) + 1
    expense = {
        "id": next_id,
        "date": expense_date,
        "amount": amount,
        "category": category,
        "description": description,
    }

    expenses.append(expense)
    if save_expenses(expenses):
        print("Expense added and saved successfully.")


def view_expenses(expenses):
    """Print all saved expenses in a readable table."""
    print("\n--- All Expenses ---")
    if not expenses:
        print("No expenses recorded yet.")
        return

    print(f"{'ID':<5} {'Date':<12} {'Category':<16} {'Amount (INR)':>14}  Description")
    print("-" * 75)
    for item in sorted(expenses, key=lambda entry: (entry.get("date", ""), entry.get("id", 0))):
        print(
            f"{item.get('id', '-'):<5} "
            f"{item.get('date', '-'):<12} "
            f"{item.get('category', '-'):<16} "
            f"{item.get('amount', 0):>14,.2f}  "
            f"{item.get('description', '')}"
        )


def show_total(expenses):
    """Calculate and display total spending."""
    total = sum(float(item.get("amount", 0)) for item in expenses)
    print(f"\nTotal spending: INR {total:,.2f}")
    print(f"Number of expenses: {len(expenses)}")


def show_category_summary(expenses):
    """Calculate and display spending grouped by category."""
    print("\n--- Category-wise Spending ---")
    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = {}
    for item in expenses:
        category = item.get("category", "Other")
        totals[category] = totals.get(category, 0) + float(item.get("amount", 0))

    for category, amount in sorted(totals.items(), key=lambda pair: pair[1], reverse=True):
        print(f"{category:<18} INR {amount:>12,.2f}")


def delete_expense(expenses):
    """Delete an expense using its ID."""
    print("\n--- Delete Expense ---")
    if not expenses:
        print("No expenses available to delete.")
        return

    view_expenses(expenses)
    raw_id = input("\nEnter the ID of the expense to delete: ").strip()

    if not raw_id.isdigit():
        print("Please enter a valid numeric ID.")
        return

    expense_id = int(raw_id)
    for index, item in enumerate(expenses):
        if item.get("id") == expense_id:
            removed = expenses.pop(index)
            if save_expenses(expenses):
                print(f"Deleted expense: {removed.get('description', 'No description')}")
            return

    print("No expense found with that ID.")


def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 42)
    print("         PERSONAL EXPENSE TRACKER")
    print("=" * 42)
    print("1. Add an expense")
    print("2. View all expenses")
    print("3. View total spending")
    print("4. View category-wise spending")
    print("5. Delete an expense")
    print("6. Exit")
    print("=" * 42)


def main():
    expenses = load_expenses()
    print("Welcome to Personal Expense Tracker!")
    print(f"Loaded {len(expenses)} saved expense(s).")

    while True:
        show_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            show_total(expenses)
        elif choice == "4":
            show_category_summary(expenses)
        elif choice == "5":
            delete_expense(expenses)
        elif choice == "6":
            print("Thank you for using Personal Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 6.")


if __name__ == "__main__":
    main()
