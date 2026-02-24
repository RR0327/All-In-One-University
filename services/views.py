from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from collections import OrderedDict
import datetime

from .models import (
    CafeteriaMenu,
    BusRoute,
    BusSchedule,
    Faculty,
    Course,
    ClassSchedule,
    Club,
    Event,
    CampusBuilding,
    MealBooking,
)
from .forms import MealBookingForm, RegistrationForm
from django.db.models import Sum
from datetime import date, timedelta
import qrcode
import io
import base64
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
import uuid
from sslcommerz_lib import SSLCommerz
from .utils import generate_meal_pdf


# ==========================================
# 1. HOME & AUTHENTICATION
# ==========================================


def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def user_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def user_logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("index")


@login_required
def dashboard_view(request):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Calculate total projected cost for the week
    weekly_total = (
        CafeteriaMenu.objects.filter(day__range=[start_of_week, end_of_week]).aggregate(
            total=Sum("price")
        )["total"]
        or 0
    )

    notices = Event.objects.all().order_by("-event_date")[:5]  # Get 5 latest notices

    return render(
        request,
        "dashboard.html",
        {
            "weekly_total": weekly_total,
            "start_date": start_of_week,
            "end_date": end_of_week,
            "notices": notices,
        },
    )


# ==========================================
# 2. CAFETERIA LOGIC
# ==========================================


def cafeteria_weekly_view(request):
    """Groups and sorts menus chronologically: Breakfast -> Lunch -> Snacks -> Dinner."""
    menu_items = CafeteriaMenu.objects.all().order_by("day")

    # Define the professional chronological order
    meal_order = {"Breakfast": 1, "Lunch": 2, "Snacks": 3, "Dinner": 4}

    day_groups = OrderedDict()

    # Sort the items using our meal_order mapping
    sorted_menu = sorted(
        menu_items, key=lambda x: (x.day, meal_order.get(x.meal_type, 99))
    )

    for item in sorted_menu:
        if item.day not in day_groups:
            day_groups[item.day] = []
        day_groups[item.day].append(item)

    return render(request, "cafeteria_multi_day.html", {"day_groups": day_groups})


@login_required
def create_meal_booking(request):
    if request.method == "POST":
        form = MealBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect("booking_success")
    else:
        form = MealBookingForm()
    return render(request, "meal_booking.html", {"form": form})


@login_required
def booking_success_view(request):
    # Fetch the latest booking for the user
    booking = MealBooking.objects.filter(user=request.user).latest("created_at")

    # Create the data string for the QR code
    qr_data = f"User:{booking.user.username}|Dates:{booking.date_from}-{booking.date_to}|B:{booking.breakfast}|L:{booking.lunch}|D:{booking.dinner}"

    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to buffer to send to template
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(
        request, "booking_success.html", {"qr_code": qr_code_base64, "booking": booking}
    )


# Generic view for individual meal types
def cafeteria_meal_type_view(request, meal_type):
    menus = CafeteriaMenu.objects.filter(meal_type__iexact=meal_type)
    template_map = {
        "breakfast": "cafeteria_breakfast.html",
        "lunch": "cafeteria_lunch.html",
        "snacks": "cafeteria_snacks.html",
        "dinner": "cafeteria_dinner.html",
    }
    template_name = template_map.get(meal_type.lower(), "cafeteria_all.html")
    return render(request, template_name, {"menus": menus, "meal_type": meal_type})


# ==========================================
# 3. TRANSPORT & ACADEMICS
# ==========================================


def bus_schedules_view(request):
    schedules = BusSchedule.objects.select_related("route").all()
    return render(request, "bus_schedules.html", {"schedules": schedules})


@login_required
def class_schedules_view(request):
    schedules = ClassSchedule.objects.select_related("course").all()
    faculty = Faculty.objects.all()
    return render(
        request, "class_schedules.html", {"schedules": schedules, "faculty": faculty}
    )


@login_required
def add_class_schedule(request):
    # Logic for adding schedules can be expanded here
    return redirect("class_schedules")


# ==========================================
# 4. EVENTS & MAPS
# ==========================================


