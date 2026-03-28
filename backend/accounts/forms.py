from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "you@aideed.com"})
        self.fields["first_name"].widget.attrs.update({"placeholder": "First name"})
        self.fields["last_name"].widget.attrs.update({"placeholder": "Last name"})


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True, "placeholder": "you@aideed.com"}))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
