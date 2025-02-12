from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import json

class InvoiceGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.invoice_style = ParagraphStyle(
            'CustomStyle',
            fontSize=12,
            fontName='Helvetica',
            spaceAfter=1
        )
        # Add organization header style
        self.org_header_style = ParagraphStyle(
            'OrgHeader',
            parent=self.styles['Heading1'],
            fontSize=22,
            fontName='Helvetica-Bold',
            alignment=1,  # Center alignment
            spaceAfter=0
        )
        # Add manager details style
        self.manager_style = ParagraphStyle(
            'ManagerDetails',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica',
            alignment=1,  # Center alignment
            spaceAfter=0
        )

    def generate_invoice(self, invoice_data: dict, output_path: str):
        """Generate PDF invoice with specific layout"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=10,
            bottomMargin=10
        )

        # Build content
        elements = []

        # Main border
        main_table_style = TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ])
    
        # Organization header
        org_name = Paragraph("MZ TRADERS PESHAWAR", self.org_header_style)
        manager_details = Paragraph("Manager: Malik Zafar (0311-9898059)", self.manager_style)

        # Horizontal separator line
        separator = HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black,
            spaceBefore=0,
            spaceAfter=0
        )

        # details with invoice number and date and name and address
        details_data_1 = [
            [invoice_data['customer_name'], f"Invoice # {invoice_data['invoice_number']}"]
        ]
        details_table_1 = Table(details_data_1, colWidths=[4*inch, 4*inch])
        details_table_1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 100),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        details_data_2 = [
            [invoice_data['customer_address'], invoice_data['date']]
        ]
        details_table_2 = Table(details_data_2, colWidths=[4*inch, 4*inch])
        details_table_2.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 100),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))

        # Product details table with border
        product_headers = ['Product Name', 'Quantity Box', 'Pieces Sent', 'Price per Piece', 'Total Price']
        product_data = [product_headers]

        # Parse items if they're stored as a JSON string
        items = invoice_data['items']
        if isinstance(items, str):
            items = json.loads(items)

        total_pieces = 0
        for item in items:
            product_data.append([
                item['product_name'],
                str(item['quantity_box']),
                str(item['pieces_sent']),
                f"{item['price_per_piece']:.2f}/-",
                f"{item['total_price']:.2f}/-"
            ])
            total_pieces += int(item['pieces_sent'])

        products_table = Table(product_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        products_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        # Summary
        summary_data = [
            [f"Total Pieces: {total_pieces}"],
            [ f"Total Amount: {invoice_data['total_amount']:.2f}/-"]
        ]
        summary_table = Table(summary_data, colWidths=[4*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            # ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))

        # Wrap all content in the main border
        content = [
            [org_name],
            [manager_details],
            [separator],
            [details_table_1],
            [details_table_2],  
            [products_table],
            [summary_table]
        ]

        main_table = Table(content, colWidths=[8*inch])
        main_table.setStyle(main_table_style)
        elements.append(main_table)

        # Generate PDF
        doc.build(elements)