from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class Application(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		REVIEWING = "reviewing", "Reviewing"
		SHORTLISTED = "shortlisted", "Shortlisted"
		ACCEPTED = "accepted", "Accepted"
		REJECTED = "rejected", "Rejected"

	candidate = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="applications")
	job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="applications")
	cover_letter = models.TextField(blank=True)
	cv = models.FileField(upload_to="cvs/", null=True, blank=True, validators=[FileExtensionValidator(["pdf"])])
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	applied_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-applied_at"]
		constraints = [
			models.UniqueConstraint(fields=["candidate", "job"], name="unique_candidate_job_application"),
		]

	def __str__(self):
		return f"{self.candidate.email} -> {self.job.title}"

	def clean(self):
		super().clean()
		if self.candidate and not self.candidate.is_candidate():
			raise ValidationError({"candidate": "Only candidates can apply to jobs."})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
