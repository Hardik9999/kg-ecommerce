def products_by_brand(G, brand=None, brand_id=None):
    brand_id = brand if brand is not None else brand_id
    if not brand_id or brand_id not in G:
        return []
    results = []
    for pu, pv, data in G.in_edges(brand_id, data=True):
        if data.get('type') == 'MADE_BY':
            results.append({"product_name": G.nodes[pu]['name']})
    return results

def products_by_vendor(G, vendor=None, vendor_id=None):
    vendor_id = vendor if vendor is not None else vendor_id
    if not vendor_id or vendor_id not in G:
        return []
    results = []
    for u, v, data in G.out_edges(vendor_id, data=True):
        if data.get('type') == 'SUPPLIES':
            results.append({"product_name": G.nodes[v]['name']})
    return results

def products_by_brand_and_vendor(G, brand=None, vendor=None, brand_id=None, vendor_id=None):
    brand_id = brand if brand is not None else brand_id
    vendor_id = vendor if vendor is not None else vendor_id
    if not brand_id and not vendor_id:
        return []
    if brand_id and not vendor_id:
        return products_by_brand(G, brand_id=brand_id)
    if vendor_id and not brand_id:
        return products_by_vendor(G, vendor_id=vendor_id)
    if vendor_id not in G or brand_id not in G:
        return []
    results = []
    for u, v, data in G.out_edges(vendor_id, data=True):
        if data.get('type') == 'SUPPLIES':
            product_id = v
            for pu, pv, pdata in G.out_edges(product_id, data=True):
                if pdata.get('type') == 'MADE_BY' and pv == brand_id:
                    results.append({"product_name": G.nodes[product_id]['name']})
    return results


def categories_by_vendor(G, vendor=None, vendor_id=None):
    vendor_id = vendor if vendor is not None else vendor_id
    if vendor_id not in G:
        return []
    categories = set()
    for u, v, data in G.out_edges(vendor_id, data=True):
        if data.get('type') == 'SUPPLIES':
            product_id = v
            for pu, pv, pdata in G.out_edges(product_id, data=True):
                if pdata.get('type') == 'BELONGS_TO':
                    categories.add(G.nodes[pv]['name'])
    return [{"category_name": c} for c in categories]

def vendors_by_brand(G, brand=None, brand_id=None):
    brand_id = brand if brand is not None else brand_id
    if brand_id not in G:
        return []
    vendors = set()
    for pu, bv, pdata in G.in_edges(brand_id, data=True):
        if pdata.get('type') == 'MADE_BY':
            product_id = pu
            for vu, pv, vdata in G.in_edges(product_id, data=True):
                if vdata.get('type') == 'SUPPLIES':
                    vendors.add(G.nodes[vu]['name'])
    return [{"vendor_name": v} for v in vendors]

def customers_by_brand(G, brand=None, brand_id=None):
    brand_id = brand if brand is not None else brand_id
    if brand_id not in G:
        return []
    customers = set()
    for pu, bv, pdata in G.in_edges(brand_id, data=True):
        if pdata.get('type') == 'MADE_BY':
            product_id = pu
            for ou, pv, odata in G.in_edges(product_id, data=True):
                if odata.get('type') == 'CONTAINS':
                    order_id = ou
                    for cu, ov, cdata in G.in_edges(order_id, data=True):
                        if cdata.get('type') == 'PLACED':
                            customers.add(G.nodes[cu]['name'])
    return [{"customer_name": c} for c in customers]

def total_quantity_ordered(G, product=None, product_id=None):
    product_id = product if product is not None else product_id
    if product_id not in G:
        return []
    total = 0
    for u, v, data in G.in_edges(product_id, data=True):
        if data.get('type') == 'CONTAINS':
            total += data.get('quantity', 0)
    if total > 0:
        return [{"product_name": G.nodes[product_id]['name'], "total_quantity": total}]
    return []

def order_details(G, order_id=None, order=None):
    order_id = order_id if order_id is not None else order
    if order_id not in G:
        return []
    results = []
    customer_name = "Unknown"
    for u, v, data in G.in_edges(order_id, data=True):
        if data.get('type') == 'PLACED':
            customer_name = G.nodes[u]['name']
            
    for u, v, data in G.out_edges(order_id, data=True):
        if data.get('type') == 'CONTAINS':
            results.append({
                "customer_name": customer_name,
                "product_name": G.nodes[v]['name'],
                "quantity": data.get('quantity'),
                "unit_price": data.get('unit_price')
            })
    return results

def products_by_category(G, category=None, category_id=None):
    category_id = category if category is not None else category_id
    if category_id not in G:
        return []
    results = []
    for u, v, data in G.in_edges(category_id, data=True):
        if data.get('type') == 'BELONGS_TO':
            results.append({"product_name": G.nodes[u]['name']})
    return results
