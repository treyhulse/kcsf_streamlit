import streamlit as st
from utils.rest import make_netsuite_rest_api_request

# Title
st.title("Fetch Sales Order by Sales Order Number")

# 1. User input for Sales Order Number
sales_order_number = st.text_input("Enter Sales Order Number")

# If user inputs a sales order number and presses the button
if st.button("Fetch Sales Order"):
    
    if sales_order_number:
        # 2. Fetch internal ID from the sales order number
        endpoint_for_internal_id = f"salesOrder?transactionNumber={sales_order_number}"
        search_result = make_netsuite_rest_api_request(endpoint_for_internal_id)

        if search_result and "id" in search_result:
            # Fetch the internal ID from the search result
            internal_id = search_result["id"]

            # 3. Fetch Sales Order details using the internal ID
            endpoint = f"salesOrder/{internal_id}"
            sales_order_data = make_netsuite_rest_api_request(endpoint)

            # Check if data is retrieved successfully
            if sales_order_data:
                # Trimmed down data
                trimmed_data = {
                    "id": sales_order_data.get("id"),
                    "tranId": sales_order_data.get("tranId"),
                    "orderStatus": sales_order_data.get("orderStatus", {}).get("refName"),
                    "billAddress": sales_order_data.get("billAddress"),
                    "shipAddress": sales_order_data.get("shipAddress"),
                    "subtotal": sales_order_data.get("subtotal"),
                    "total": sales_order_data.get("total"),
                    "createdDate": sales_order_data.get("createdDate"),
                    "salesRep": sales_order_data.get("salesRep", {}).get("refName"),
                    "shippingMethod": sales_order_data.get("shipMethod", {}).get("refName"),
                    "currency": sales_order_data.get("currency", {}).get("refName")
                }
                
                # Create a "card-like" UI for displaying the Sales Order details
                with st.expander(f"Sales Order #{trimmed_data['tranId']} (ID: {trimmed_data['id']})"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Order Information")
                        st.write(f"**Status**: {trimmed_data['orderStatus']}")
                        st.write(f"**Order ID**: {trimmed_data['id']}")
                        st.write(f"**Transaction ID**: {trimmed_data['tranId']}")
                        st.write(f"**Created Date**: {trimmed_data['createdDate']}")
                    
                    with col2:
                        st.markdown("### Financial Information")
                        st.write(f"**Subtotal**: ${trimmed_data['subtotal']}")
                        st.write(f"**Total**: ${trimmed_data['total']}")
                        st.write(f"**Currency**: {trimmed_data['currency']}")
                
                    st.markdown("### Addresses")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Billing Address")
                        st.write(trimmed_data['billAddress'])
                        
                    with col2:
                        st.markdown("#### Shipping Address")
                        st.write(trimmed_data['shipAddress'])
                
                    st.markdown("### Other Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Sales Rep**: {trimmed_data['salesRep']}")
                    
                    with col2:
                        st.write(f"**Shipping Method**: {trimmed_data['shippingMethod']}")

                # Optional: View full raw response if needed
                with st.expander("View Full Response"):
                    st.json(sales_order_data)

            else:
                st.error("Sales Order details not found.")
        else:
            st.error("Invalid Sales Order Number or no matching internal ID found.")
    else:
        st.error("Please enter a Sales Order Number.")
