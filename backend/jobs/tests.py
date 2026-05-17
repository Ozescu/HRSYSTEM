from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from jobs.models import Job


class JobPermissionTests(APITestCase):
	def setUp(self):
		self.recruiter = User.objects.create_user(
			email="recruiter@example.com",
			password="pass1234",
			role="recruiter",
		)
		self.other_recruiter = User.objects.create_user(
			email="other-recruiter@example.com",
			password="pass1234",
			role="recruiter",
		)
		self.candidate = User.objects.create_user(
			email="candidate@example.com",
			password="pass1234",
			role="candidate",
		)

		self.job_list_url = reverse("job-list-create")

	def test_public_can_read_jobs(self):
		response = self.client.get(self.job_list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_candidate_cannot_create_job(self):
		self.client.force_authenticate(user=self.candidate)
		payload = {
			"title": "Backend Developer",
			"description": "Build APIs",
		}
		response = self.client.post(self.job_list_url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_recruiter_can_create_job(self):
		self.client.force_authenticate(user=self.recruiter)
		payload = {
			"title": "Backend Developer",
			"description": "Build APIs",
		}
		response = self.client.post(self.job_list_url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Job.objects.count(), 1)
		self.assertEqual(Job.objects.first().recruiter_id, self.recruiter.id)

	def test_recruiter_cannot_edit_other_recruiter_job(self):
		foreign_job = Job.objects.create(
			recruiter=self.other_recruiter,
			title="Foreign Job",
			description="Owned by another recruiter",
		)
		self.client.force_authenticate(user=self.recruiter)

		detail_url = reverse("job-detail", kwargs={"pk": foreign_job.pk})
		response = self.client.patch(detail_url, {"title": "Updated"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
