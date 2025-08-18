from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        (False, "Student"),
        (True, "Instructor"),
    ]
    is_instructor = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="Register as"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "is_instructor", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-400"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-400"
            }),
            "password1": forms.PasswordInput(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-400"
            }),
            "password2": forms.PasswordInput(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-400"
            }),
        }
