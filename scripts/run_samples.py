import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import execute_plan_with_retry

QUESTIONS = [
    {
        "category": "Multi-Hop Traversal (Assignment Primary Example)",
        "question": "What products does Apple make that are supplied by TechDistributors?",
        "notes": "Traverses Vendor -> SUPPLIES -> Product -> MADE_BY -> Brand."
    },
    {
        "category": "Order Line-Item Breakdown",
        "question": "Show me the details for order O001.",
        "notes": "Retrieves Customer -> PLACED -> Order -> CONTAINS -> Products with quantities and unit prices."
    },
    {
        "category": "Customer Multi-Hop Purchasing Traversal",
        "question": "Which customers have bought Apple products?",
        "notes": "Traverses Brand <- MADE_BY <- Product <- CONTAINS <- Order <- PLACED <- Customer."
    },
    {
        "category": "Order Quantity Aggregation",
        "question": "What is the total quantity of iPhone 15 ordered?",
        "notes": "Aggregates 'quantity' property across all CONTAINS edges incoming to the product node."
    },
    {
        "category": "Category Classification",
        "question": "List all products in the Footwear category.",
        "notes": "Traverses Category <- BELONGS_TO <- Product."
    },
    {
        "category": "Supplier Lookup",
        "question": "Which vendors supply Apple products?",
        "notes": "Traverses Brand <- MADE_BY <- Product <- SUPPLIES <- Vendor."
    },
    {
        "category": "Grounding Test (Zero-Match Fallback)",
        "question": "What Apple products are supplied by SportSupplies Co?",
        "notes": "Both entities exist in the graph, but SportSupplies Co does not supply Apple products. Tests hard fallback intercepting 0 rows with zero hallucinations."
    },
    {
        "category": "Grounding Test (Out-of-Vocabulary Entity)",
        "question": "Which customers bought Tesla cars?",
        "notes": "Tesla does not exist in the dataset. Tests the fuzzy resolver rejecting unknown entities gracefully."
    }
]

def run_samples():
    output = "# Sample Queries and System Results\n\n"
    output += "This document demonstrates the E-Commerce Knowledge Graph retrieval pipeline.\n"
    output += "For each sample, it presents:\n"
    output += "1. **API Response (`POST /query`)**: The clean, industry-standard JSON format returned to frontend/API clients.\n"
    output += "2. **Internal Grounding Architecture**: The generated query plan (LLM #1), raw retrieved graph rows (deterministic NetworkX traversal), and grounding validation.\n\n"
    output += "---\n\n"
    
    for i, item in enumerate(QUESTIONS, 1):
        q = item["question"]
        print(f"Running sample {i}/{len(QUESTIONS)}: {q}")
        result = execute_plan_with_retry(q)
        
        answer = result.get("answer", "")
        rows = result.get("rows", [])
        plan = result.get("plan", "")
        is_success = not answer.startswith("Graceful failure:")
        
        api_response = {
            "success": is_success,
            "answer": answer,
            "rows": rows
        }
        
        output += f"## Sample {i}: {item['category']}\n\n"
        output += f"**Question:** *\"{q}\"*\n\n"
        output += f"**Context / Traversal:** {item['notes']}\n\n"
        output += "### 1. API Response (`POST /query`)\n"
        output += "```json\n"
        output += json.dumps(api_response, indent=2) + "\n"
        output += "```\n\n"
        output += "### 2. Internal Execution Details\n"
        output += "- **Generated Plan (LLM #1):**\n"
        output += "  ```json\n  " + plan.replace("\n", "\n  ") + "\n  ```\n"
        output += f"- **Retrieved Rows ({len(rows)} record{'s' if len(rows) != 1 else ''}):**\n"
        output += "  ```json\n  " + json.dumps(rows, indent=2).replace("\n", "\n  ") + "\n  ```\n\n"
        output += "---\n\n"
        time.sleep(1.0)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, '..', 'sample_results.md')
    with open(out_path, "w", encoding='utf-8') as f:
        f.write(output)
        
    print(f"Done! Results written to {out_path}")

if __name__ == "__main__":
    run_samples()
