import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.utils.timezone import now

def generate_invoice_pdf(user, cart_items, total, shipping_address, payment_method):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = styles["Heading1"]

    # ----------------------------
    # Company Header
    # ----------------------------
    elements.append(Paragraph("<b>MyShop</b>", heading))
    elements.append(Paragraph("123 Business Street, India", normal))
    elements.append(Paragraph("Email: support@myshop.com", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ----------------------------
    # Invoice Info
    # ----------------------------
    elements.append(Paragraph("<b>INVOICE</b>", styles["Heading2"]))
    elements.append(Paragraph(
        f"Date: {now().strftime('%d-%m-%Y %H:%M')}",
        normal
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # ----------------------------
    # Customer / Shipping Info
    # ----------------------------
    elements.append(Paragraph("<b>Bill To:</b>", styles["Heading3"]))
    elements.append(Paragraph(shipping_address.full_name, normal))
    elements.append(Paragraph(shipping_address.address_line_1, normal))

    if shipping_address.address_line_2:
        elements.append(Paragraph(shipping_address.address_line_2, normal))

    elements.append(Paragraph(
        f"{shipping_address.city}, {shipping_address.state} - {shipping_address.postal_code}",
        normal
    ))
    elements.append(Paragraph(shipping_address.country, normal))
    elements.append(Spacer(1, 0.5 * inch))

    # ----------------------------
    # Payment Method Section
    # ----------------------------
    elements.append(Paragraph(f"<b>Payment Method:</b> {payment_method}", normal))
    elements.append(Spacer(1, 0.3 * inch))

    # ----------------------------
    # Items Table
    # ----------------------------
    data = [["Product", "Qty", "Unit Price", "Subtotal"]]

    for item in cart_items:
        data.append([
            Paragraph(item["name"], normal),
            str(item["quantity"]),
            f"Rs {item['price']:.2f}",
            f"Rs {item['subtotal']:.2f}",
        ])

    data.append(["", "", "Total", f"Rs {total:.2f}"])

    table = Table(data, colWidths=[2.5 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2874F0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("ALIGN", (1, 1), (-1, -1), "CENTER"),

        ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),

        ("BACKGROUND", (-2, -1), (-1, -1), colors.HexColor("#E3F2FD")),

        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # ----------------------------
    # Footer
    # ----------------------------
    elements.append(Paragraph(
        "Thank you for shopping with us!",
        styles["Italic"]
    ))

    doc.build(elements)
    buffer.seek(0)

    return buffer