from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


def generate_meal_pdf(user, transactions, total_spent):
    """Generates a professional PDF report for student meal spending."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Header ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "BAIUST - Campus Management System")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, f"Meal Summary Report: {user.username}")
    p.line(100, height - 80, 500, height - 80)

    # --- Content ---
    y_position = height - 120
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y_position, "Date")
    p.drawString(250, y_position, "Description")
    p.drawString(450, y_position, "Amount")

    p.setFont("Helvetica", 10)
    y_position -= 20

    for tx in transactions:
        if y_position < 50:  # Simple pagination check
            p.showPage()
            y_position = height - 50

        p.drawString(100, y_position, tx.timestamp.strftime("%Y-%m-%d"))
        p.drawString(250, y_position, tx.description[:30])
        p.drawString(450, y_position, f"BDT {tx.amount}")
        y_position -= 20

    # --- Footer ---
    p.line(100, y_position - 10, 500, y_position - 10)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y_position - 30, f"Total Spent: BDT {total_spent}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
