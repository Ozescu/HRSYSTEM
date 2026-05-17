from rest_framework import generics

from core.permissions import JobPermission, ReadOnlyOrRecruiterAdmin
from .models import Job, JobCategory, Skill
from .serializers import JobCategorySerializer, JobSerializer, SkillSerializer


class JobCategoryListCreateView(generics.ListCreateAPIView):
	queryset = JobCategory.objects.all()
	serializer_class = JobCategorySerializer
	permission_classes = [ReadOnlyOrRecruiterAdmin]


class JobCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = JobCategory.objects.all()
	serializer_class = JobCategorySerializer
	permission_classes = [ReadOnlyOrRecruiterAdmin]


class SkillListCreateView(generics.ListCreateAPIView):
	queryset = Skill.objects.all()
	serializer_class = SkillSerializer
	permission_classes = [ReadOnlyOrRecruiterAdmin]


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Skill.objects.all()
	serializer_class = SkillSerializer
	permission_classes = [ReadOnlyOrRecruiterAdmin]


class JobListCreateView(generics.ListCreateAPIView):
	serializer_class = JobSerializer
	permission_classes = [JobPermission]

	def get_queryset(self):
		queryset = Job.objects.select_related("recruiter", "company", "category").prefetch_related("skills")
		is_active = self.request.query_params.get("is_active")
		category = self.request.query_params.get("category")
		employment_type = self.request.query_params.get("employment_type")

		if is_active in {"true", "false"}:
			queryset = queryset.filter(is_active=(is_active == "true"))
		if category:
			queryset = queryset.filter(category_id=category)
		if employment_type:
			queryset = queryset.filter(employment_type=employment_type)

		return queryset

	def perform_create(self, serializer):
		serializer.save(recruiter=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Job.objects.select_related("recruiter", "company", "category").prefetch_related("skills")
	serializer_class = JobSerializer
	permission_classes = [JobPermission]
