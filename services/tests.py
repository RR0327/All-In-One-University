from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CafeteriaMenu, BusRoute, BusSchedule
import datetime


class UniversityAppTests(TestCase):

    def setUp(self):
        # Set up a test user
        self.user = User.objects.create_user(
            username="teststudent", password="password123"
        )

        # Set up test data for features
        self.route = BusRoute.objects.create(
            route_name="Campus Express",
            start_location="Main Gate",
            end_location="Hostel A",
        )
        self.menu = CafeteriaMenu.objects.create(
            day=datetime.date.today(),
            meal_type="Lunch",
            description="Chicken Curry and Rice",
            price=120.00,
        )

    # --- Test Authentication ---
    def test_login_access(self):
        """Verify that the dashboard requires login."""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    # --- Test Cafeteria Logic ---
    def test_cafeteria_view(self):
        """Verify the cafeteria menu displays correctly."""
        response = self.client.get(reverse("cafeteria_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chicken Curry")

    # --- Test Transport Data ---
    def test_bus_route_creation(self):
        """Verify bus route models work."""
        self.assertEqual(str(self.route), "Campus Express")
