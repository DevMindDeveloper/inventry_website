import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils.google_sheets_data_manager import GoogleSheetsDataManager
from utils.invoice_generator import InvoiceGenerator

# Initialize data manager
data_manager = GoogleSheetsDataManager(sheet_name="invoices")
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

order_booker_options = [
    "Zubair Khan (0315-9288706)",
    "Other"
]

# Invoice generation form
form = st.form("invoice_form")
with form:
    # Customer and sender details
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Details")
        customer_name = st.text_input("Customer Name")
        customer_address = st.text_area("Customer Address")

    with col2:
        st.subheader("Order Booker")
        order_booker_name = st.selectbox(
            "Order Booker Name",
            order_booker_options,
            key="order_booker_name"
        )
        if order_booker_name == "Other":
            final_order_booker_name = st.text_input(
                "Enter custom order booker name",
                key="custom_order_booker_name"
            )
        else:
            final_order_booker_name = order_booker_name

    # Product details
    st.subheader("Product Details")

    # Dynamic product rows
    products = []

    product_options = [
        "",
        "Other",
        "SHAMPOO STRIPS 20 ML (12 Strips)",
        "VELVET SHAMPOO 300ML",
        "VELVET SHAMPOO 500ML",
        "VELVET SHAMPOO 4L",
        "GLASS CLEANER 500ML",
        "WATERLESS CAR WASH 500ML",
        "ENGINE DEGREASER 500ML",
        "ALL PURPOSE CLEANER 500ML",
        "RUST PREVENTIVE 500 ML",
        "TIRE POLISH 200ML",
        "CAR DASHBOARD CLEANER 200 ML",
        "INTERIOR DRESSING 500 ML",
        "TIRE DRESSING 500 ML",
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (1L)",
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (1L)",
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (1L)",
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (1L)",
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (4L)",
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (4L)",
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (4L)",
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (4L)",
        "COMPLETE KIT BOX",
        "DASHBOARD WAX SPRAY (ROSE) 450ML",
        "DASHBOARD WAX SPRAY (STRAWBERRY) 450ML",
        "DASHBOARD WAX SPRAY (LEMON) 450ML",
        "DASHBOARD WAX SPRAY (JASMINE) 450ML",
        "DASHBOARD WAX SPRAY (COLOGNE) 450ML",
        "DASHBOARD WAX SPRAY (OCEAN) 450ML",
        "INJECTOR CLEANER 450 ML",
        "INJECTOR CLEANER 300 ML",
        "TIRE FOAM 650 ML",
        "MULTI PURPOSE FOAM CLEANER 650 ML",
        "ENGINE SURFACE CLEANER 650ML",
        "ANTIRUST LUBRICANT 100 ML",
        "ANTIRUSTproduct_name LUBRICANT 220 ML",
        "HARD PASTE CAR WAX 180 GRM",
        "TONE ROYALITY FOR HER",
        "TONE WONDER FOR HER",
        "TONE VAPOR FOR ALL",
        "TONE MYSTERY FOR ALL",        
    ]

    product_rates = {
        "" : 0,
        "SHAMPOO STRIPS 20 ML (12 Strips)" : 150,
        "VELVET SHAMPOO 300ML" : 350,
        "VELVET SHAMPOO 500ML": 460,
        "VELVET SHAMPOO 4L":2650,
        "GLASS CLEANER 500ML":350,
        "WATERLESS CAR WASH 500ML":620,
        "ENGINE DEGREASER 500ML":620,
        "ALL PURPOSE CLEANER 500ML":620,
        "RUST PREVENTIVE 500 ML":1050,
        "TIRE POLISH 200ML":460,
        "CAR DASHBOARD CLEANER 200 ML":390,
        "INTERIOR DRESSING 500 ML":660,
        "TIRE DRESSING 500 ML":790,
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (1L)":530,
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (1L)":530,
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (1L)":790,
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (1L)":790,
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (4L)":1950,
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (4L)":1950,
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (4L)":2720,
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (4L)":2720,
        "COMPLETE KIT BOX":4920,
        "DASHBOARD WAX SPRAY (ROSE) 450ML":350,
        "DASHBOARD WAX SPRAY (STRAWBERRY) 450ML":350,
        "DASHBOARD WAX SPRAY (LEMON) 450ML":350,
        "DASHBOARD WAX SPRAY (JASMINE) 450ML":350,
        "DASHBOARD WAX SPRAY (COLOGNE) 450ML":350,
        "DASHBOARD WAX SPRAY (OCEAN) 450ML":350,
        "INJECTOR CLEANER 450 ML":350,
        "INJECTOR CLEANER 300 ML":250,
        "TIRE FOAM 650 ML":420,
        "MULTI PURPOSE FOAM CLEANER 650 ML":390,
        "ENGINE SURFACE CLEANER 650ML":420,
        "ANTIRUST LUBRICANT 100 ML":190,
        "ANTIRUSTproduct_name LUBRICANT 220 ML":300,
        "HARD PASTE CAR WAX 180 GRM":700,
        "TONE ROYALITY FOR HER":580,
        "TONE WONDER FOR HER":580,
        "TONE VAPOR FOR ALL":580,
        "TONE MYSTERY FOR ALL":580,
    }

    units_per_coton = {
        "" : 0,
        "SHAMPOO STRIPS 20 ML (12 Strips)" : 12,
        "VELVET SHAMPOO 300ML" : 24,
        "VELVET SHAMPOO 500ML": 12,
        "VELVET SHAMPOO 4L" : 4,
        "GLASS CLEANER 500ML":12,
        "WATERLESS CAR WASH 500ML":12,
        "ENGINE DEGREASER 500ML":12,
        "ALL PURPOSE CLEANER 500ML":12,
        "RUST PREVENTIVE 500 ML":12,
        "TIRE POLISH 200ML":24,
        "CAR DASHBOARD CLEANER 200 ML":24,
        "INTERIOR DRESSING 500 ML":12,
        "TIRE DRESSING 500 ML":12,
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (1L)":12,
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (1L)":12,
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (1L)":12,
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (1L)":12,
        "RADIATOR COOLANT GREEN OVER-HEAT PREVENTIVE (4L)":4,
        "RADIATOR COOLANT RED OVER-HEAT PREVENTIVE (4L)":4,
        "RADIATOR COOLANT GREEN SUPER ANTI-FREEZE (4L)":4,
        "RADIATOR COOLANT RED SUPER ANTI-FREEZE (4L)":4,
        "COMPLETE KIT BOX":3,
        "DASHBOARD WAX SPRAY (ROSE) 450ML":24,
        "DASHBOARD WAX SPRAY (STRAWBERRY) 450ML":24,
        "DASHBOARD WAX SPRAY (LEMON) 450ML":24,
        "DASHBOARD WAX SPRAY (JASMINE) 450ML":24,
        "DASHBOARD WAX SPRAY (COLOGNE) 450ML":24,
        "DASHBOARD WAX SPRAY (OCEAN) 450ML":24,
        "INJECTOR CLEANER 450 ML":24,
        "INJECTOR CLEANER 300 ML":24,
        "TIRE FOAM 650 ML":12,
        "MULTI PURPOSE FOAM CLEANER 650 ML":12,
        "ENGINE SURFACE CLEANER 650ML":12,
        "ANTIRUST LUBRICANT 100 ML":48,
        "ANTIRUST LUBRICANT 220 ML":24,
        "HARD PASTE CAR WAX 180 GRM":12,
        "TONE ROYALITY FOR HER":96,
        "TONE WONDER FOR HER":96,
        "TONE VAPOR FOR ALL":96,
        "TONE MYSTERY FOR ALL":96,
    }

    tab_space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    
    for i in range(st.session_state.num_products):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            product_name = st.selectbox(
                f"  {i+1} Product Name",
                product_options,
                key=f"product_name_{i}"
            )
            if product_name == "Other":
                custom_name = st.text_input(
                    f"Enter custom product name for item {i+1}",
                    key=f"custom_product_name_{i}"
                )
                final_product_name = custom_name
                # st.rerun()
            else:
                final_product_name = product_name
        with col2:
            quantity = st.number_input(f"Quantity", min_value=0, key=f"quantity_{i}")
        with col3:
            if final_product_name in product_rates:
                unit_rate = st.number_input(
                    "Unit Rate",
                    min_value=0,
                    value=product_rates[final_product_name],
                    key=f"unit_rate_{i}",
                    disabled=True
                )
            else:
                unit_rate = st.number_input(
                    "Unit Rate",
                    min_value=0,
                    key=f"unit_rate_{i}",
                    disabled=False
                )
        with col4:
            discount_percent = st.number_input(f"Discount (%)", min_value=0, max_value=100, key=f"discount_{i}")

        # units per ctn
        if final_product_name in units_per_coton:
                units_per_coton_value = units_per_coton[final_product_name]
                # st.markdown(f"**Unit Rate:** {units_per_coton_value}")
        else:
            units_per_coton_value = st.number_input(
                f"Units/Ctn",
                min_value=0,
                key=f"units_per_coton_value_{i}"
            )

        discount_amount = (unit_rate) * (discount_percent / 100)

        net_rate = unit_rate - discount_amount

        total_price = (quantity * net_rate)

        if final_product_name and quantity > 0:
            products.append({
                'product_name': final_product_name,
                'units_per_coton': units_per_coton_value,
                'quantity': quantity,
                'unit_rate': unit_rate,
                'discount_percent': discount_percent,
                'discount_amount': discount_amount,
                'net_rate' : net_rate,
                'total_price': total_price
            })
            print(products)

    # Submit button
    submitted = form.form_submit_button("Generate Invoice")

# Add/Remove product buttons
col1, col2 = st.columns([10, 4])
with col1:
    # if st.button(f"➕ Add Product ({30-st.session_state.num_products} Items)"):
    if st.button(f"➕ Add Product"):
        st.session_state.num_products += 1
        st.experimental_rerun()
        # st.rerun()
with col2:
    if st.session_state.num_products > 1 and st.button("➖ Remove Last Product"):
        st.session_state.num_products -= 1
        st.experimental_rerun()
        # st.rerun()

# Handle form submission outside the form
if submitted:
    # if st.session_state.num_products <= 30:
        if customer_name and customer_address and products:

            # Calculate total amount and price
            total_amount = sum(item['quantity'] * item['net_rate'] for item in products)

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
                'order_booker_name' : final_order_booker_name,
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
    # else:
    #     st.error("Inovice is FULL! Remove items more than 30 and create a new inovice for it.")
