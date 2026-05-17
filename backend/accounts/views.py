from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render

from accounts.models import Company
from applications.models import Application
from assessments.models import Assessment, AssessmentResult, AssessmentSubmission
from jobs.models import Job, Skill

from .forms import AssessmentCreateForm, AssessmentLaunchForm, EmailAuthenticationForm, JobCreateForm, UserRegistrationForm


def _handle_application_status_update(request, applications_queryset):
	if request.method != "POST" or request.POST.get("action") != "update_application_status":
		return False

	application_id = request.POST.get("application_id")
	new_status = request.POST.get("status")
	if new_status not in {Application.Status.ACCEPTED, Application.Status.REJECTED}:
		messages.error(request, "Choose accept or refuse for the application.")
		return True

	try:
		application = applications_queryset.get(pk=application_id)
	except Application.DoesNotExist:
		messages.error(request, "The selected application could not be found.")
		return True

	application.status = new_status
	application.save(update_fields=["status", "updated_at"])
	messages.success(request, f"Application marked as {application.get_status_display().lower()}.")
	return True


def _handle_assessment_submission(request, assessments_queryset):
	if request.method != "POST" or request.POST.get("action") != "submit_assessment":
		return False

	assessment_id = request.POST.get("assessment_id")
	python_code = request.POST.get("python_code", "").strip()
	submission_file = request.FILES.get("submission_file")
	if not python_code and not submission_file:
		messages.error(request, "Upload a PDF or paste Python code before submitting.")
		return True

	try:
		assessment = assessments_queryset.get(pk=assessment_id)
	except Assessment.DoesNotExist:
		messages.error(request, "The selected assessment could not be found.")
		return True

	defaults = {}
	if python_code:
		defaults["python_code"] = python_code
	if submission_file:
		defaults["submission_file"] = submission_file
	AssessmentSubmission.objects.update_or_create(assessment=assessment, defaults=defaults)
	messages.success(request, "Assessment submitted successfully.")
	return True


def landing_page(request):
	return render(request, "accounts/landing.html")


def login_page(request):
	if request.user.is_authenticated:
		return redirect("landing")

	form = EmailAuthenticationForm(request, data=request.POST or None)
	if request.method == "POST" and form.is_valid():
		login(request, form.get_user())
		messages.success(request, "Welcome back to AIDEED.")
		return redirect("landing")

	return render(request, "accounts/login.html", {"form": form})


def register_page(request):
	if request.user.is_authenticated:
		return redirect("landing")

	form = UserRegistrationForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.save()
		login(request, user)
		messages.success(request, "Your account has been created successfully.")
		return redirect("landing")

	return render(request, "accounts/register.html", {"form": form})


def logout_page(request):
	if request.method == "POST":
		logout(request)
		messages.info(request, "You have been signed out.")
	return redirect("landing")


@login_required
def dashboard_page(request):
	user = request.user
	if user.role == "candidate":
		return redirect("candidate-dashboard")
	if user.role == "recruiter" or user.role == "admin" or user.is_staff or user.is_superuser:
		return redirect("recruiter-dashboard")
	return redirect("candidate-dashboard")


@login_required
def candidate_dashboard_page(request):
	if request.user.role != "candidate":
		return redirect("dashboard")

	if request.method == "POST":
		action = request.POST.get("action")
		if action == "apply_job":
			job_id = request.POST.get("job_id")
			cover_letter = request.POST.get("cover_letter", "").strip()
			cv_file = request.FILES.get("cv")
			try:
				job = Job.objects.get(pk=job_id, is_active=True)
				Application.objects.create(candidate=request.user, job=job, cover_letter=cover_letter, cv=cv_file)
				messages.success(request, "Application submitted successfully.")
			except Job.DoesNotExist:
				messages.error(request, "The selected job does not exist.")
			except IntegrityError:
				messages.error(request, "You already applied for this job.")
			except ValidationError as exc:
				messages.error(request, exc.message_dict if hasattr(exc, "message_dict") else str(exc))

			return redirect("candidate-dashboard")
		if _handle_assessment_submission(request, Assessment.objects.select_related("application", "application__candidate").filter(application__candidate=request.user)):
			return redirect("candidate-dashboard")

	stats = {
		"applications": Application.objects.filter(candidate=request.user).count(),
		"assessments": Assessment.objects.filter(application__candidate=request.user).count(),
		"results": AssessmentResult.objects.filter(application__candidate=request.user).count(),
	}

	active_jobs = Job.objects.select_related("company", "recruiter", "category").prefetch_related("skills").filter(is_active=True)[:8]
	assigned_assessments_queryset = Assessment.objects.select_related("application", "application__job", "submission").filter(application__candidate=request.user)
	assessment_notification = assigned_assessments_queryset.filter(application__status=Application.Status.ACCEPTED).first()
	assigned_assessments = assigned_assessments_queryset[:8]
	recent_applications = Application.objects.select_related("job", "job__recruiter").filter(candidate=request.user)[:6]
	return render(
		request,
		"accounts/candidate_dashboard.html",
		{
			"stats": stats,
			"active_jobs": active_jobs,
			"assigned_assessments": assigned_assessments,
			"assessment_notification": assessment_notification,
			"recent_applications": recent_applications,
		},
	)


