# Project Report — SpendSmart: Smart Expense Management Agent

## Objective
Build a local-first expense management website that records categorized spending, checks category budgets, identifies risks, and selects an appropriate next action without requiring a paid AI API or external service.

## Problem
Automatic category prediction can be wrong for ambiguous merchant descriptions. Users need direct control over categories and useful feedback about budget risks rather than only a transaction list.

## Solution
The interface lets the user select a category for every expense and enter monthly income, investments, and savings. The deterministic agent preserves that choice and uses keyword rules only for records whose category is missing or invalid. It aggregates spending, calculates budget utilization, prioritizes budget overruns, and proposes an action.

## Agent architecture
```text
User -> Streamlit UI -> Local JSON files -> ExpenseAgent
                                        1. Plan
                                        2. Validate and act
                                        3. Evaluate budget utilization
                                        4. Decide next action
                                        5. Self-evaluate
                                           |
                                           v
                        Risk assessment + recommendations + trace
```

## Agentic loop
- **Planning:** create an explicit list of processing steps.
- **Action:** validate fields, skip invalid records, and fill only missing categories using local keyword rules.
- **Evaluation:** aggregate category spending and compare it with user-configured limits.
- **Decision:** if over budget, prioritize the category with the largest monetary overrun; otherwise warn when a category has used at least 80% of its budget; if no risk exists, recommend continued tracking.
- **Self-evaluation:** check that category totals equal total spending, all valid transactions have known categories, and all processed amounts are positive.
- **Feedback:** show a chosen next action, risk messages, category recommendations, and execution trace.

## Interface
The website has Overview, Add Expense, Agent Cockpit, and Transactions tabs. The Overview shows a three-color pie chart with percentages for spending, investments, and savings. Category progress bars are calculated from actual spent-to-limit ratios. The agent cockpit filters expenses to the selected month and compares total allocation against monthly income. Users can configure budgets, add transactions with explicit categories, edit transaction categories, view charts, and download a JSON report.

## Technologies
Python, Streamlit, Pandas, JSON local storage, Python unittest, and JSON Schema.

## Testing
Six unit tests cover category rules, total aggregation and self-checks, preservation of user-selected categories, budget-overrun action selection, invalid-record handling, and JSON round-tripping. Run `python -m unittest -v test_agent.py`.

## Privacy and limitations
The application does not call external APIs or require AI credentials. It stores data locally. Rule-based fallback categorization is limited by its keyword dictionary, so the user-selected category is the preferred source of truth. The prototype is for education and is not professional financial advice.
