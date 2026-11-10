# Personal Expense Tracker

A beginner-friendly Python command-line application for recording and reviewing personal expenses.

## Features

- Add expenses with date, category, amount and description
- View all saved expenses
- Calculate total spending
- View category-wise spending
- Delete an expense by its ID
- Persist records in a local `expenses.json` file

## Requirements

- Python 3.10 or later
- No third-party packages required

## How to run

1. Download or clone this repository.
2. Open the project folder in VS Code.
3. Open the terminal in that folder.
4. Run:

```bash
python expense_tracker.py
```

On Windows, if `python` is not recognized, try:

```powershell
py expense_tracker.py
```

## Data storage

The application automatically creates `expenses.json` in the same folder when the first expense is saved. Keep this file if you want to retain your records. It is excluded from Git by `.gitignore` so personal spending data is not accidentally uploaded.

## Categories

Food, Travel, Shopping, Bills, Education, Health, Entertainment and Other.

## Project structure

```text
Expense-Tracker-Python-Mini-Project/
├── expense_tracker.py
├── README.md
└── .gitignore
```

## Concepts used

- Variables and data types
- Conditional statements and loops
- Functions
- Lists and dictionaries
- Exception handling
- File handling with JSON
- Date validation
