import tempfile
import unittest
from pathlib import Path
from expense_agent import ExpenseAgent, categorize, load_expenses, save_expenses

class ExpenseAgentTests(unittest.TestCase):
    def setUp(self):
        self.sample = [
            {"id": 1, "date": "2026-10-01", "description": "grocery supermarket", "amount": 1250, "category": "Food", "payment_method": "UPI"},
            {"id": 2, "date": "2026-10-02", "description": "bus travel", "amount": 500, "category": "Transport", "payment_method": "Cash"},
            {"id": 3, "date": "2026-10-03", "description": "movie tickets", "amount": 1800, "category": "Entertainment", "payment_method": "Card"},
        ]
    def test_categorization_rules(self):
        self.assertEqual(categorize("GROCERY store"), "Food")
        self.assertEqual(categorize("bus pass"), "Transport")
        self.assertEqual(categorize("unknown purchase"), "Other")
    def test_agent_totals_and_self_check(self):
        result = ExpenseAgent().run(self.sample)
        self.assertEqual(result["summary"]["transactions_processed"], 3)
        self.assertEqual(result["summary"]["total_spending"], 3550.0)
        self.assertTrue(result["summary"]["self_evaluation_passed"])
    def test_user_selected_category_is_preserved(self):
        data = [{"id": 1, "date": "2026-10-01", "description": "grocery", "amount": 100, "category": "Shopping", "payment_method": "UPI"}]
        result = ExpenseAgent().run(data)
        self.assertEqual(result["expenses"][0]["category"], "Shopping")
    def test_over_budget_triggers_action(self):
        data = [{"id": 1, "date": "2026-10-01", "description": "shopping shoes", "amount": 5000, "category": "Shopping", "payment_method": "Card"}]
        result = ExpenseAgent({"Shopping": 1000}).run(data)
        self.assertIn("Shopping", result["next_action"])
        self.assertEqual(result["summary"]["over_budget_categories"], 1)
    def test_invalid_record_skipped(self):
        data = self.sample + [{"id": 4, "date": "2026-10-04", "description": "", "amount": -2, "category": "Other", "payment_method": "Cash"}]
        result = ExpenseAgent().run(data)
        self.assertEqual(result["summary"]["invalid_transactions_skipped"], 1)
    def test_json_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "expenses.json"
            save_expenses(self.sample, path)
            self.assertEqual(len(load_expenses(path)), 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)
