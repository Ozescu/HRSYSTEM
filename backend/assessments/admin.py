from django.contrib import admin

from .models import Assessment, AssessmentResult, AssessmentSubmission, CandidateAnswer, Choice, Question


class ChoiceInline(admin.TabularInline):
	model = Choice
	extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("assessment", "order", "question_type", "max_score")
	list_filter = ("question_type",)
	inlines = [ChoiceInline]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
	list_display = ("title", "application", "duration_minutes", "created_at")
	search_fields = ("title", "application__candidate__email", "application__job__title")


@admin.register(CandidateAnswer)
class CandidateAnswerAdmin(admin.ModelAdmin):
	list_display = ("application", "question", "selected_choice", "score", "submitted_at")
	search_fields = ("application__candidate__email", "question__text")


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
	list_display = ("application", "total_score", "percentage", "passed", "evaluated_at")


@admin.register(AssessmentSubmission)
class AssessmentSubmissionAdmin(admin.ModelAdmin):
	list_display = ("assessment", "submitted_at", "updated_at")
	search_fields = ("assessment__application__candidate__email", "assessment__application__job__title")
