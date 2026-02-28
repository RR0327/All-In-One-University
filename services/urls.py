from django.urls import path
from . import views

urlpatterns = [
    # --- Home & Authentication ---
    path("", views.index, name="index"),
    path("login/", views.user_login_view, name="login"),
    path("logout/", views.user_logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # --- Cafeteria & Meals ---
    path("cafeteria/", views.cafeteria_weekly_view, name="cafeteria_main"),
    path(
        "cafeteria/multi-day/", views.cafeteria_weekly_view, name="cafeteria_multi_day"
    ),
    path("meal-booking/", views.create_meal_booking, name="meal_booking"),
    path("booking-success/", views.booking_success_view, name="booking_success"),
    # --- Transport & Bus Schedules ---
    path("bus-schedules/", views.bus_schedules_view, name="bus_schedules"),
    # --- Academics & Class Schedules ---
    path("schedule/", views.class_schedules_view, name="class_schedules"),
    path("add-schedule/", views.add_class_schedule, name="add_class_schedule"),
    # --- Events & Clubs ---
    path("events/", views.events_view, name="events"),
    # --- Campus Navigation ---
    path("campus-map/", views.campus_map_view, name="campus_map"),
    path("api/buildings/", views.buildings_json, name="buildings_json"),
    path(
        "download-meal-summary/",
        views.download_meal_summary,
        name="download_meal_summary",
    ),
    path("payment/initiate/", views.initiate_payment, name="initiate_payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("profile/update/", views.profile_update, name="profile_update"),
    path("wallet/history/", views.transaction_history, name="transaction_history"),
]
