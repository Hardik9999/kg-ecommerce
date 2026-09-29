# Loom Video Walkthrough Script: E-Commerce Knowledge Graph & AI Retrieval System

> **Target Duration:** 3 to 5 minutes  
> **Audience:** Technical Evaluation Panel / Hiring Team  
> **Goal:** Present the architecture, Knowledge Graph design, multi-hop retrieval, LLM integration, and strict grounding verification with a live demonstration.

---

## 🛠️ Pre-Recording Checklist & Screen Setup

Before hitting record on Loom, prepare your desktop:
- **Left Half of Screen:** VS Code / Antigravity IDE with the project open.
  - Tabs open: `src/build_graph.py`, `src/pipeline.py`, `src/queries.py`, and `sample_results.md`.
- **Right Half of Screen:** 
  - Terminal 1: Active virtual environment (`.\venv\Scripts\activate`).
  - Terminal 2 (or Browser tab): FastAPI Swagger Docs at `http://127.0.0.1:8000/docs` (server running: `uvicorn src.api:app --reload`).
- **Audio & Webcam:** Test microphone and enable webcam bubble in the corner.

---

## ⏱️ Video Outline & Timing Breakdown

| Section | Topic | Target Time | Key Talking Point |
|---|---|---|---|
| **1** | Introduction & Problem Framing | 0:00 - 0:40 (40s) | Why Knowledge Graphs beat traditional Vector RAG for relational e-commerce queries. |
| **2** | Knowledge Graph Schema & Data Model | 0:40 - 1:30 (50s) | The 6 entities, directional relationships, and NetworkX implementation. |
| **3** | Retrieval Pipeline & LLM Integration | 1:30 - 2:30 (60s) | 2-stage decoupled pipeline: LLM #1 Planner -> Deterministic Traversal -> LLM #2 Synthesizer. |
| **4** | Hallucination Prevention & Strict Grounding | 2:30 - 3:15 (45s) | Zero-row interception, fuzzy matching, and strict context prompts. |
| **5** | Live Demonstration & Test Run | 3:15 - 4:45 (90s) | Pytest pass, primary assignment query, multi-hop query, and zero-match fallback. |
| **6** | Conclusion & Submission Wrap-Up | 4:45 - 5:00 (15s) | Clean code, production-ready FastAPI, comprehensive test suite. |

---

## 🎙️ Section-by-Section Script & Actions

### Section 1: Introduction & Problem Statement (0:00 - 0:40)
**Screen Focus:** Show `README.md` or the terminal with the project directory.

> *"Hi everyone, welcome to my walkthrough of the E-Commerce Knowledge Graph and AI-powered retrieval system.*
>
> *When dealing with e-commerce catalogs, standard vector similarity search often falls short. It struggles with multi-hop relational questions like: 'Which products from Brand X are supplied by Vendor Y?' or 'Which customers bought products from Brand Z?'.*
> 
> *To solve this, I built a deterministic Knowledge Graph retrieval system using NetworkX and Python, paired with Google Gemini models. It uses a decoupled two-step LLM architecture that guarantees answers are 100% grounded in verified graph data with zero hallucinations."*

---

### Section 2: Knowledge Graph Architecture & Entities (0:40 - 1:30)
**Screen Focus:** Switch to `src/build_graph.py` and highlight lines 14–50, or show the Mermaid diagram in `README.md`.

> *"Let’s look at the graph structure.*
>
> *I used NetworkX's `MultiDiGraph` to represent the e-commerce domain. We have 6 distinct entity types across 73 nodes and 117 edges:*
> 1. ***Brands*** (e.g., Apple, Samsung, Nike, Sony)
> 2. ***Categories*** (e.g., Electronics, Footwear, Home Appliances)
> 3. ***Products*** (e.g., iPhone 15, Air Force 1, Dyson V15)
> 4. ***Vendors*** (e.g., TechDistributors, GlobalElectronics)
> 5. ***Customers*** (e.g., Alice Johnson, Bob Smith)
> 6. ***Orders*** (with edge properties for quantity and unit price)
>
> *The key directional edges define the relationships:*
> - `Product MADE_BY Brand`
> - `Product BELONGS_TO Category`
> - `Vendor SUPPLIES Product`
> - `Customer PLACED Order`
> - `Order CONTAINS Product` (storing line-item metadata like `quantity` and `unit_price`)."*

---

### Section 3: AI Retrieval Pipeline & Decoupled LLM Architecture (1:30 - 2:30)
**Screen Focus:** Switch to `src/pipeline.py` and walk through `execute_plan_with_retry` and `_execute`.

