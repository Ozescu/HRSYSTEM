from django.contrib import admin

from .models import Job, JobCategory, Skill


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
	list_display = ("title", "recruiter", "employment_type", "location", "is_active", "created_at")
	list_filter = ("employment_type", "experience_level", "is_active", "created_at")
	search_fields = ("title", "recruiter__email", "company__name")
	filter_horizontal = ("skills",)
