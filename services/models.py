from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


class bus_schedule(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.title

# User authentication
class UserManager(BaseUserManager):
    def create_user(self, email, name, id_number, contact_information, password=None, role='student', level=None, term=None):
        """Creates and returns a user with the given details."""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            role=role,  # Default role is Student unless specified
            id_number=id_number,
            contact_information=contact_information,
            level=level if role == 'student' else None,
            term=term if role == 'student' else None,
        )
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """Creates and returns a superuser without requiring role, level, or term."""
        user = self.create_user(
            email=email,
            name=name,
            id_number="000000",  # Default ID for admin
            contact_information="Admin User",  # Default contact
            password=password,
            role="admin"  # Admin role assigned automatically
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),  # Add Admin as a Role
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    id_number = models.CharField(max_length=20, unique=True)
    level = models.CharField(max_length=50, null=True, blank=True)  # Optional for non-students
    term = models.CharField(max_length=50, null=True, blank=True)  # Optional for non-students
    contact_information = models.TextField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin


#           
@receiver(post_save, sender=bus_schedule)
def send_schedule_update_notification(sender, instance, **kwargs):
    """
    Sends email notifications to all users when a schedule is updated.
    Triggered automatically whenever a Schedule record is saved.
    """
    from .models import User  # Import here to avoid circular imports

    subject = f"Schedule Update: {instance.title}"
    message = (
        f"Dear User,\n\nThe transport schedule has been updated:\n"
        f"Title: {instance.title}\n"
        f"Description: {instance.description}\n"
        f"Date: {instance.date}\n"
        f"Time: {instance.time}\n\n"
        f"Please log in to check the latest updates.\n\n"
        f"Best Regards,\nCampus Transport Management Team"
    )

    # Gather all user emails
    recipient_list = list(User.objects.values_list('email', flat=True))
    # Send the email
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

# 1) Cafeteria Menu & Meal Schedules
class CafeteriaMenu(models.Model):
    # (Your existing fields)
    day = models.DateField()
    meal_type = models.CharField(max_length=20)  # e.g. "Breakfast", "Lunch", etc.
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # ...any other fields you have...

    def __str__(self):
        return f"{self.day} - {self.meal_type} - {self.description[:20]}..."

class MealBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()

    # Booleans for each meal category (align with your cafeteria approach)
    breakfast = models.BooleanField(default=False)  # Sehri
    lunch = models.BooleanField(default=False)      # Iftar
    dinner = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MealBooking #{self.id} by {self.user.username}"

    def total_days(self):
        """Example helper: total number of days in the selected range."""
        return (self.date_to - self.date_from).days + 1
    
# 2) University Bus Routes & Schedules
class BusRoute(models.Model):
    route_name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)

    def __str__(self):
        return self.route_name

class BusSchedule(models.Model):
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    # You can add fields for notifications, delays, etc.

    def __str__(self):
        return f"{self.route.route_name} - {self.departure_time} to {self.arrival_time}"

# 3) Class Schedules & Faculty Contacts
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.course_name

class ClassSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)  # e.g., "Monday"
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course.course_name} on {self.day_of_week}"

# 4) Event & Club Management
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
        return self.event_name

# 5) (Optional) Campus Navigation - just a placeholder
class CampusBuilding(models.Model):
    building_name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.building_name
