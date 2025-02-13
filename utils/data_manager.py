import pandas as pd
import json
from pathlib import Path
import os

class DataManager:
    def __init__(self):
        self.invoices_file = "data/invoices.csv"
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.invoices_file):
            pd.DataFrame(columns=[
                'invoice_number', 'customer_name', 'customer_address',
                'sender_name', 'items', 'total_amount', 'date'
            ]).to_csv(self.invoices_file, index=False)

    def get_next_invoice_number(self):
        """Generate the next sequential invoice number"""
        # try:
        df = pd.read_csv(self.invoices_file)
        if df.empty:
            return "1"
        else:
            return df['invoice_number'].shape[0] + 1

    def save_invoice(self, invoice_data: dict):
        """Save generated invoice"""
        df = pd.read_csv(self.invoices_file)
        # Convert items list to string for storage
        invoice_data['items'] = json.dumps(invoice_data['items'])
        new_row = pd.DataFrame([invoice_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.invoices_file, index=False)

    def get_invoices(self):
        """Get all invoices"""
        return pd.read_csv(self.invoices_file)

# ob = DataManager()