@login_required
def recruiter_dashboard_page(request):
	if not (request.user.role == "recruiter" or request.user.role == "admin" or request.user.is_staff or request.user.is_superuser):
		return redirect("dashboard")

	is_admin_like = request.user.role == "admin" or request.user.is_staff or request.user.is_superuser
	recruiter_jobs_filter = {} if is_admin_like else {"recruiter": request.user}
	recruiter_applications_filter = {} if is_admin_like else {"job__recruiter": request.user}
	accepted_applications_filter = {} if is_admin_like else {"job__recruiter": request.user, "status": Application.Status.ACCEPTED}

	job_form = JobCreateForm(request.POST or None)
	launch_form = AssessmentLaunchForm(request.POST or None)
	launch_modal_open = False
	assessment_form = AssessmentCreateForm(
		request.POST or None,
		application_queryset=Application.objects.select_related("job", "candidate").filter(**accepted_applications_filter),
	)

	if request.method == "POST":
		action = request.POST.get("action")
		if action == "create_job":
			job_form = JobCreateForm(request.POST)
			if job_form.is_valid():
				job = job_form.save(commit=False)
				company_name = job_form.cleaned_data.get("company_name", "").strip()
				skills_text = job_form.cleaned_data.get("skills_text", "").strip()
				if company_name:
					company_owner = request.user if request.user.is_recruiter() else request.user
					company, _ = Company.objects.get_or_create(owner=company_owner, name=company_name)
					job.company = company
				job.recruiter = request.user
				job.save()
				if skills_text:
					skill_names = [skill_name.strip() for skill_name in skills_text.replace("\n", ",").split(",") if skill_name.strip()]
					skill_objects = []
					for skill_name in skill_names:
						skill, _ = Skill.objects.get_or_create(name=skill_name)
						skill_objects.append(skill)
					job.skills.set(skill_objects)
				messages.success(request, "Job offer published successfully.")
				return redirect("recruiter-dashboard")
		elif action == "create_assessment":
			assessment_form = AssessmentCreateForm(
				request.POST,
				application_queryset=Application.objects.select_related("job", "candidate").filter(job__recruiter=request.user, status=Application.Status.ACCEPTED),
			)
			if assessment_form.is_valid():
				assessment = assessment_form.save(commit=False)
				assessment.save()
				messages.success(request, "Assessment assigned manually.")
				return redirect("recruiter-dashboard")
		elif action == "accept_and_create_assessment":
			launch_modal_open = True
			launch_form = AssessmentLaunchForm(request.POST)
			if launch_form.is_valid():
				application_id = launch_form.cleaned_data["application_id"]
				try:
					application = Application.objects.select_related("job", "candidate").filter(**recruiter_applications_filter).get(pk=application_id)
				except Application.DoesNotExist:
					messages.error(request, "The selected application could not be found.")
				else:
					application.status = Application.Status.ACCEPTED
					application.save(update_fields=["status", "updated_at"])
					Assessment.objects.update_or_create(
						application=application,
						defaults={
							"title": launch_form.cleaned_data["title"],
							"instructions": launch_form.cleaned_data["instructions"],
							"duration_minutes": launch_form.cleaned_data["duration_minutes"],
						},
					)
					messages.success(request, "Applicant accepted and assessment created.")
					return redirect("recruiter-dashboard")
		elif action == "update_application_status":
			if _handle_application_status_update(
				request,
				Application.objects.select_related("job", "candidate").filter(**recruiter_applications_filter),
			):
				return redirect("recruiter-dashboard")

	stats = {
		"jobs": Job.objects.filter(**recruiter_jobs_filter).count(),
		"applications": Application.objects.filter(**recruiter_applications_filter).count(),
		"assessments": Assessment.objects.filter(application__job__recruiter=request.user).count() if not is_admin_like else Assessment.objects.count(),
	}
	recent_jobs = Job.objects.select_related("company", "category").filter(**recruiter_jobs_filter)[:6]
	applications = Application.objects.select_related("candidate", "job").filter(**recruiter_applications_filter).order_by("-applied_at")[:8]
	accepted_applications = Application.objects.select_related("candidate", "job").filter(**accepted_applications_filter)
	assessment_submissions = accepted_applications.filter(assessment__isnull=False).select_related("assessment", "assessment__submission")

	return render(
		request,
		"accounts/recruiter_dashboard.html",
		{
			"stats": stats,
			"job_form": job_form,
			"launch_form": launch_form,
			"launch_modal_open": launch_modal_open,
			"assessment_form": assessment_form,
			"recent_jobs": recent_jobs,
			"applications": applications,
			"accepted_applications": accepted_applications,
			"assessment_submissions": assessment_submissions,
		},
	)