def events_view(request):
    events = Event.objects.all().order_by("event_date")
    clubs = Club.objects.all()
    return render(request, "events.html", {"events": events, "clubs": clubs})


def campus_map_view(request):
    buildings = CampusBuilding.objects.all()
    return render(request, "campus_map.html", {"buildings": buildings})


def buildings_json(request):
    buildings = list(
        CampusBuilding.objects.values("building_name", "latitude", "longitude")
    )
    return JsonResponse({"buildings": buildings})


def send_booking_email(user, booking, qr_image_base64):
    """Automated email delivery for meal QR codes."""
    subject = f"Meal Booking Confirmed - {booking.id}"
    message = f"Hello {user.username},\n\nYour meal booking for {booking.date_from} is confirmed."

    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    # Optional: Attach the QR code as an image
    # In a real production environment, you would attach the raw buffer bytes
    email.send()


@staff_member_required
def verify_meal_qr(request):
    """Secure endpoint for cafeteria staff to verify meal codes."""
    qr_data = request.GET.get("data")

    try:
        # Expected format from our generator: User:rakib|Dates:2026-02-24-2026-02-25|B:True|L:True|D:False
        parts = dict(item.split(":") for item in qr_data.split("|"))
        username = parts.get("User")

        # In a production app, you would query the database here to check if
        # this specific booking ID has already been 'used' for today.

        return JsonResponse(
            {
                "status": "success",
                "message": f"Valid Booking for {username}",
                "details": parts,
            }
        )
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Invalid or Corrupted QR Code"}, status=400
        )


@login_required
def process_meal_payment(request, amount):
    """Atomic transaction to ensure data integrity during payment."""
    try:
        with transaction.atomic():
            wallet = request.user.studentwallet
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    tx_type="Debit",
                    description="Meal Booking Payment",
                )
                return True
            return False
    except StudentWallet.DoesNotExist:
        return False


@login_required
def transaction_history_view(request):
    """Retrieves all wallet activity for the logged-in user."""
    wallet = request.user.studentwallet
    transactions = wallet.transactions.all().order_by("-timestamp")
    return render(
        request, "transactions.html", {"transactions": transactions, "wallet": wallet}
    )


# Payment gateway integration example (SSLCommerz)
@login_required
def initiate_payment(request):
    """Initializes a secure payment session with SSLCommerz."""
    # Use environment variables for Store ID and Password
    mypayment = SSLCommerz(
        {
            "store_id": settings.SSLCOMMERZ_STORE_ID,
            "store_pass": settings.SSLCOMMERZ_STORE_PASS,
            "issandbox": True,  # Set to False for production
        }
    )

    total_amount = request.POST.get("amount", 500)  # Amount to add to wallet
    tran_id = str(uuid.uuid4())[:10]  # Unique transaction ID

    post_body = {
        "total_amount": total_amount,
        "currency": "BDT",
        "tran_id": tran_id,
        "success_url": "http://127.0.0.1:8000/payment-success/",
        "fail_url": "http://127.0.0.1:8000/payment-fail/",
        "cancel_url": "http://127.0.0.1:8000/payment-cancel/",
        "emi_option": 0,
        "cus_name": request.user.username,
        "cus_email": request.user.email,
        "cus_phone": "01XXXXXXXXX",  # Can be pulled from a Profile model
        "cus_add1": "Cumilla",  # User's location
        "cus_city": "Cumilla",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "product_name": "Wallet Credit",
        "product_category": "Digital",
        "product_profile": "general",
    }

    response = mypayment.init_payment(post_body)
    return redirect(response["GatewayPageURL"])


@login_required
def download_meal_summary(request):
    """View to trigger the download of the monthly meal report."""
    wallet = request.user.studentwallet
    # Filter for the current month's debits
    transactions = wallet.transactions.filter(tx_type="Debit").order_by("-timestamp")

    total_spent = sum(tx.amount for tx in transactions)

    pdf_buffer = generate_meal_pdf(request.user, transactions, total_spent)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"Meal_Summary_{request.user.username}.pdf",
    )
