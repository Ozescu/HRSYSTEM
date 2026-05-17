from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from core.permissions import AssessmentPermission, AssessmentResultPermission, AssessmentSubmissionPermission, CandidateAnswerPermission
from .models import Assessment, AssessmentResult, AssessmentSubmission, CandidateAnswer, Choice, Question
from .serializers import (
	AssessmentResultSerializer,
	AssessmentSerializer,
	AssessmentSubmissionSerializer,
	CandidateAnswerSerializer,
	ChoiceSerializer,
	QuestionSerializer,
)


class AssessmentListCreateView(generics.ListCreateAPIView):
	serializer_class = AssessmentSerializer
	permission_classes = [AssessmentPermission]

	def get_queryset(self):
		queryset = Assessment.objects.select_related("application", "application__job", "application__candidate")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			return queryset
		if role == "recruiter":
			return queryset.filter(application__job__recruiter=user)
		if role == "candidate":
			return queryset.filter(application__candidate=user)
		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		application = serializer.validated_data["application"]

		if role not in {"recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("Only recruiters or admins can create assessments.")

		if role == "recruiter" and application.job.recruiter_id != user.id:
			raise PermissionDenied("You can only create assessments for your own job applications.")

		serializer.save()


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Assessment.objects.select_related("application", "application__job", "application__candidate")
	serializer_class = AssessmentSerializer
	permission_classes = [AssessmentPermission]


class QuestionListCreateView(generics.ListCreateAPIView):
	serializer_class = QuestionSerializer
	permission_classes = [AssessmentPermission]

	def get_queryset(self):
		queryset = Question.objects.select_related("assessment")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			pass
		elif role == "recruiter":
			queryset = queryset.filter(assessment__application__job__recruiter=user)
		elif role == "candidate":
			queryset = queryset.filter(assessment__application__candidate=user)
		else:
			queryset = queryset.none()

		assessment_id = self.request.query_params.get("assessment")
		if assessment_id:
			queryset = queryset.filter(assessment_id=assessment_id)
		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		assessment = serializer.validated_data["assessment"]

		if role not in {"recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("Only recruiters or admins can create questions.")

		if role == "recruiter" and assessment.application.job.recruiter_id != user.id:
			raise PermissionDenied("You can only add questions to your own assessments.")

		serializer.save()


class ChoiceListCreateView(generics.ListCreateAPIView):
	serializer_class = ChoiceSerializer
	permission_classes = [AssessmentPermission]

	def get_queryset(self):
		queryset = Choice.objects.select_related("question")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			pass
		elif role == "recruiter":
			queryset = queryset.filter(question__assessment__application__job__recruiter=user)
		elif role == "candidate":
			queryset = queryset.filter(question__assessment__application__candidate=user)
		else:
			queryset = queryset.none()

		question_id = self.request.query_params.get("question")
		if question_id:
			queryset = queryset.filter(question_id=question_id)
		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		question = serializer.validated_data["question"]

		if role not in {"recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("Only recruiters or admins can create choices.")

		if role == "recruiter" and question.assessment.application.job.recruiter_id != user.id:
			raise PermissionDenied("You can only add choices to your own assessments.")

		serializer.save()


class CandidateAnswerListCreateView(generics.ListCreateAPIView):
	serializer_class = CandidateAnswerSerializer
	permission_classes = [CandidateAnswerPermission]

	def get_queryset(self):
		queryset = CandidateAnswer.objects.select_related("application", "question", "selected_choice")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			pass
		elif role == "recruiter":
			queryset = queryset.filter(application__job__recruiter=user)
		elif role == "candidate":
			queryset = queryset.filter(application__candidate=user)
		else:
			queryset = queryset.none()

		application_id = self.request.query_params.get("application")
		if application_id:
			queryset = queryset.filter(application_id=application_id)
		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		application = serializer.validated_data["application"]

		if role == "candidate" and application.candidate_id != user.id:
			raise PermissionDenied("Candidates can only answer their own assessments.")

		if role == "recruiter" and application.job.recruiter_id != user.id:
			raise PermissionDenied("Recruiters can only manage answers for their own job applications.")

		if role not in {"candidate", "recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("You do not have permission to create answers.")

		serializer.save()


class CandidateAnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = CandidateAnswer.objects.select_related("application", "question", "selected_choice")
	serializer_class = CandidateAnswerSerializer
	permission_classes = [CandidateAnswerPermission]


class AssessmentResultListCreateView(generics.ListCreateAPIView):
	serializer_class = AssessmentResultSerializer
	permission_classes = [AssessmentResultPermission]

	def get_queryset(self):
		queryset = AssessmentResult.objects.select_related("application", "application__job", "application__candidate")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			return queryset
		if role == "recruiter":
			return queryset.filter(application__job__recruiter=user)
		if role == "candidate":
			return queryset.filter(application__candidate=user)
		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		application = serializer.validated_data["application"]

		if role not in {"recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("Only recruiters or admins can publish results.")

		if role == "recruiter" and application.job.recruiter_id != user.id:
			raise PermissionDenied("You can only publish results for your own job applications.")

		serializer.save()


class AssessmentResultDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = AssessmentResult.objects.select_related("application")
	serializer_class = AssessmentResultSerializer
	permission_classes = [AssessmentResultPermission]


class AssessmentSubmissionListCreateView(generics.ListCreateAPIView):
	serializer_class = AssessmentSubmissionSerializer
	permission_classes = [AssessmentSubmissionPermission]

	def get_queryset(self):
		queryset = AssessmentSubmission.objects.select_related("assessment", "assessment__application", "assessment__application__candidate", "assessment__application__job")
		user = self.request.user
		role = getattr(user, "role", None)

		if user.is_superuser or role == "admin":
			return queryset
		if role == "recruiter":
			return queryset.filter(assessment__application__job__recruiter=user)
		if role == "candidate":
			return queryset.filter(assessment__application__candidate=user)
		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		role = getattr(user, "role", None)
		assessment = serializer.validated_data["assessment"]

		if role == "candidate" and assessment.application.candidate_id != user.id:
			raise PermissionDenied("Candidates can only submit their own assessments.")

		if role == "recruiter" and assessment.application.job.recruiter_id != user.id:
			raise PermissionDenied("Recruiters can only manage submissions for their own job applications.")

		if role not in {"candidate", "recruiter", "admin"} and not user.is_superuser:
			raise PermissionDenied("You do not have permission to create submissions.")

		serializer.save()


class AssessmentSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = AssessmentSubmission.objects.select_related("assessment", "assessment__application", "assessment__application__candidate", "assessment__application__job")
	serializer_class = AssessmentSubmissionSerializer
	permission_classes = [AssessmentSubmissionPermission]