@login_required
def jobs_page(request):
	query = request.GET.get("q", "").strip()
	employment_type = request.GET.get("employment_type", "").strip()

	jobs = Job.objects.select_related("recruiter", "company", "category").prefetch_related("skills").filter(is_active=True)
	if query:
		jobs = jobs.filter(title__icontains=query)
	if employment_type:
		jobs = jobs.filter(employment_type=employment_type)

	if request.method == "POST":
		if request.user.role != "candidate":
			messages.error(request, "Only candidates can apply to jobs.")
			return redirect("jobs-board")

		job_id = request.POST.get("job_id")
		cover_letter = request.POST.get("cover_letter", "").strip()
		cv_file = request.FILES.get("cv")
		try:
			job = Job.objects.get(pk=job_id, is_active=True)
			Application.objects.create(candidate=request.user, job=job, cover_letter=cover_letter, cv=cv_file)
			messages.success(request, "Application submitted successfully.")
		except Job.DoesNotExist:
			messages.error(request, "The selected job does not exist.")
		except IntegrityError:
			messages.error(request, "You already applied for this job.")
		except ValidationError as exc:
			messages.error(request, exc.message_dict if hasattr(exc, "message_dict") else str(exc))

		return redirect("jobs-board")

	context = {
		"jobs": jobs,
		"query": query,
		"employment_type": employment_type,
		"employment_choices": Job.EmploymentType.choices,
	}
	return render(request, "accounts/jobs_board.html", context)

@login_required
def applications_page(request):
	user = request.user
	applications = Application.objects.select_related("candidate", "job", "job__recruiter")
	can_manage = user.role == "recruiter" or user.role == "admin" or user.is_staff or user.is_superuser

	if request.method == "POST" and can_manage:
		if _handle_application_status_update(
			request,
			applications.filter(job__recruiter=user) if user.role == "recruiter" and not (user.role == "admin" or user.is_staff or user.is_superuser) else applications,
		):
			return redirect("applications-board")
	elif request.method == "POST":
		messages.error(request, "Only recruiters or admin users can update application statuses.")
		return redirect("applications-board")

	if user.role == "candidate":
		applications = applications.filter(candidate=user)
	elif user.role == "recruiter":
		applications = applications.filter(job__recruiter=user)

	applications = applications.order_by("-applied_at")
	return render(request, "accounts/applications_board.html", {"applications": applications})


@login_required
def assessments_page(request):
	user = request.user
	assessments = Assessment.objects.select_related("application", "application__candidate", "application__job", "submission")
	results = AssessmentResult.objects.select_related("application", "application__candidate", "application__job")

	if user.role == "candidate":
		assessments = assessments.filter(application__candidate=user)
		results = results.filter(application__candidate=user)
	elif user.role == "recruiter":
		assessments = assessments.filter(application__job__recruiter=user)
		results = results.filter(application__job__recruiter=user)

	context = {
		"assessments": assessments.order_by("-created_at"),
		"results": results.order_by("-evaluated_at"),
	}
	return render(request, "accounts/assessments_board.html", context)
