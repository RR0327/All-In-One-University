from django.contrib import admin
from .models import (
    CafeteriaMenu, 
    BusRoute, 
    bus_schedule,
    Faculty, 
    Course, 
    ClassSchedule, 
    Club, 
    bus_schedule,
    Event, 
    CampusBuilding
)

class BusScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'updated_at')
    search_fields = ('title', 'date')


admin.site.register(bus_schedule, BusScheduleAdmin)
admin.site.register(CafeteriaMenu)
admin.site.register(BusRoute)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(ClassSchedule)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(CampusBuilding)
