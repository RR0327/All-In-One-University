from django.contrib import admin
from .models import (
    BusRoute,
    BusSchedule,
    CafeteriaMenu,
    MealBooking,
    Faculty,
    Course,
    ClassSchedule,
    Club,
    Event,
    CampusBuilding,
)


@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    list_display = ("route", "departure_time", "arrival_time", "last_updated")
    list_filter = ("route",)
    search_fields = ("route__route_name",)


@admin.register(CafeteriaMenu)
class CafeteriaMenuAdmin(admin.ModelAdmin):
    list_display = ("day", "meal_type", "price", "description")
    list_filter = ("day", "meal_type")
    date_hierarchy = "day"


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ("course", "day_of_week", "start_time", "end_time")
    list_filter = ("day_of_week", "course")


# Registering standard models
admin.site.register(BusRoute)
admin.site.register(MealBooking)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(CampusBuilding)
