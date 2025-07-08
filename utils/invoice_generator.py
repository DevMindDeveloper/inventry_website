from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, HRFlowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import json

class InvoiceGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

        self.wrap_style = self.styles["BodyText"]

        self.bold_style = ParagraphStyle(name="BoldStyle", fontName="Helvetica", fontSize=12)

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
            ('TOPPADDING', (0, 0), (-1, -1), 5),  # Reduced padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # Reduced padding
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ])

        header_style = ParagraphStyle(
            name="HeaderStyle",
            fontName="Helvetica-Bold",
            fontSize=10,
            alignment=TA_CENTER,  # Center horizontally
            textColor=colors.whitesmoke,
            leading=12
        )
                     
        # Organization header
        org_name = Paragraph("MZ TRADERS PESHAWAR", self.org_header_style)
        manager_details = Paragraph("SALE INVOICE", self.org_header_style)

        # Horizontal separator line
        separator = HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black,
            spaceBefore=0,
            spaceAfter=0
        )

        # Details with invoice number, date, name, and address
        details_data_1 = [[
            Paragraph(f"<b>Name:</b> {invoice_data['customer_name']}", self.bold_style),
            f"Invoice # {invoice_data['invoice_number']}"
        ]]
        details_table_1 = Table(details_data_1, colWidths=[4*inch, 4*inch])
        details_table_1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 85),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
        ]))
        details_data_2 = [[
            Paragraph(f"<b>Address:</b> {invoice_data['customer_address']}", self.bold_style),
            f"Date : {invoice_data['date']}"
        ]]
        details_table_2 = Table(details_data_2, colWidths=[4*inch, 4*inch])
        details_table_2.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 70),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
        ]))
        details_data_3 = [[
            Paragraph(f"<b>Order Booker:</b> {invoice_data['order_booker_name']}", self.bold_style)
        ]]
        details_table_3 = Table(details_data_3, colWidths=[8*inch])
        details_table_3.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 70),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
        ]))

        # Product details table
        product_headers = [
            Paragraph('S#', header_style),
            Paragraph('Product<br/>Description', header_style),
            Paragraph('Units Per<br/>Ctn', header_style),
            Paragraph('Quantity', header_style),
            Paragraph('Unit<br/>Rate', header_style),
            Paragraph('Discount<br/>(%)', header_style),
            Paragraph('Discount<br/>Amount', header_style),
            Paragraph('Net<br/>Rate', header_style),
            Paragraph('Total<br/>Amount', header_style)
        ]
        product_data = [product_headers]

        # Parse items if they're stored as a JSON string
        items = invoice_data['items']
        if isinstance(items, str):
            items = json.loads(items)

        total_pieces = 0
        for ind, item in enumerate(items, start=1):
            product_data.append([
                ind,
                Paragraph(item['product_name'], self.wrap_style),
                str(item['units_per_coton']),
                str(item['quantity']),
                f"{item['unit_rate']:.2f}/-",
                f"{item['discount_percent']:.2f}%",
                f"{item['discount_amount']:.2f}/-",
                f"{item['net_rate']:.2f}/-",
                f"{item['total_price']:.2f}/-"
            ])
            total_pieces += int(item['quantity'])

        products_table = Table(product_data, colWidths=[0.5*inch, 1.00*inch, 0.93*inch, 0.90*inch, 0.91*inch, 0.95*inch, 0.82*inch, 0.80*inch, 0.80*inch])
        products_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Add border to product table
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            # ('LEFTPADDING', (0, 0), (-1, -1), 15),
            # ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            # ('TOPPADDING', (0, 0), (-1, -1), 10),
            # ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Summary
        summary_data = [
            [f"Total Pieces: {total_pieces}"],
            [f"Net Total: {invoice_data['total_amount']:.2f}/-"]
        ]
        summary_table = Table(summary_data, colWidths=[8*inch])
        summary_table.setStyle(TableStyle([
            # ('BOX', (0, 0), (-1, -1), 0, colors.black),  # Add border to summary table
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 25),
            ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ]))

        # Wrap header and customer details in the main border
        main_content = [
            [org_name],
            [manager_details],
            [separator],
            [details_table_1],
            [details_table_2],
            [details_table_3]
        ]
        main_table = Table(main_content, colWidths=[8*inch])
        main_table.setStyle(main_table_style)
        elements.append(main_table)
        elements.append(Spacer(1, 12))  # Add vertical space (12 points) between main_table and products_table
        elements.append(products_table)
        elements.append(Spacer(1, 12))  # Add vertical space (12 points) between main_table and products_table
        elements.append(summary_table)

        # Generate PDF
        doc.build(elements)
