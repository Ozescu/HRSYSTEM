from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from core.permissions import ApplicationPermission
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationListCreateView(generics.ListCreateAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [ApplicationPermission]

	def get_queryset(self):
		queryset = Application.objects.select_related("candidate", "job", "job__recruiter")
		user = self.request.user
		role = getattr(user, "role", None)

		if not user.is_superuser and role != "admin":
			if role == "candidate":
				queryset = queryset.filter(candidate=user)
			elif role == "recruiter":
				queryset = queryset.filter(job__recruiter=user)
			else:
				queryset = queryset.none()

		status_value = self.request.query_params.get("status")
		job_id = self.request.query_params.get("job")

		if status_value:
			queryset = queryset.filter(status=status_value)
		if job_id:
			queryset = queryset.filter(job_id=job_id)

		return queryset

	def perform_create(self, serializer):
		if getattr(self.request.user, "role", None) != "candidate":
			raise PermissionDenied("Only candidates can create job applications.")
		serializer.save(candidate=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Application.objects.select_related("candidate", "job", "job__recruiter")
	serializer_class = ApplicationSerializer
	permission_classes = [ApplicationPermission]
