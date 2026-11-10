# AI Expense Assistant

A Python command-line mini project that combines local expense tracking, offline spending insights, and optional Gemini-powered natural-language analysis.

## Features

- Add, list and delete expense records
- View total, category-wise and monthly spending
- Generate instant local insights without an internet connection
- Ask Gemini questions about aggregated spending summaries (optional)
- Store expense records locally in `expenses.json`

## Requirements

- Python 3.10+
- No third-party packages required for the core application
- A Gemini API key only if you want to use the optional AI question feature

## Run the application

```powershell
py ai_expense_assistant.py
```

Or:

```powershell
python ai_expense_assistant.py
```

## Enable the Gemini feature (optional)

1. Create an API key through Google AI Studio: https://aistudio.google.com/app/apikey
2. In PowerShell, set the key for the current terminal session:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

3. Start the application in the same terminal:

```powershell
py ai_expense_assistant.py
```

The application reads the key from the environment. Do not paste your key into the Python source code, README, screenshots, GitHub, or chat.

Optional model override:

```powershell
$env:GEMINI_MODEL="gemini-2.5-flash"
```

## Privacy

- Expense records are stored locally in `expenses.json`.
- The offline insights feature does not send data anywhere.
- When you choose the Gemini feature, the app sends only aggregated totals by category and month, total spending and expense count. It does not send individual descriptions or dates for each record.
- Do not enter sensitive personal information in expense descriptions.
- Review Google's API terms and privacy settings before using an external AI service.

## Project structure

```text
AI-Expense-Assistant/
├── ai_expense_assistant.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Concepts demonstrated

- Python functions, loops and conditional statements
- Lists and dictionaries
- JSON file handling
- Exception handling
- Data aggregation
- HTTP requests to an AI API
- Environment variables for API-key management

## Important note

This is an educational budgeting helper, not a financial adviser. Its observations are based only on expenses entered by the user.
