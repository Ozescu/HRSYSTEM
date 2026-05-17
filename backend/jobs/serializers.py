from rest_framework import serializers

from .models import Job, JobCategory, Skill


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ("id", "name", "description")


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name")


class JobSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, required=False)
    recruiter_email = serializers.EmailField(source="recruiter.email", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "recruiter",
            "recruiter_email",
            "company",
            "category",
            "title",
            "description",
            "requirements",
            "location",
            "employment_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "deadline",
            "is_active",
            "skills",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "recruiter", "created_at", "updated_at")
