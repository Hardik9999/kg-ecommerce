import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT_1 = """You are an AI assistant that translates natural language questions into structured queries against an e-commerce knowledge graph.

The graph has the following nodes and edge types:
- Product -[MADE_BY]-> Brand
- Product -[BELONGS_TO]-> Category
- Vendor -[SUPPLIES]-> Product
- Customer -[PLACED]-> Order
- Order -[CONTAINS {quantity, unit_price}]-> Product

You must output a JSON object with exactly two keys: "op" and "params".
The "op" must be one of the following operations:
1. "products_by_brand_and_vendor" (params: "brand", "vendor")
2. "categories_by_vendor" (params: "vendor")
3. "vendors_by_brand" (params: "brand")
4. "customers_by_brand" (params: "brand")
5. "total_quantity_ordered" (params: "product")
6. "order_details" (params: "order_id")
7. "products_by_category" (params: "category")

The "params" must be a dictionary matching the operation's required arguments. 
Use the exact names mentioned in the question for the parameters.

Examples:
Q: What products does Apple make that are supplied by TechDistributors?
{"op": "products_by_brand_and_vendor", "params": {"brand": "Apple", "vendor": "TechDistributors"}}

Q: Show me the details for order O001.
{"op": "order_details", "params": {"order_id": "O001"}}

Q: Which customers have bought Samsung products?
{"op": "customers_by_brand", "params": {"brand": "Samsung"}}
"""

SYSTEM_PROMPT_2 = """You are a strict data-reporting assistant.
Answer the user's question ONLY using the provided retrieved data.
Do not use outside knowledge. 
If the retrieved data is empty, you must reply exactly: "No matching data found in the knowledge graph."
If the data is provided, formulate a natural language answer based on it.
"""

model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite")

import time
from src.logger import get_logger

logger = get_logger("kg_llm")

def _call_gemini(contents, response_mime_type=None):

    candidate_models = [
        model_name,
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash"
    ]



    seen = set()
    models_to_try = []
    for m in candidate_models:
        if m and m not in seen:
            seen.add(m)
            models_to_try.append(m)

    last_err = None
    for m in models_to_try:
        for attempt in range(2):
            try:
                t0 = time.time()
                config_kwargs = {
                    "temperature": 0.0,
                    "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True)
                }
                if response_mime_type:
                    config_kwargs["response_mime_type"] = response_mime_type

                response = client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_kwargs)
                )
                logger.debug("Gemini model '%s' responded in %.2fs", m, time.time() - t0)
                return response.text
            except Exception as e:
                last_err = e
                logger.warning("Call to model '%s' failed (%s). Retrying / falling over...", m, str(e)[:120])
                time.sleep(1.0)
                continue

    raise last_err

def generate_query_plan(question, error_message=None):
    prompt = SYSTEM_PROMPT_1 + f"\n\nQuestion: {question}"
    if error_message:
        prompt += f"\n\nYour previous attempt failed with error: {error_message}. Please fix the query plan and output a valid JSON."
    return _call_gemini(prompt, response_mime_type="application/json")

def answer_from_rows(question, rows):
    prompt = SYSTEM_PROMPT_2 + f"\n\nQuestion: {question}\n\nRetrieved Data:\n{str(rows)}"
    return _call_gemini(prompt)
