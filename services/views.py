from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
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
    return render(request, "dashboard.html")


# ==========================================
# 2. CAFETERIA LOGIC
# ==========================================


def cafeteria_weekly_view(request):
    menu_items = CafeteriaMenu.objects.all().order_by("day", "meal_type")
    day_groups = OrderedDict()
    for item in menu_items:
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
    return render(request, "booking_success.html")


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
