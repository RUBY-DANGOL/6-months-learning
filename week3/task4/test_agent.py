"""Test the SQL Agent directly (without FastAPI)."""
import json
from app.agent import process_question

TEST_QUESTIONS = [
    "How many shipped orders are from USA customers?",
    "Get employees with office city",
    "Count customers per country",
    "List all products",
    "Show all orders from customers in Germany",
    "What is the total amount of payments received?",
    "Find customers in France",
    "How many products are in each product line?",
]

for q in TEST_QUESTIONS:
    print("\n" + "=" * 80)
    print(f"QUESTION: {q}")
    print("=" * 80)
    result = process_question(q)
    print("\nRESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n" + "-" * 80)
