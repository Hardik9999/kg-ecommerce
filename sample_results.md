# Sample Queries and System Results

This document demonstrates the E-Commerce Knowledge Graph retrieval pipeline.
For each sample, it presents:
1. **API Response (`POST /query`)**: The clean, industry-standard JSON format returned to frontend/API clients.
2. **Internal Grounding Architecture**: The generated query plan (LLM #1), raw retrieved graph rows (deterministic NetworkX traversal), and grounding validation.

---

## Sample 1: Multi-Hop Traversal (Assignment Primary Example)

**Question:** *"What products does Apple make that are supplied by TechDistributors?"*

**Context / Traversal:** Traverses Vendor -> SUPPLIES -> Product -> MADE_BY -> Brand.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "Apple products supplied by TechDistributors include the iPhone 15, iPad Air, and AirPods Pro.",
  "rows": [
    {
      "product_name": "iPhone 15"
    },
    {
      "product_name": "iPad Air"
    },
    {
      "product_name": "AirPods Pro"
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "products_by_brand_and_vendor",
    "params": {
      "brand": "Apple",
      "vendor": "TechDistributors"
    }
  }
  ```
- **Retrieved Rows (3 records):**
  ```json
  [
    {
      "product_name": "iPhone 15"
    },
    {
      "product_name": "iPad Air"
    },
    {
      "product_name": "AirPods Pro"
    }
  ]
  ```

---

## Sample 2: Order Line-Item Breakdown

**Question:** *"Show me the details for order O001."*

**Context / Traversal:** Retrieves Customer -> PLACED -> Order -> CONTAINS -> Products with quantities and unit prices.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "Order O001 was placed by Alice Johnson and includes the following items:\n* 1 iPhone 15 at a unit price of $999.00\n* 2 pairs of Air Force 1s at a unit price of $100.00 each",
  "rows": [
    {
      "customer_name": "Alice Johnson",
      "product_name": "iPhone 15",
      "quantity": 1,
      "unit_price": 999.0
    },
    {
      "customer_name": "Alice Johnson",
      "product_name": "Air Force 1",
      "quantity": 2,
      "unit_price": 100.0
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "order_details",
    "params": {
      "order_id": "O001"
    }
  }
  ```
- **Retrieved Rows (2 records):**
  ```json
  [
    {
      "customer_name": "Alice Johnson",
      "product_name": "iPhone 15",
      "quantity": 1,
      "unit_price": 999.0
    },
    {
      "customer_name": "Alice Johnson",
      "product_name": "Air Force 1",
      "quantity": 2,
      "unit_price": 100.0
    }
  ]
  ```

---

## Sample 3: Customer Multi-Hop Purchasing Traversal

**Question:** *"Which customers have bought Apple products?"*

**Context / Traversal:** Traverses Brand <- MADE_BY <- Product <- CONTAINS <- Order <- PLACED <- Customer.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "The customers who have bought Apple products are Diana Prince, Charlie Davis, Bob Smith, Alice Johnson, and Fiona Gallagher.",
  "rows": [
    {
      "customer_name": "Diana Prince"
    },
    {
      "customer_name": "Charlie Davis"
    },
    {
      "customer_name": "Bob Smith"
    },
    {
      "customer_name": "Alice Johnson"
    },
    {
      "customer_name": "Fiona Gallagher"
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "customers_by_brand",
    "params": {
      "brand": "Apple"
    }
  }
  ```
- **Retrieved Rows (5 records):**
  ```json
  [
    {
      "customer_name": "Diana Prince"
    },
    {
      "customer_name": "Charlie Davis"
    },
    {
      "customer_name": "Bob Smith"
    },
    {
      "customer_name": "Alice Johnson"
    },
    {
      "customer_name": "Fiona Gallagher"
    }
  ]
  ```

---

## Sample 4: Order Quantity Aggregation

**Question:** *"What is the total quantity of iPhone 15 ordered?"*

**Context / Traversal:** Aggregates 'quantity' property across all CONTAINS edges incoming to the product node.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "The total quantity of iPhone 15 ordered is 8.",
  "rows": [
    {
      "product_name": "iPhone 15",
      "total_quantity": 8
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {"op": "total_quantity_ordered", "params": {"product": "iPhone 15"}}
  ```
- **Retrieved Rows (1 record):**
  ```json
  [
    {
      "product_name": "iPhone 15",
      "total_quantity": 8
    }
  ]
  ```

---

## Sample 5: Category Classification

**Question:** *"List all products in the Footwear category."*

**Context / Traversal:** Traverses Category <- BELONGS_TO <- Product.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "The products in the Footwear category are Air Force 1, Air Max 270, Ultraboost 1.0, and Stan Smith.",
  "rows": [
    {
      "product_name": "Air Force 1"
    },
    {
      "product_name": "Air Max 270"
    },
    {
      "product_name": "Ultraboost 1.0"
    },
    {
      "product_name": "Stan Smith"
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {"op": "products_by_category", "params": {"category": "Footwear"}}
  ```
- **Retrieved Rows (4 records):**
  ```json
  [
    {
      "product_name": "Air Force 1"
    },
    {
      "product_name": "Air Max 270"
    },
    {
      "product_name": "Ultraboost 1.0"
    },
    {
      "product_name": "Stan Smith"
    }
  ]
  ```

---

## Sample 6: Supplier Lookup

**Question:** *"Which vendors supply Apple products?"*

**Context / Traversal:** Traverses Brand <- MADE_BY <- Product <- SUPPLIES <- Vendor.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "The vendors that supply Apple products are GlobalElectronics and TechDistributors.",
  "rows": [
    {
      "vendor_name": "GlobalElectronics"
    },
    {
      "vendor_name": "TechDistributors"
    }
  ]
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "vendors_by_brand",
    "params": {
      "brand": "Apple"
    }
  }
  ```
- **Retrieved Rows (2 records):**
  ```json
  [
    {
      "vendor_name": "GlobalElectronics"
    },
    {
      "vendor_name": "TechDistributors"
    }
  ]
  ```

---

## Sample 7: Grounding Test (Zero-Match Fallback)

**Question:** *"What Apple products are supplied by SportSupplies Co?"*

**Context / Traversal:** Both entities exist in the graph, but SportSupplies Co does not supply Apple products. Tests hard fallback intercepting 0 rows with zero hallucinations.

### 1. API Response (`POST /query`)
```json
{
  "success": true,
  "answer": "No matching data found in the knowledge graph.",
  "rows": []
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "products_by_brand_and_vendor",
    "params": {
      "brand": "Apple",
      "vendor": "SportSupplies Co"
    }
  }
  ```
- **Retrieved Rows (0 records):**
  ```json
  []
  ```

---

## Sample 8: Grounding Test (Out-of-Vocabulary Entity)

**Question:** *"Which customers bought Tesla cars?"*

**Context / Traversal:** Tesla does not exist in the dataset. Tests the fuzzy resolver rejecting unknown entities gracefully.

### 1. API Response (`POST /query`)
```json
{
  "success": false,
  "answer": "Graceful failure: Could not understand or map query. Error: Could not resolve 'Tesla' to any known Brand.",
  "rows": []
}
```

### 2. Internal Execution Details
- **Generated Plan (LLM #1):**
  ```json
  {
    "op": "customers_by_brand",
    "params": {
      "brand": "Tesla"
    }
  }
  ```
- **Retrieved Rows (0 records):**
  ```json
  []
  ```

---

