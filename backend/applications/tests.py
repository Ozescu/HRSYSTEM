from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from applications.models import Application
from jobs.models import Job


class ApplicationPermissionTests(APITestCase):
	def setUp(self):
		self.recruiter = User.objects.create_user(
			email="recruiter@app.com",
			password="pass1234",
			role="recruiter",
		)
		self.other_recruiter = User.objects.create_user(
			email="other-recruiter@app.com",
			password="pass1234",
			role="recruiter",
		)
		self.candidate = User.objects.create_user(
			email="candidate@app.com",
			password="pass1234",
			role="candidate",
		)
		self.other_candidate = User.objects.create_user(
			email="other-candidate@app.com",
			password="pass1234",
			role="candidate",
		)

		self.job = Job.objects.create(
			recruiter=self.recruiter,
			title="Backend Role",
			description="Main backend job",
		)
		self.other_job = Job.objects.create(
			recruiter=self.other_recruiter,
			title="Other Role",
			description="Other backend job",
		)

		self.application_list_url = reverse("application-list-create")

	def test_candidate_can_create_application(self):
		self.client.force_authenticate(user=self.candidate)
		response = self.client.post(
			self.application_list_url,
			{"job": self.job.id, "cover_letter": "I am interested"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Application.objects.count(), 1)

	def test_candidate_can_create_application_with_pdf_cv(self):
		self.client.force_authenticate(user=self.candidate)
		cv_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test cv", content_type="application/pdf")
		response = self.client.post(
			self.application_list_url,
			{"job": self.job.id, "cover_letter": "I am interested", "cv": cv_file},
			format="multipart",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Application.objects.count(), 1)
		self.assertTrue(Application.objects.first().cv.name.endswith(".pdf"))

	def test_recruiter_cannot_create_application(self):
		self.client.force_authenticate(user=self.recruiter)
		response = self.client.post(
			self.application_list_url,
			{"job": self.job.id, "cover_letter": "Attempt"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_candidate_sees_only_own_applications(self):
		own = Application.objects.create(candidate=self.candidate, job=self.job)
		Application.objects.create(candidate=self.other_candidate, job=self.job)

		self.client.force_authenticate(user=self.candidate)
		response = self.client.get(self.application_list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["id"], own.id)

	def test_recruiter_sees_only_applications_for_their_jobs(self):
		own = Application.objects.create(candidate=self.candidate, job=self.job)
		Application.objects.create(candidate=self.other_candidate, job=self.other_job)

		self.client.force_authenticate(user=self.recruiter)
		response = self.client.get(self.application_list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["id"], own.id)

	def test_candidate_cannot_change_application_status(self):
		application = Application.objects.create(candidate=self.candidate, job=self.job)
		detail_url = reverse("application-detail", kwargs={"pk": application.id})

		self.client.force_authenticate(user=self.candidate)
		response = self.client.patch(detail_url, {"status": "accepted"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_recruiter_can_change_application_status_for_own_job(self):
		application = Application.objects.create(candidate=self.candidate, job=self.job)
		detail_url = reverse("application-detail", kwargs={"pk": application.id})

		self.client.force_authenticate(user=self.recruiter)
		response = self.client.patch(detail_url, {"status": "reviewing"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_recruiter_can_accept_or_refuse_own_application(self):
		application = Application.objects.create(candidate=self.candidate, job=self.job)
		detail_url = reverse("application-detail", kwargs={"pk": application.id})

		self.client.force_authenticate(user=self.recruiter)
		response = self.client.patch(detail_url, {"status": "rejected"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		application.refresh_from_db()
		self.assertEqual(application.status, Application.Status.REJECTED)
