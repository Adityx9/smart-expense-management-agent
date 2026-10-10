# SpendSmart — Smart Expense Management Agent

A dark-themed website-style local expense manager with a purposeful agent loop. No AI API key, no LLM, and no application calls to external APIs.

## What's new
- Select the category while entering each expense.
- User-selected categories are preserved; rules only fill in missing/invalid categories.
- Agent computes budget utilization, flags watch/high-risk categories, prioritizes the largest budget overrun, chooses a specific next action, and runs consistency checks.
- Improved dark dashboard, budget progress bars, transaction editor, and report download.

## Run (Windows)
Extract the ZIP, open Command Prompt in the extracted folder, then run:

```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open `http://localhost:8501`.

## Test the agent without the website

```bash
python -m unittest -v test_agent.py
```

## How agentic behavior is demonstrated
1. **Plan:** creates an explicit ordered plan for processing.
2. **Act:** validates transactions and categorizes only when no valid user-selected category exists.
3. **Evaluate:** computes category totals and budget utilization.
4. **Decide:** ranks budget risk and selects a next action based on current results.
5. **Self-evaluate:** checks total consistency, category coverage, and positive amounts.

It is a transparent deterministic agent, not a generative LLM. Its actions and recommendations are reproducible for the same input.

## Files
- `app.py`: Streamlit interface
- `expense_agent.py`: agent planning/action/evaluation logic
- `schema.json`: JSON Schema for report shape
- `test_agent.py`: automated unit tests
- `REPORT.md`: assignment report
- `requirements.txt`: required Python packages
- `.gitignore`: excludes local data and virtual environment

## Data and privacy
Expenses and budgets are stored locally as `expenses.json`, `budgets.json`, and `monthly_finance.json`. These are ignored by Git. Do not upload real personal financial data to a public repository.


## Demo for assessment
1. Load demo transactions in Transactions.
2. Show category selection in Add expense.
3. Set a small budget for one category in the sidebar and save.
4. Run the agent. Show the risk assessment and chosen next action.
5. Show the self-evaluation checks and execution trace.
6. Run the test suite and open `REPORT.md`.

## Monthly income, investments, and savings

The sidebar stores monthly income, planned investments, and savings by reporting month in `monthly_finance.json`. Income is the overall monthly cap. The Overview tab shows a percentage-labeled pie chart for spending, investments, and savings. Category progress bars are calculated as spending divided by that category's configured limit; when no category limit is set, income is used as the fallback denominator.

The Agent Cockpit analyzes only expenses whose date matches the selected reporting month. It also compares spending plus investments and savings against that month's income.
