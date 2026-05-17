from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class Assessment(models.Model):
	application = models.OneToOneField("applications.Application", on_delete=models.CASCADE, related_name="assessment")
	title = models.CharField(max_length=255)
	instructions = models.TextField(blank=True)
	duration_minutes = models.PositiveIntegerField(default=30)
	starts_at = models.DateTimeField(null=True, blank=True)
	ends_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Assessment - {self.application.job.title}"

	def clean(self):
		super().clean()
		if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
			raise ValidationError({"ends_at": "ends_at must be later than starts_at."})


class Question(models.Model):
	class Type(models.TextChoices):
		MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
		TEXT = "text", "Text"

	assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")
	text = models.TextField()
	question_type = models.CharField(max_length=20, choices=Type.choices, default=Type.MULTIPLE_CHOICE)
	max_score = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
	order = models.PositiveIntegerField(default=1)

	class Meta:
		ordering = ["order", "id"]

	def __str__(self):
		return f"Q{self.order} - {self.assessment.title}"


class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
	text = models.CharField(max_length=255)
	is_correct = models.BooleanField(default=False)

	def __str__(self):
		return self.text


class CandidateAnswer(models.Model):
	application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="answers")
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
	selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name="selected_in_answers")
	text_answer = models.TextField(blank=True)
	score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	submitted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["application", "question"], name="unique_application_question_answer"),
		]

	def __str__(self):
		return f"Answer - {self.application_id} / {self.question_id}"

	def clean(self):
		super().clean()
		if self.selected_choice and self.selected_choice.question_id != self.question_id:
			raise ValidationError({"selected_choice": "Selected choice must belong to the same question."})


class AssessmentResult(models.Model):
	application = models.OneToOneField("applications.Application", on_delete=models.CASCADE, related_name="assessment_result")
	total_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
	percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	passed = models.BooleanField(default=False)
	evaluated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Result - {self.application_id}"


class AssessmentSubmission(models.Model):
	assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="submission")
	submission_file = models.FileField(
		upload_to="assessment_submissions/",
		null=True,
		blank=True,
		validators=[FileExtensionValidator(["pdf"])],
	)
	python_code = models.TextField(blank=True)
	submitted_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-submitted_at"]

	def __str__(self):
		return f"Submission - {self.assessment_id}"

	def clean(self):
		super().clean()
		if not self.submission_file and not self.python_code.strip():
			raise ValidationError({"python_code": "Submit either a PDF file or Python code."})

	def save(self, *args, **kwargs):
		if self.python_code:
			self.python_code = self.python_code.strip()
		self.full_clean()
		super().save(*args, **kwargs)
