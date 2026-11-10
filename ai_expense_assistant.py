"""
AI Expense Assistant
Module 05 — AI Tools & Mini Project

A command-line expense tracker with:
- Add, list and delete expenses
- Monthly and category-wise summaries
- Rule-based spending insights that work offline
- Optional Gemini-powered natural-language analysis

Privacy:
- Expense records stay in local expenses.json.
- The Gemini API key is read from the GEMINI_API_KEY environment variable.
- Only the summary data you choose to send is included in an AI request.
"""

import json
import time
import os
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("expenses.json")
CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills",
    "Education", "Health", "Entertainment", "Other"
]

# Use a currently supported Gemini model name; can be overridden by environment.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def load_expenses():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read expense data: {error}")
        return []


def save_expenses(expenses):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"Could not save expense data: {error}")
        return False


def add_expense(expenses):
    print("\n--- Add expense ---")
    while True:
        try:
            amount = float(input("Amount (INR): ").strip())
            if amount <= 0:
                print("Enter an amount greater than zero.")
                continue
            amount = round(amount, 2)
            break
        except ValueError:
            print("Enter a valid number, such as 250 or 250.50.")

    print("\nCategories:")
    for index, category in enumerate(CATEGORIES, 1):
        print(f"{index}. {category}")

    while True:
        choice = input("Choose category number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            category = CATEGORIES[int(choice) - 1]
            break
        print(f"Choose a number from 1 to {len(CATEGORIES)}.")

    description = input("Description: ").strip() or "No description"
    expense_date = input(f"Date YYYY-MM-DD [default {date.today()}]: ").strip()
    if not expense_date:
        expense_date = date.today().isoformat()

    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD. Expense not saved.")
        return

    next_id = max((item.get("id", 0) for item in expenses), default=0) + 1
    expenses.append({
        "id": next_id,
        "date": expense_date,
        "amount": amount,
        "category": category,
        "description": description
    })

    if save_expenses(expenses):
        print("Expense saved successfully.")


def list_expenses(expenses):
    print("\n--- Expense records ---")
    if not expenses:
        print("No expenses recorded.")
        return

    print(f"{'ID':<5}{'Date':<13}{'Category':<17}{'Amount (INR)':>15}  Description")
    print("-" * 75)
    for item in sorted(expenses, key=lambda row: (row.get("date", ""), row.get("id", 0))):
        print(
            f"{item.get('id', '-'):<5}"
            f"{item.get('date', '-'):<13}"
            f"{item.get('category', '-'):<17}"
            f"{item.get('amount', 0):>15,.2f}  "
            f"{item.get('description', '')}"
        )


def category_totals(expenses):
    totals = defaultdict(float)
    for item in expenses:
        totals[item.get("category", "Other")] += float(item.get("amount", 0))
    return dict(totals)


def show_summary(expenses):
    print("\n--- Spending summary ---")
    if not expenses:
        print("No expenses recorded.")
        return

    total = sum(float(item.get("amount", 0)) for item in expenses)
    print(f"Total spending: INR {total:,.2f}")
    print(f"Number of expenses: {len(expenses)}")

    print("\nCategory totals:")
    for category, amount in sorted(category_totals(expenses).items(),
                                   key=lambda pair: pair[1], reverse=True):
        print(f"  {category:<17} INR {amount:,.2f}")

    monthly = defaultdict(float)
    for item in expenses:
        month = item.get("date", "")[:7]
        monthly[month] += float(item.get("amount", 0))

    print("\nMonthly totals:")
    for month, amount in sorted(monthly.items()):
        print(f"  {month}: INR {amount:,.2f}")


def build_insights(expenses):
    """Generate useful local insights without sending data to an external service."""
    if not expenses:
        return ["Add some expenses first to generate insights."]

    total = sum(float(item.get("amount", 0)) for item in expenses)
    totals = category_totals(expenses)
    top_category = max(totals, key=totals.get)
    share = (totals[top_category] / total * 100) if total else 0

    insights = [
        f"Total recorded spending is INR {total:,.2f} across {len(expenses)} expense(s).",
        f"{top_category} is your highest-spending category at INR {totals[top_category]:,.2f} ({share:.1f}% of recorded spending)."
    ]

    monthly = defaultdict(float)
    for item in expenses:
        monthly[item.get("date", "")[:7]] += float(item.get("amount", 0))

    if monthly:
        highest_month = max(monthly, key=monthly.get)
        insights.append(
            f"Your highest-spending recorded month is {highest_month} "
            f"at INR {monthly[highest_month]:,.2f}."
        )

    if len(totals) > 1:
        lowest_category = min(totals, key=totals.get)
        insights.append(
            f"{lowest_category} is currently your lowest-spending category "
            f"at INR {totals[lowest_category]:,.2f}."
        )

    return insights


def make_ai_prompt(question, expenses):
    """Send only aggregated category/month totals, not descriptions or individual records."""
    categories = category_totals(expenses)
    months = defaultdict(float)
    for item in expenses:
        months[item.get("date", "")[:7]] += float(item.get("amount", 0))

    total = sum(float(item.get("amount", 0)) for item in expenses)
    safe_summary = {
        "currency": "INR",
        "total_spending": round(total, 2),
        "expense_count": len(expenses),
        "category_totals": {key: round(value, 2) for key, value in categories.items()},
        "monthly_totals": {key: round(value, 2) for key, value in sorted(months.items())}
    }

    return (
        "You are a cautious personal budgeting assistant. Analyze only the aggregated "
        "expense summary below. Give practical, non-judgmental observations. Do not "
        "claim to know income, savings, debts, or financial goals because they are not provided. "
        "Do not present advice as professional financial advice. If the data is insufficient, say so. "
        f"\n\nAggregated expense summary:\n{json.dumps(safe_summary, ensure_ascii=False)}"
        f"\n\nUser question: {question}"
    )



def ask_gemini(question, expenses):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("\nGemini API key not found. Set GEMINI_API_KEY to enable AI questions.")
        return

    prompt = make_ai_prompt(question, expenses)
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    payload = {
        "model": GEMINI_MODEL,
        "input": prompt
    }

    max_attempts = 4
    wait_times = [2, 4, 8]

    for attempt in range(max_attempts):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))

            answer_parts = []

            for step in result.get("steps", []):
                if step.get("type") == "model_output":
                    for item in step.get("content", []):
                        if item.get("type") == "text":
                            answer_parts.append(item.get("text", ""))

            answer = "\n".join(answer_parts).strip()

            print("\n--- AI Expense Assistant ---")
            print(answer or "The AI service did not return a text response.")
            return

        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")

            if error.code in (429, 500, 502, 503, 504) and attempt < max_attempts - 1:
                wait = wait_times[attempt]
                print(
                    f"Gemini is temporarily unavailable (HTTP {error.code}). "
                    f"Retrying in {wait} seconds..."
                )
                time.sleep(wait)
                continue

            print(f"\nGemini API error ({error.code}): {details[:800]}")
            return

        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt < max_attempts - 1:
                wait = wait_times[attempt]
                print(f"Connection problem. Retrying in {wait} seconds...")
                time.sleep(wait)
                continue

            print(f"\nCould not contact Gemini: {error}")
            return


