import csv
import os
import networkx as nx

def build_kg():
    G = nx.MultiDiGraph()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    def load_csv(filename):
        return csv.DictReader(open(os.path.join(data_dir, filename), mode='r', encoding='utf-8'))
    
    # Load Brands
    for row in load_csv('brands.csv'):
        G.add_node(row['brand_id'], type='Brand', name=row['name'])
        
    # Load Categories
    for row in load_csv('categories.csv'):
        G.add_node(row['category_id'], type='Category', name=row['name'])
        
    # Load Vendors
    for row in load_csv('vendors.csv'):
        G.add_node(row['vendor_id'], type='Vendor', name=row['name'])
        
    # Load Customers
    for row in load_csv('customers.csv'):
        G.add_node(row['customer_id'], type='Customer', name=row['name'])
        
    # Load Orders
    for row in load_csv('orders.csv'):
        G.add_node(row['order_id'], type='Order', name=row['order_id'])
        G.add_edge(row['customer_id'], row['order_id'], type='PLACED')
        
    # Load Products
    for row in load_csv('products.csv'):
        G.add_node(row['product_id'], type='Product', name=row['name'])
        G.add_edge(row['product_id'], row['brand_id'], type='MADE_BY')
        G.add_edge(row['product_id'], row['category_id'], type='BELONGS_TO')
        G.add_edge(row['vendor_id'], row['product_id'], type='SUPPLIES')
        
    # Load Order Items
    for row in load_csv('order_items.csv'):
        G.add_edge(
            row['order_id'], 
            row['product_id'], 
            type='CONTAINS', 
            quantity=int(row['quantity']), 
            unit_price=float(row['unit_price'])
        )
        
    return G

if __name__ == "__main__":
    G = build_kg()
    
    print(f"Graph loaded successfully.")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    node_types = {}
    for _, data in G.nodes(data=True):
        t = data.get('type')
        node_types[t] = node_types.get(t, 0) + 1
        
    edge_types = {}
    for u, v, data in G.edges(data=True):
        t = data.get('type')
        edge_types[t] = edge_types.get(t, 0) + 1
        
    print("\nNodes by type:")
    for k, v in node_types.items():
        print(f"  {k}: {v}")
        
    print("\nEdges by type:")
    for k, v in edge_types.items():
        print(f"  {k}: {v}")
