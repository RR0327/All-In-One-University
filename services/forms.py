from django import forms
from django.contrib.auth.models import User
from .models import MealBooking


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control bg-black border-secondary text-white",
                "placeholder": "Create a password",
            }
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control bg-black border-secondary text-white",
                "placeholder": "Confirm your password",
            }
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control bg-black border-secondary text-white",
                    "placeholder": "Username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control bg-black border-secondary text-white",
                    "placeholder": "Email Address",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data


class MealBookingForm(forms.ModelForm):
    class Meta:
        model = MealBooking
        fields = ["date_from", "date_to", "breakfast", "lunch", "dinner"]
        widgets = {
            "date_from": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control bg-black border-secondary text-white",
                }
            ),
            "date_to": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control bg-black border-secondary text-white",
                }
            ),
            "breakfast": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "lunch": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "dinner": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
