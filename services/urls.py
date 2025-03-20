from django.urls import path, include
from django.views.generic import TemplateView
from . import views  

urlpatterns = [
    # ✅ Home Page Route
    path('', views.index, name='index'),

    # ✅ Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_view, name='register'),

    # ✅ Cafeteria & Meals
    path('cafeteria/', views.cafeteria_weekly_view, name='cafeteria_main'),
    path('cafeteria/multi-day/', views.cafeteria_weekly_view, name='cafeteria_multi_day'),
    path('meal-booking/', views.create_meal_booking, name='meal_booking'),
    path('booking-success/', TemplateView.as_view(template_name='booking_success.html'), name='booking_success'),

    # ✅ Bus Routes & Schedules
    path('bus-schedules/', views.bus_schedules_view, name='bus_schedules'),

    # ✅ Class Schedules
    path('schedule/', views.class_schedule_view, name='class_schedules'),
    path('schedule/add/', views.add_class_schedule, name='add_schedule'),

    # ✅ Events & Clubs
    path('events/', views.events_view, name='events'),

    # ✅ Campus Map
    path('campus-map/', views.campus_map_view, name='campus_map'),
    path('buildings-json/', views.buildings_json, name='buildings_json'),
]
