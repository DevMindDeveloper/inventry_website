import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

class GoogleSheetsDataManager:
    def __init__(self, sheet_name, worksheet_name="Sheet1"):
        # Load credentials from Streamlit secrets

        creds = st.secrets["GOOGLE_SHEETS_CREDS"]
        if isinstance(creds, str):
            creds_dict = json.loads(creds)  # Cloud: JSON string
        else:
            creds_dict = dict(creds)   # Local: TOML table

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(creds)
        self.sheet = client.open(sheet_name).worksheet(worksheet_name)

    def get_next_invoice_number(self):
        records = self.sheet.get_all_records()
        if not records:
            return 1050
        return max([int(r["invoice_number"]) for r in records if str(r["invoice_number"]).isdigit()]) + 1

    def save_invoice(self, invoice_data):
        # Flatten items for storage, or store as JSON string
        invoice_data = invoice_data.copy()
        invoice_data["items"] = json.dumps(invoice_data["items"])
        # Ensure the order matches the sheet headers
        headers = self.sheet.row_values(1)
        row = [invoice_data.get(h, "") for h in headers]
        self.sheet.append_row(row)

    def get_invoice_by_number(self, invoice_number):
        records = self.sheet.get_all_records()
        for record in records:
            if str(record.get("invoice_number")) == str(invoice_number):
                # Parse items if stored as JSON
                if "items" in record:
                    items = record["items"]
                    if isinstance(items, str):
                        try:
                            record["items"] = json.loads(items)
                        except Exception:
                            pass
                return record
        return None 