def delete_expense(expenses):
    if not expenses:
        print("No expenses to delete.")
        return

    list_expenses(expenses)
    raw_id = input("\nEnter expense ID to delete: ").strip()
    if not raw_id.isdigit():
        print("Enter a valid numeric ID.")
        return

    expense_id = int(raw_id)
    for index, item in enumerate(expenses):
        if item.get("id") == expense_id:
            removed = expenses.pop(index)
            if save_expenses(expenses):
                print(f"Deleted: {removed.get('description', 'expense')}")
            return

    print("No expense found with that ID.")


def show_menu():
    print("\n" + "=" * 46)
    print("            AI EXPENSE ASSISTANT")
    print("=" * 46)
    print("1. Add expense")
    print("2. View all expenses")
    print("3. View spending summary")
    print("4. Get instant spending insights (offline)")
    print("5. Ask the AI assistant (Gemini API)")
    print("6. Delete an expense")
    print("7. Exit")
    print("=" * 46)


def main():
    expenses = load_expenses()
    print("Welcome to AI Expense Assistant.")
    print(f"Loaded {len(expenses)} saved expense(s).")
    print("Offline summaries work without an API key.")

    while True:
        show_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            list_expenses(expenses)
        elif choice == "3":
            show_summary(expenses)
        elif choice == "4":
            print("\n--- Spending insights ---")
            for insight in build_insights(expenses):
                print(f"- {insight}")
        elif choice == "5":
            if not expenses:
                print("Add expenses before asking the AI assistant.")
                continue
            question = input("What would you like to know about your spending? ").strip()
            if question:
                ask_gemini(question, expenses)
            else:
                print("Please enter a question.")
        elif choice == "6":
            delete_expense(expenses)
        elif choice == "7":
            print("Your expense records remain saved locally. Goodbye!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
