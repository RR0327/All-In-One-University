# services/utils.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from twilio.rest import Client
from django.conf import settings


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


def send_wallet_sms(user_phone, amount, new_balance):
    """Sends a real-time SMS alert for wallet updates."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = (
        f"Campus Wallet Alert: ৳{amount} has been credited to your account. "
        f"New Balance: ৳{new_balance}. Stay secure!"
    )

    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user_phone,  # Ensure phone is in E.164 format (e.g., +8801...)
        )
    except Exception as e:
        print(f"SMS Error: {e}")
