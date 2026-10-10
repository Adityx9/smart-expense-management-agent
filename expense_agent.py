"""Transparent local spending agent with plan, action, evaluation, decision, and self-check."""
import json
from pathlib import Path
from copy import deepcopy

DATA_FILE = Path("expenses.json")
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"]
DEFAULT_BUDGETS = {"Food": 6000, "Transport": 2500, "Shopping": 4000, "Bills": 5000, "Health": 2500, "Entertainment": 2000, "Other": 3000}

CATEGORY_RULES = {
    "Food": ["restaurant", "lunch", "dinner", "breakfast", "cafe", "coffee", "grocery", "supermarket", "food", "pizza", "snack", "canteen"],
    "Transport": ["bus", "metro", "train", "taxi", "uber", "ola", "fuel", "petrol", "parking", "travel", "auto"],
    "Shopping": ["shopping", "shoes", "clothes", "amazon", "online order", "mall", "shirt", "dress", "electronics"],
    "Bills": ["electricity", "water bill", "internet", "wifi", "mobile recharge", "rent", "gas bill", "subscription", "phone bill"],
    "Health": ["pharmacy", "medicine", "doctor", "hospital", "clinic", "medical", "dentist"],
    "Entertainment": ["movie", "cinema", "game", "concert", "netflix", "spotify", "music", "theatre", "outing"],
}

def categorize(description):
    text = str(description or "").lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"

def load_expenses(path=DATA_FILE):
    path = Path(path)
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_expenses(expenses, path=DATA_FILE):
    Path(path).write_text(json.dumps(expenses, indent=2, ensure_ascii=False), encoding="utf-8")

class ExpenseAgent:
    def __init__(self, budgets=None):
        self.budgets = {**DEFAULT_BUDGETS, **(budgets or {})}

    def plan(self, expenses):
        return [
            {"step": 1, "action": "normalize_and_validate", "purpose": "Check fields and positive transaction amounts"},
            {"step": 2, "action": "complete_missing_categories", "purpose": "Use local rules only when user has not selected a category"},
            {"step": 3, "action": "measure_budget_utilization", "purpose": "Calculate spending and percentage of budget used"},
            {"step": 4, "action": "prioritize_risks_and_choose_action", "purpose": "Rank budget risks and select the most useful next action"},
            {"step": 5, "action": "self_evaluate", "purpose": "Check totals and category coverage"},
        ]

    def run(self, expenses):
        working = deepcopy(expenses)
        plan = self.plan(working)
        trace = [{"step": "Plan", "status": "complete", "details": f"Prepared {len(plan)} steps for {len(working)} transaction(s)."}]
        valid, invalid = [], 0
        for item in working:
            try:
                amount = round(float(item.get("amount", 0)), 2)
                description = str(item.get("description", "")).strip()
                if amount <= 0 or not description or not item.get("date"):
                    invalid += 1
                    continue
                item["amount"] = amount
                if item.get("category") not in CATEGORIES:
                    item["category"] = categorize(description)
                    item["category_source"] = "rule"
                else:
                    item.setdefault("category_source", "user")
                valid.append(item)
            except (TypeError, ValueError):
                invalid += 1
        trace.append({"step": "Act: validate + categorize", "status": "complete", "details": f"Kept {len(valid)} valid transaction(s); skipped {invalid}; filled missing categories only."})

        totals, counts = {}, {}
        for item in valid:
            cat = item["category"]
            totals[cat] = round(totals.get(cat, 0.0) + item["amount"], 2)
            counts[cat] = counts.get(cat, 0) + 1
        utilization, risk_assessment, over_budget = {}, [], []
        for cat, spent in totals.items():
            budget = float(self.budgets.get(cat, 0))
            pct = (spent / budget * 100) if budget > 0 else (100.0 if spent > 0 else 0.0)
            utilization[cat] = round(pct, 1)
            if spent > budget:
                over_budget.append(cat)
                risk_assessment.append(f"HIGH RISK — {cat}: {spent:,.2f} spent against a {budget:,.2f} budget ({pct:.0f}% used; over by {spent-budget:,.2f}).")
            elif budget > 0 and pct >= 80:
                risk_assessment.append(f"WATCH — {cat}: {pct:.0f}% of the {budget:,.2f} budget has been used.")
        trace.append({"step": "Evaluate: budget utilization", "status": "complete", "details": f"Calculated category totals and utilization for {len(totals)} category/categories."})

        if over_budget:
            priority = max(over_budget, key=lambda cat: totals[cat] - float(self.budgets.get(cat, 0)))
            next_action = f"Review {priority} first: spending is over budget by {totals[priority]-float(self.budgets.get(priority, 0)):,.2f}. Pause non-essential purchases in this category and review recent transactions."
        elif risk_assessment:
            watch_cats = [x for x in totals if self.budgets.get(x, 0) > 0 and totals[x] / self.budgets[x] >= .8]
            priority = max(watch_cats, key=lambda cat: totals[cat] / self.budgets[cat])
            next_action = f"Keep an eye on {priority}: it has used {utilization[priority]:.0f}% of its budget. Check the next few purchases before spending more."
        elif not valid:
            next_action = "Add at least one valid transaction, then run the agent to receive a budget assessment."
        else:
            next_action = "No budget intervention is needed yet. Keep recording expenses and run the agent again after your next purchase."
        trace.append({"step": "Decide: next action", "status": "complete", "details": next_action})

        total = round(sum(item["amount"] for item in valid), 2)
        category_total = round(sum(totals.values()), 2)
        checks = {
            "transaction_total_matches_category_total": abs(total - category_total) < 0.011,
            "every_valid_transaction_has_a_known_category": all(item.get("category") in CATEGORIES for item in valid),
            "all_processed_amounts_are_positive": all(item["amount"] > 0 for item in valid),
        }
        passed = all(checks.values())
        trace.append({"step": "Self-evaluate", "status": "passed" if passed else "failed", "details": str(checks)})
        recommendations = []
        for cat in sorted(totals, key=lambda c: utilization.get(c, 0), reverse=True):
            budget = float(self.budgets.get(cat, 0))
            spent = totals[cat]
            if spent > budget:
                recommendations.append(f"{cat}: over budget by ₹{spent-budget:,.2f}. Review non-essential expenses.")
            elif budget > 0 and spent / budget >= .8:
                recommendations.append(f"{cat}: {utilization[cat]:.0f}% of budget used. Monitor remaining purchases.")
            else:
                recommendations.append(f"{cat}: ₹{max(0, budget-spent):,.2f} remains from its budget.")
        if not recommendations:
            recommendations.append("No valid expenses to evaluate yet.")
        return {
            "expenses": working,
            "plan": plan,
            "summary": {
                "transactions_processed": len(valid),
                "invalid_transactions_skipped": invalid,
                "total_spending": total,
                "over_budget_categories": len(over_budget),
                "self_evaluation_passed": passed
            },
            "spending_by_category": totals,
            "budget_utilization_percent": utilization,
            "over_budget_categories": over_budget,
            "risk_assessment": risk_assessment,
            "next_action": next_action,
            "recommendations": recommendations,
            "self_evaluation": checks,
            "trace": trace
        }
