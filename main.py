import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils.data_manager import DataManager
from utils.invoice_generator import InvoiceGenerator

# Initialize data manager
data_manager = DataManager()
invoice_generator = InvoiceGenerator()

# Page configuration
st.set_page_config(
    page_title="Invoice Generator",
    page_icon="📄",
    layout="wide"
)
hide_button="""
    <style> 
        header{
        visibility:hidden;
        }
    </style>"""
st.markdown(hide_button, unsafe_allow_html=True)

hide_streamlit_style = """
    <style>
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for products
if 'num_products' not in st.session_state:
    st.session_state.num_products = 1

st.title("Generate Invoice #" + str(data_manager.get_next_invoice_number()))

# Invoice generation form
form = st.form("invoice_form")
with form:
    # Customer and sender details
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Details")
        customer_name = st.text_input("Customer Name")
        customer_address = st.text_area("Customer Address")

    # Product details
    st.subheader("Product Details")

    # Dynamic product rows
    products = []
    for i in range(st.session_state.num_products):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            product_name = st.text_input(f"Product Name #{i+1}")
        with col2:
            quantity_box = st.number_input(f"Quantity Box #{i+1}", min_value=0)
        with col3:
            pieces_sent = st.number_input(f"Pieces Sent #{i+1}", min_value=0)
        with col4:
            price_per_piece = st.number_input(f"Price per Piece #{i+1} (Rs)", min_value=0)

        total_price = pieces_sent * price_per_piece
        if product_name and (quantity_box > 0 or pieces_sent > 0):
            products.append({
                'product_name': product_name,
                'quantity_box': quantity_box,
                'pieces_sent': pieces_sent,
                'price_per_piece': price_per_piece,
                'total_price': total_price
            })

    # Submit button
    submitted = form.form_submit_button("Generate Invoice")

# Add/Remove product buttons
col1, col2 = st.columns([10, 4])
with col1:
    if st.button(f"➕ Add Product ({30-st.session_state.num_products} Items)"):
        st.session_state.num_products += 1
        st.rerun()
with col2:
    if st.session_state.num_products > 1 and st.button("➖ Remove Last Product"):
        st.session_state.num_products -= 1
        st.rerun()

# Handle form submission outside the form
if submitted:
    if st.session_state.num_products <= 30:
        if customer_name and customer_address and products:

            # Calculate total amount and price
            total_amount = sum(item['pieces_sent'] * item['price_per_piece'] for item in products)

            # Generate invoice number
            invoice_number = data_manager.get_next_invoice_number()

            # Prepare invoice data
            invoice_data = {
                'invoice_number': invoice_number,
                'customer_name': customer_name,
                'customer_address': customer_address,
                # 'sender_name': sender_name,
                'items': products,
                'total_amount': total_amount,
                'date': datetime.now().strftime('%Y-%m-%d')
            }

            # Save invoice data
            data_manager.save_invoice(invoice_data)

            # Generate PDF
            os.makedirs('generated_invoices', exist_ok=True)
            safe_customer_name = "".join(x for x in customer_name if x.isalnum() or x.isspace()).strip()
            pdf_path = f"generated_invoices/{safe_customer_name}_{invoice_number}.pdf"
            invoice_generator.generate_invoice(invoice_data, pdf_path)

            # Success message and download button (outside form)
            st.success(f"Invoice #{invoice_number} generated successfully!")

            # Open and provide PDF for download
            with open(pdf_path, "rb") as pdf_file:
                bytes_data = pdf_file.read()
                st.download_button(
                    label="Download Invoice PDF",
                    data=bytes_data,
                    file_name=f"{safe_customer_name}_{invoice_number}.pdf",
                    mime="application/pdf"
                )
            
        else:
            st.error("Please fill in all required fields and add at least one product")
    else:
        st.error("Inovice is FULL! Remove items more than 30 and create a new inovice for it.")
