from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .managers import UserManager


class User(AbstractUser):
	class Role(models.TextChoices):
		CANDIDATE = "candidate", "Candidate"
		RECRUITER = "recruiter", "Recruiter"
		ADMIN = "admin", "Admin"

	username = None
	email = models.EmailField("Email address", unique=True)
	role = models.CharField("Role", max_length=20, choices=Role.choices, default=Role.CANDIDATE, db_index=True)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	objects = UserManager()

	class Meta:
		verbose_name = "User"
		verbose_name_plural = "Users"

	def __str__(self):
		full_name = f"{self.first_name} {self.last_name}".strip()
		return full_name or self.email

	def is_candidate(self):
		return self.role == self.Role.CANDIDATE

	def is_recruiter(self):
		return self.role == self.Role.RECRUITER


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="User")
	bio = models.TextField("Bio", blank=True)
	phone_number = models.CharField("Phone number", max_length=30, blank=True)
	profile_picture = models.ImageField("Profile picture", upload_to="profiles/", blank=True, null=True)
	linkedin_url = models.URLField("LinkedIn URL", blank=True)
	github_url = models.URLField("GitHub URL", blank=True)
	created_at = models.DateTimeField("Created at", auto_now_add=True)

	class Meta:
		verbose_name = "Profile"
		verbose_name_plural = "Profiles"

	def __str__(self):
		return f"Profile - {self.user.email}"


class Company(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="companies", verbose_name="Owner")
	name = models.CharField("Company name", max_length=255)
	description = models.TextField("Description", blank=True)
	website = models.URLField("Website", blank=True)
	location = models.CharField("Location", max_length=255, blank=True)
	logo = models.ImageField("Logo", upload_to="companies/", blank=True, null=True)
	created_at = models.DateTimeField("Created at", auto_now_add=True)

	class Meta:
		verbose_name = "Company"
		verbose_name_plural = "Companies"

	def __str__(self):
		return self.name

	def clean(self):
		super().clean()
		if self.owner and not self.owner.is_recruiter():
			raise ValidationError({"owner": "Only recruiters can own companies."})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
