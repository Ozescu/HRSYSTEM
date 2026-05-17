from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from assessments.models import Assessment
from applications.models import Application
from jobs.models import Job

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


class JobCreateForm(forms.ModelForm):
    company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"placeholder": "Company name"}))
    skills_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Python, Django, REST"}),
        help_text="Enter skills separated by commas.",
    )

    class Meta:
        model = Job
        fields = (
            "title",
            "description",
            "requirements",
            "location",
            "employment_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "deadline",
            "category",
            "is_active",
        )
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "requirements": forms.Textarea(attrs={"rows": 3}),
        }


class AssessmentCreateForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ("application", "title", "instructions", "duration_minutes")
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        application_queryset = kwargs.pop("application_queryset", Application.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["application"].queryset = application_queryset


class AssessmentLaunchForm(forms.Form):
    application_id = forms.IntegerField(widget=forms.HiddenInput())
    title = forms.CharField(max_length=255)
    instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
    duration_minutes = forms.IntegerField(min_value=1, initial=30)
