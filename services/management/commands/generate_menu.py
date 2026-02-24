from django.core.management.base import BaseCommand
from services.models import CafeteriaMenu
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Generates a monthly cafeteria menu automatically"

    def handle(self, *args, **options):
        # Professional meal options for the rotation
        meals = {
            "Breakfast": [
                ("Oatmeal with Fruits & Coffee", 60),
                ("Egg Sandwich & Juice", 50),
                ("Pancakes with Syrup", 70),
            ],
            "Lunch": [
                ("Chicken Biryani with Salad", 150),
                ("Beef Tehari", 160),
                ("Fish Curry with Rice & Lentils", 120),
            ],
            "Dinner": [
                ("Grilled Fish and Steamed Veggies", 180),
                ("Pasta Carbonara", 140),
                ("Chicken Stir-fry", 130),
            ],
            "Snacks": [
                ("Vegetable Pakora", 30),
                ("Chicken Patties", 40),
                ("Fruit Bowl", 50),
            ],
        }

        start_date = date.today()
        count = 0

        # Generate for the next 30 days
        for i in range(30):
            current_day = start_date + timedelta(days=i)
            for meal_type, options_list in meals.items():
                desc, price = random.choice(options_list)

                _, created = CafeteriaMenu.objects.get_or_create(
                    day=current_day,
                    meal_type=meal_type,
                    defaults={"description": desc, "price": price},
                )
                if created:
                    count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {count} menu items for the month!"
            )
        )
