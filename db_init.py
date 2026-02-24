import os
import django
import datetime
from django.utils import timezone

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
)


def populate_data():
    print("Starting data initialization...")

    # 1. Create a Professional Faculty & Academic Data
    cse_dept = "Computer Science & Engineering"
    f1 = Faculty.objects.get_or_create(
        name="Dr. Ariful Islam", email="arif@university.edu", department=cse_dept
    )[0]
    f2 = Faculty.objects.get_or_create(
        name="Prof. Sarah Jahan", email="sarah@university.edu", department=cse_dept
    )[0]

    c1 = Course.objects.get_or_create(
        faculty=f1,
        name="Data Structures",
        code="CSE-201",
        description="Fundamental algorithms",
    )[0]
    c2 = Course.objects.get_or_create(
        faculty=f2,
        name="Web Development",
        code="CSE-305",
        description="Fullstack Django development",
    )[0]

    # 2. Create Weekly Class Schedules
    ClassSchedule.objects.get_or_create(
        course=c1, day_of_week="Monday", start_time="09:00", end_time="10:30"
    )
    ClassSchedule.objects.get_or_create(
        course=c2, day_of_week="Tuesday", start_time="11:00", end_time="12:30"
    )

    # 3. Create Bus Routes & Schedules
    r1 = BusRoute.objects.get_or_create(
        route_name="Campus Express",
        start_location="Main Gate",
        end_location="CSE Building",
    )[0]
    r2 = BusRoute.objects.get_or_create(
        route_name="City Shuttle",
        start_location="City Center",
        end_location="University Terminal",
    )[0]

    BusSchedule.objects.get_or_create(
        route=r1, departure_time="08:00", arrival_time="08:20"
    )
    BusSchedule.objects.get_or_create(
        route=r2, departure_time="07:30", arrival_time="08:15"
    )

    # 4. Create 7 Days of Cafeteria Menus
    today = datetime.date.today()
    for i in range(7):
        target_date = today + datetime.timedelta(days=i)
        CafeteriaMenu.objects.get_or_create(
            day=target_date,
            meal_type="Breakfast",
            description="Oatmeal with Fruits & Coffee",
            price=60.00,
        )
        CafeteriaMenu.objects.get_or_create(
            day=target_date,
            meal_type="Lunch",
            description="Chicken Biryani with Salad",
            price=150.00,
        )
        CafeteriaMenu.objects.get_or_create(
            day=target_date,
            meal_type="Dinner",
            description="Grilled Fish and Steamed Veggies",
            price=180.00,
        )

    # 5. Create Clubs and Upcoming Events
    club = Club.objects.get_or_create(
        club_name="Robotics Society", description="Innovating for the future"
    )[0]
    Event.objects.get_or_create(
        club=club,
        event_name="NEOFETCH Hackathon",
        event_date=timezone.now() + datetime.timedelta(days=5),
        description="A 24-hour innovation challenge.",
    )

    # 6. Campus Landmarks
    CampusBuilding.objects.get_or_create(
        building_name="Central Library", latitude=23.456, longitude=91.123
    )
    CampusBuilding.objects.get_or_create(
        building_name="Auditorium", latitude=23.457, longitude=91.124
    )

    print("Data successfully populated!")


if __name__ == "__main__":
    populate_data()
