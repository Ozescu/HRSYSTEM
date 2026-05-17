from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from applications.models import Application
from assessments.models import Assessment, CandidateAnswer, Choice, Question
from jobs.models import Job


class AssessmentPermissionTests(APITestCase):
	def setUp(self):
		self.recruiter = User.objects.create_user(
			email="recruiter@assessment.com",
			password="pass1234",
			role="recruiter",
		)
		self.other_recruiter = User.objects.create_user(
			email="other-recruiter@assessment.com",
			password="pass1234",
			role="recruiter",
		)
		self.candidate = User.objects.create_user(
			email="candidate@assessment.com",
			password="pass1234",
			role="candidate",
		)
		self.other_candidate = User.objects.create_user(
			email="other-candidate@assessment.com",
			password="pass1234",
			role="candidate",
		)

		self.job = Job.objects.create(
			recruiter=self.recruiter,
			title="Assessment Job",
			description="Job with assessment",
		)
		self.other_job = Job.objects.create(
			recruiter=self.other_recruiter,
			title="Other Assessment Job",
			description="Other job",
		)

		self.application = Application.objects.create(candidate=self.candidate, job=self.job)
		self.other_application = Application.objects.create(candidate=self.other_candidate, job=self.other_job)

		self.assessment_list_url = reverse("assessment-list-create")
		self.result_list_url = reverse("result-list-create")
		self.answer_list_url = reverse("answer-list-create")
		self.submission_list_url = reverse("submission-list-create")

	def test_owner_recruiter_can_create_assessment(self):
		self.client.force_authenticate(user=self.recruiter)
		response = self.client.post(
			self.assessment_list_url,
			{
				"application": self.application.id,
				"title": "Python Test",
				"instructions": "Answer all",
				"duration_minutes": 20,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_non_owner_recruiter_cannot_create_assessment(self):
		self.client.force_authenticate(user=self.other_recruiter)
		response = self.client.post(
			self.assessment_list_url,
			{
				"application": self.application.id,
				"title": "Forbidden Test",
				"duration_minutes": 20,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_candidate_only_sees_own_assessments(self):
		own_assessment = Assessment.objects.create(application=self.application, title="Own Assessment")
		Assessment.objects.create(application=self.other_application, title="Other Assessment")

		self.client.force_authenticate(user=self.candidate)
		response = self.client.get(self.assessment_list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["id"], own_assessment.id)

	def test_candidate_cannot_create_result(self):
		self.client.force_authenticate(user=self.candidate)
		response = self.client.post(
			self.result_list_url,
			{
				"application": self.application.id,
				"total_score": "10.00",
				"percentage": "80.00",
				"passed": True,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_candidate_cannot_set_score_in_answer(self):
		assessment = Assessment.objects.create(application=self.application, title="Scoring Assessment")
		question = Question.objects.create(assessment=assessment, text="What is Python?")
		choice = Choice.objects.create(question=question, text="Programming language", is_correct=True)

		self.client.force_authenticate(user=self.candidate)
		response = self.client.post(
			self.answer_list_url,
			{
				"application": self.application.id,
				"question": question.id,
				"selected_choice": choice.id,
				"score": "5.00",
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(CandidateAnswer.objects.count(), 0)

	def test_candidate_can_submit_pdf_assessment(self):
		assessment = Assessment.objects.create(application=self.application, title="PDF Assessment")
		self.client.force_authenticate(user=self.candidate)
		pdf_file = SimpleUploadedFile("answer.pdf", b"%PDF-1.4 test", content_type="application/pdf")
		response = self.client.post(
			self.submission_list_url,
			{"assessment": assessment.id, "submission_file": pdf_file},
			format="multipart",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_candidate_can_submit_python_code_assessment(self):
		assessment = Assessment.objects.create(application=self.application, title="Code Assessment")
		self.client.force_authenticate(user=self.candidate)
		response = self.client.post(
			self.submission_list_url,
			{"assessment": assessment.id, "python_code": "print('hello')"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
