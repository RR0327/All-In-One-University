import os
import django
import datetime
from django.utils import timezone
from decimal import Decimal

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "university_app.settings")
django.setup()

from django.contrib.auth.models import User
from services.models import (
    BusRoute,
    BusSchedule,
    CafeteriaMenu,
    Faculty,
    Course,
    ClassSchedule,
    Club,
    Event,
    CampusBuilding,
    StudentWallet,
    Transaction,
)


def create_academic_data():
    """Initializes faculty and course data."""
    dept = "Computer Science & Engineering"

    # Use a dictionary for cleaner faculty management
    faculties = [
        {"name": "Dr. Ariful Islam", "email": "arif@university.edu", "dept": dept},
        {"name": "Prof. Sarah Jahan", "email": "sarah@university.edu", "dept": dept},
    ]

    faculty_objs = []
    for f in faculties:
        obj, _ = Faculty.objects.get_or_create(
            name=f["name"], defaults={"email": f["email"], "department": f["dept"]}
        )
        faculty_objs.append(obj)

    # Courses
    Course.objects.get_or_create(
        code="CSE-201",
        defaults={
            "faculty": faculty_objs[0],
            "name": "Data Structures",
            "description": "Fundamental algorithms and complexity analysis",
        },
    )
    Course.objects.get_or_create(
        code="CSE-305",
        defaults={
            "faculty": faculty_objs[1],
            "name": "Web Development",
            "description": "Fullstack development with Python and Django",
        },
    )
    print("✓ Academic data initialized.")


def create_transport_data():
    """Initializes bus routes and base schedules."""
    routes = [
        ("Campus Express", "Main Gate", "CSE Building"),
        ("City Shuttle", "City Center", "University Terminal"),
    ]

    for name, start, end in routes:
        route, _ = BusRoute.objects.get_or_create(
            route_name=name, defaults={"start_location": start, "end_location": end}
        )

        # Base schedules
        BusSchedule.objects.get_or_create(
            route=route, departure_time="08:00", defaults={"arrival_time": "08:20"}
        )
    print("✓ Transport data initialized.")


def create_cafeteria_menu():
    """Generates 7 days of menus."""
    today = datetime.date.today()
    menu_templates = [
        ("Breakfast", "Oatmeal with Fruits & Coffee", 60.00),
        ("Lunch", "Chicken Biryani with Salad", 150.00),
        ("Dinner", "Grilled Fish and Steamed Veggies", 180.00),
    ]

    for i in range(7):
        target_date = today + datetime.timedelta(days=i)
        for m_type, desc, price in menu_templates:
            CafeteriaMenu.objects.get_or_create(
                day=target_date,
                meal_type=m_type,
                defaults={"description": desc, "price": Decimal(price)},
            )
    print("✓ 7-day Cafeteria menu generated.")


def initialize_wallets():
    """Ensures all users have a wallet with an initial signup bonus."""
    users = User.objects.all()
    count = 0

    for user in users:
        wallet, created = StudentWallet.objects.get_or_create(
            user=user, defaults={"balance": Decimal("500.00")}
        )
        if created:
            Transaction.objects.create(
                wallet=wallet,
                amount=Decimal("500.00"),
                tx_type="Credit",
                description="Initial Signup Bonus",
            )
            count += 1
    print(f"✓ Initialized {count} new student wallets with ৳500.")


def main():
    """Main execution flow."""
    print("--- Starting System Initialization ---")
    try:
        create_academic_data()
        create_transport_data()
        create_cafeteria_menu()

        # Clubs & Events
        club, _ = Club.objects.get_or_create(
            club_name="Robotics Society",
            defaults={"description": "Innovating for the future at BAIUST"},
        )
        Event.objects.get_or_create(
            event_name="NEOFETCH Hackathon",
            defaults={
                "club": club,
                "event_date": timezone.now() + datetime.timedelta(days=5),
                "description": "A 24-hour innovation challenge.",
            },
        )

        # Wallet setup is now part of the main flow
        initialize_wallets()

        print("--- Initialization Complete: System Ready ---")
    except Exception as e:
        print(f"!! Initialization Error: {e}")


if __name__ == "__main__":
    main()
