from django.core.management.base import BaseCommand
from services.models import BusRoute, BusSchedule
from datetime import time


class Command(BaseCommand):
    help = "Generates a full week of bus schedules automatically"

    def handle(self, *args, **options):
        # Retrieve all existing routes from the database
        routes = BusRoute.objects.all()

        # Bangladesh Standard University Shifts
        slots = [
            (time(7, 30), time(8, 15)),  # Early Morning
            (time(8, 30), time(9, 15)),  # Morning
            (time(14, 0), time(14, 45)),  # Afternoon Return
            (time(16, 30), time(17, 15)),  # Evening Return
        ]

        count = 0
        for route in routes:  # We use 'route' here
            for dep, arr in slots:
                # Fixed: Changed 'row' to 'route' to match the loop
                _, created = BusSchedule.objects.get_or_create(
                    route=route, departure_time=dep, arrival_time=arr
                )
                if created:
                    count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} new schedules!")
        )