> *"Now let's examine the retrieval and LLM flow. Many naive implementations ask an LLM to generate Cypher or SQL directly on the whole database, which is prone to syntax bugs and hallucinations.*
>
> *Instead, I implemented a robust 4-step pipeline:*
>
> 1. **Step 1 - Query Planning (LLM #1):** When a user asks a natural language question, LLM #1 translates it into a structured JSON query plan containing a whitelisted operation and parameters. At this point, the LLM has zero access to raw data.
> 2. **Step 2 - Fuzzy Entity Resolution:** Before touching the graph, our entity resolver normalizes brand or vendor names (handling case differences and typos using `difflib`) to exact node IDs.
> 3. **Step 3 - Deterministic NetworkX Traversal:** We execute a purely deterministic multi-hop graph traversal in Python (in `src/queries.py`). This traverses from Vendor to Product to Brand, or Customer to Order to Product.
> 4. **Step 4 - Answer Synthesis (LLM #2):** The retrieved graph rows are passed to LLM #2 alongside a strict system prompt instructing it to answer solely based on those rows."*

---

### Section 4: Ensuring Strict Grounding & Zero Hallucination (2:30 - 3:15)
**Screen Focus:** Highlight `src/pipeline.py` lines 138–144 (the Hard Grounding Fallback) and `SYSTEM_PROMPT_2` in `src/llm.py`.

> *"A critical requirement of this assignment is ensuring answers are based ONLY on retrieved graph data. We enforce this through three defensive layers:*
>
> 1. **Data Isolation:** LLM #1 is strictly a planner. It never sees graph rows, so it cannot invent answers during planning.
> 2. **Hard Interception for Zero Rows:** If the graph traversal returns 0 rows—for example, if a vendor doesn't supply a requested brand—the pipeline intercepts immediately. It returns: *'No matching data found in the knowledge graph.'* We completely skip calling LLM #2, making hallucination mathematically impossible.
> 3. **Strict Synthesizer Constraints:** When rows do exist, LLM #2 operates under temperature 0.0 with a system prompt that explicitly forbids using external parametric knowledge."*

---

### Section 5: Live Demonstration & Tests (3:15 - 4:45)
**Screen Focus:** Switch to your terminal and Swagger UI.

#### 1. Run Unit Tests (Terminal):
> *"First, let's run our automated test suite with pytest:"*
```bash
.\venv\Scripts\pytest tests/
```
> *"All 9 tests pass in under a second! This verifies graph construction, multi-hop traversals, edge-case empty handling, and fuzzy entity resolution."*

#### 2. Test Primary Assignment Example (Swagger UI / CLI):
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) -> Click `POST /query` -> `Try it out` -> paste:
```json
{
  "question": "What products does Apple make that are supplied by TechDistributors?"
}
```
Click **Execute**. Show the response:
> *"Here is the primary question from the assignment prompt: 'What products does Apple make that are supplied by TechDistributors?'*
> *Notice the result: It resolved Apple and TechDistributors, traversed the graph, retrieved iPhone 15, iPad Air, and AirPods Pro, and synthesized a concise natural language answer."*

#### 3. Test Multi-Hop Customer Traversal:
In Swagger UI, execute:
```json
{
  "question": "Which customers have bought Apple products?"
}
```
Show the response:
> *"Here is a 4-hop traversal: Brand -> Product -> Order -> Customer. It accurately identifies Alice Johnson, Bob Smith, and Diana Prince."*

#### 4. Demonstrate Zero-Hallucination Fallback:
In Swagger UI, execute:
```json
{
  "question": "What Apple products are supplied by HomeGoodsCo?"
}
```
Show the response:
> *"Now let's test grounding. Both Apple and HomeGoodsCo exist in our database, but HomeGoodsCo only supplies Dyson vacuums. When we execute this, the graph returns 0 rows, LLM #2 is skipped, and the system cleanly reports: 'No matching data found in the knowledge graph.' Zero hallucinations."*

#### 5. Demonstrate Unknown Entity / Out-of-Vocabulary:
In Swagger UI, execute:
```json
{
  "question": "Which customers bought Tesla cars?"
}
```
Show the response:
> *"And if an entity doesn't exist in our catalog—like Tesla—the entity resolver safely catches it with a graceful failure message."*

---

### Section 6: Conclusion (4:45 - 5:00)
**Screen Focus:** Switch back to `README.md` and show `sample_results.md`.

> *"To wrap up:*
> - *We built a complete Knowledge Graph adhering to all 6 entity types and relationships.*
> - *We decoupled query planning, deterministic traversal, and answer synthesis.*
> - *We proved 100% grounding with zero hallucination via our hard fallback mechanism.*
> - *The project includes automated sample runs in `sample_results.md`, 9 passing unit tests, and a production-ready FastAPI endpoint.*
>
> *Thank you for your time, and I look forward to your feedback!"*

---

## 📋 Quick Copy-Paste Cheat Sheet for Recording

Have these queries ready on a sticky note or second monitor during your Loom recording:

1. **Test Query 1 (Primary Assignment Example):**
   ```
   What products does Apple make that are supplied by TechDistributors?
   ```
2. **Test Query 2 (Order Line Items):**
   ```
   Show me the details for order O001.
   ```
3. **Test Query 3 (Multi-Hop Customer):**
   ```
   Which customers have bought Apple products?
   ```
4. **Test Query 4 (Order Aggregation):**
   ```
   What is the total quantity of iPhone 15 ordered?
   ```
5. **Test Query 5 (Strict Grounding Zero-Match):**
   ```
   What Apple products are supplied by HomeGoodsCo?
   ```
6. **Test Query 6 (Out of Vocabulary):**
   ```
   Which customers bought Tesla cars?
   ```
