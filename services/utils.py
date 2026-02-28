# services/utils.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime


def generate_meal_pdf(user, transactions, total_spent):
    """Generates a professional PDF report for student meal spending."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Header ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "BAIUST - Campus Management System")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 70, f"Meal Summary Report for: {user.username}")
    p.drawString(
        100, height - 85, f"Report Generated: {datetime.now().strftime('%d %b, %Y')}"
    )
    p.line(100, height - 90, 500, height - 90)

    # --- Table Headers ---
    y_position = height - 120
    p.setFont("Helvetica-Bold", 11)
    p.drawString(100, y_position, "Date")
    p.drawString(200, y_position, "Description")
    p.drawString(420, y_position, "Amount (BDT)")
    p.line(100, y_position - 5, 500, y_position - 5)

    # --- Transaction Rows ---
    p.setFont("Helvetica", 10)
    y_position -= 25

    for tx in transactions:
        # Check for page overflow
        if y_position < 100:
            p.showPage()
            y_position = height - 50

        # Displaying the data you just created in the shell
        p.drawString(100, y_position, tx.timestamp.strftime("%Y-%m-%d"))
        p.drawString(200, y_position, tx.description[:35])  # Limits text length
        p.drawString(420, y_position, f"{tx.amount:,.2f}")
        y_position -= 20

    # --- Summary Footer ---
    p.line(100, y_position, 500, y_position)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y_position - 25, f"Total Monthly Spend: BDT {total_spent:,.2f}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
