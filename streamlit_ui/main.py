import streamlit as st
from api_client import api_client

# Set page config for a better layout
if st.button("📸 Take Photo", type="primary", use_container_width=True):
    st.switch_page("pages/camera.py")


# Get annotations from API
annotations = api_client.export_annotations()

# Process and display annotations
if annotations and "results" in annotations:
    # Group by date
    transactions_by_date = {}
    
    for result in annotations["results"]:
        # Extract date from arrived_at
        date_str = result.get("arrived_at", "").split("T")[0]
        if not date_str:
            continue
            
        # Find store name in content
        store_name = None
        items = []
        
        for section in result.get("content", []):
            if section.get("schema_id") == "basic_info_section":
                for child in section.get("children", []):
                    if child.get("schema_id") == "store_name":
                        store_name = child.get("value", "Unknown Store")
            
            elif section.get("schema_id") == "line_items_section":
                for child in section.get("children", []):
                    if child.get("schema_id") == "line_items":
                        for item in child.get("children", []):
                            if item.get("category") == "tuple":
                                item_data = {}
                                for field in item.get("children", []):
                                    if field.get("schema_id") == "item_description":
                                        item_data["Item"] = field.get("value", "")
                                    elif field.get("schema_id") == "item_amount":
                                        item_data["Price (Kč)"] = field.get("value", "")
                                    elif field.get("schema_id") == "item_quantity":
                                        item_data["Quantity"] = field.get("value", "")
                                    elif field.get("schema_id") == "item_amount_total":
                                        item_data["Total (Kč)"] = field.get("value", "")
                                if item_data:
                                    items.append(item_data)
        
        # Add to transactions by date
        if date_str not in transactions_by_date:
            transactions_by_date[date_str] = {}
        if store_name not in transactions_by_date[date_str]:
            transactions_by_date[date_str][store_name] = []
        transactions_by_date[date_str][store_name].extend(items)

    # Display transactions
    for date in sorted(transactions_by_date.keys(), reverse=True):
        st.write(f"#### {date}")
        
        for store_name, items in transactions_by_date[date].items():
            st.write(f"##### {store_name}")
            
            if items:
                # Create DataFrame for items
                import pandas as pd
                df = pd.DataFrame(items)
                
                # Display table
                st.dataframe(df, use_container_width=True)
            else:
                st.write("No items found")

#st.dataframe({
#    "Date": ["2024-03-20", "2024-03-19", "2024-03-18"],
#    "Description": ["Grocery Store", "Coffee Shop", "Restaurant"],
#    "Amount": ["$50.00", "$4.50", "$35.00"]
#})




