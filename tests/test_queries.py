import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.build_graph import build_kg
from src.queries import (
    products_by_brand_and_vendor,
    categories_by_vendor,
    vendors_by_brand,
    customers_by_brand,
    total_quantity_ordered,
    order_details,
    products_by_category
)

@pytest.fixture(scope="module")
def G():
    return build_kg()

def test_products_by_brand_and_vendor(G):
    res = products_by_brand_and_vendor(G, "B001", "V001")
    names = [r["product_name"] for r in res]
    assert "iPhone 15" in names
    assert "MacBook Pro" not in names

def test_categories_by_vendor(G):
    res = categories_by_vendor(G, "V001")
    names = [r["category_name"] for r in res]
    assert "Electronics" in names
    assert "Accessories" in names

def test_vendors_by_brand(G):
    res = vendors_by_brand(G, "B001")
    names = [r["vendor_name"] for r in res]
    assert "TechDistributors" in names
    assert "GlobalElectronics" in names

def test_customers_by_brand(G):
    res = customers_by_brand(G, "B001")
    names = [r["customer_name"] for r in res]
    assert "Alice Johnson" in names

def test_total_quantity_ordered(G):
    res = total_quantity_ordered(G, "P001")
    assert res[0]["total_quantity"] == 8

def test_order_details(G):
    res = order_details(G, "O001")
    assert len(res) == 2
    assert res[0]["customer_name"] == "Alice Johnson"
    products = {r["product_name"]: r["quantity"] for r in res}
    assert products["iPhone 15"] == 1
    assert products["Air Force 1"] == 2

def test_products_by_category(G):
    res = products_by_category(G, "C004")
    names = [r["product_name"] for r in res]
    assert "Air Force 1" in names
    assert "Air Max 270" in names

def test_empty_query_handling(G):
    # Non-existent node ID should safely return empty list without crashing
    assert products_by_brand_and_vendor(G, "NON_EXISTENT", "V001") == []
    assert vendors_by_brand(G, "NON_EXISTENT") == []
    assert order_details(G, "NON_EXISTENT") == []

def test_products_by_brand(G):
    from src.queries import products_by_brand
    res = products_by_brand(G, "B001")
    names = [r["product_name"] for r in res]
    assert "iPhone 15" in names
    assert "MacBook Pro" in names
    assert "iPad Air" in names
    assert "Apple Watch Series 9" in names
    assert "AirPods Pro" in names
    assert "Galaxy S23" not in names

def test_products_by_vendor(G):
    from src.queries import products_by_vendor
    res = products_by_vendor(G, "V001")
    names = [r["product_name"] for r in res]
    assert "iPhone 15" in names
    assert "Galaxy S23" in names

def test_entity_resolution():
    from src.pipeline import resolve_entity
    # Exact match (case insensitive)
    assert resolve_entity("brand", "apple") == "B001"
    assert resolve_entity("vendor", "TechDistributors") == "V001"
    assert resolve_entity("category", "footwear") == "C004"
    assert resolve_entity("product", "iPhone 15") == "P001"
    assert resolve_entity("order_id", "O001") == "O001"
    
    # None / null handling
    assert resolve_entity("vendor", None) is None
    assert resolve_entity("vendor", "none") is None
    assert resolve_entity("vendor", "null") is None
    
    # Fuzzy match with reasonable similarity (e.g. typos)
    assert resolve_entity("brand", "aple") == "B001"
    
    # Cross-entity mismatch prevention: "apple" must NEVER match "home appliances"
    with pytest.raises(ValueError):
        resolve_entity("category", "apple")
        
    # Unknown entity raises ValueError
    with pytest.raises(ValueError):
        resolve_entity("brand", "TeslaNonExistentBrand")


