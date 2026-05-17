from django.core.exceptions import ValidationError
from django.db import models


class JobCategory(models.Model):
	name = models.CharField(max_length=120, unique=True)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Job category"
		verbose_name_plural = "Job categories"

	def __str__(self):
		return self.name


class Skill(models.Model):
	name = models.CharField(max_length=120, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


class Job(models.Model):
	class EmploymentType(models.TextChoices):
		FULL_TIME = "full_time", "Full time"
		PART_TIME = "part_time", "Part time"
		CONTRACT = "contract", "Contract"
		INTERNSHIP = "internship", "Internship"

	class ExperienceLevel(models.TextChoices):
		JUNIOR = "junior", "Junior"
		MID = "mid", "Mid"
		SENIOR = "senior", "Senior"
		LEAD = "lead", "Lead"

	recruiter = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="posted_jobs")
	company = models.ForeignKey("accounts.Company", on_delete=models.SET_NULL, related_name="jobs", null=True, blank=True)
	category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, related_name="jobs", null=True, blank=True)
	title = models.CharField(max_length=255)
	description = models.TextField()
	requirements = models.TextField(blank=True)
	location = models.CharField(max_length=255, blank=True)
	employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
	experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.JUNIOR)
	salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	deadline = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	skills = models.ManyToManyField(Skill, related_name="jobs", blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title

	def clean(self):
		super().clean()
		if self.recruiter_id and not (
			self.recruiter.is_recruiter()
			or self.recruiter.role == self.recruiter.Role.ADMIN
			or self.recruiter.is_staff
			or self.recruiter.is_superuser
		):
			raise ValidationError({"recruiter": "Only recruiters or admin users can post jobs."})
		if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
			raise ValidationError({"salary_max": "salary_max must be greater than or equal to salary_min."})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
