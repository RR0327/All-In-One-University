from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

# ==========================================
# 1. TRANSPORT FEATURE
# ==========================================


class BusRoute(models.Model):
    route_name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Bus Routes"

    def __str__(self):
        return self.route_name


class BusSchedule(models.Model):
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.route.route_name} | {self.departure_time} - {self.arrival_time}"


@receiver(post_save, sender=BusSchedule)
def notify_bus_update(sender, instance, **kwargs):
    """Automated email alerts for transport updates."""
    # This logic triggers automatically whenever a BusSchedule is saved
    recipient_list = list(User.objects.values_list("email", flat=True))
    if recipient_list:
        subject = f"Transport Update: {instance.route.route_name}"
        message = (
            f"Dear User,\n\nThe bus schedule for {instance.route.route_name} has been updated.\n"
            f"New Departure: {instance.departure_time}\n"
            f"New Arrival: {instance.arrival_time}\n\n"
            f"Please check the CampusMS app for further details."
        )
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=True,
        )


# ==========================================
# 2. CAFETERIA & DINING FEATURE
# ==========================================


class CafeteriaMenu(models.Model):
    MEAL_CHOICES = [
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
        ("Snacks", "Snacks"),
    ]
    day = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["day", "meal_type"]
        verbose_name_plural = "Cafeteria Menus"

    def __str__(self):
        return f"{self.day} | {self.meal_type} - {self.description[:30]}"


class MealBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    breakfast = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    dinner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} ({self.date_from} to {self.date_to})"

    def total_days(self):
        return (self.date_to - self.date_from).days + 1


# ==========================================
# 3. ACADEMICS & FACULTY
# ==========================================


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.name} ({self.department})"


class Course(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code}: {self.name}"


class ClassSchedule(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course.name} on {self.day_of_week}"


# ==========================================
# 4. EVENTS & CLUBS
# ==========================================


class Club(models.Model):
    club_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.club_name


class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_date = models.DateTimeField()
    description = models.TextField()

    def __str__(self):
        return f"{self.event_name} - {self.event_date.date()}"


# ==========================================
# 5. CAMPUS NAVIGATION
# ==========================================


class CampusBuilding(models.Model):
    building_name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.building_name


class StudentWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(
        auto_now=True
    )  # Consistent with your transit tracking

    def __str__(self):
        return f"{self.user.username}'s Wallet - ৳{self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("Credit", "Deposit"),
        ("Debit", "Meal Payment"),
    )
    wallet = models.ForeignKey(
        StudentWallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    tx_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        StudentWallet.objects.create(user=instance, balance=500.00)
