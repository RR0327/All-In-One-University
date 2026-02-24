from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CafeteriaMenu, BusRoute, BusSchedule, StudentWallet, Transaction
import datetime
from decimal import Decimal
from .views import process_meal_payment


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


class WalletSystemTest(TestCase):
    def setUp(self):
        """Setup initial user and wallet for testing."""
        self.user = User.objects.create_user(
            username="teststudent", password="password123"
        )
        self.wallet = StudentWallet.objects.create(
            user=self.user, balance=Decimal("500.00")
        )

    def test_successful_meal_payment(self):
        """Verifies credit is deducted and transaction is logged."""
        meal_price = Decimal("150.00")
        # Simulate booking process
        success = process_meal_payment(self.user, meal_price)

        # Refresh from DB
        self.wallet.refresh_from_db()

        self.assertTrue(success)
        self.assertEqual(self.wallet.balance, Decimal("350.00"))
        self.assertEqual(
            Transaction.objects.filter(wallet=self.wallet, tx_type="Debit").count(), 1
        )

    def test_insufficient_funds(self):
        """Ensures payments fail if balance is too low."""
        high_price = Decimal("1000.00")
        success = process_meal_payment(self.user, high_price)

        self.assertFalse(success)
        self.assertEqual(self.wallet.balance, Decimal("500.00"))
