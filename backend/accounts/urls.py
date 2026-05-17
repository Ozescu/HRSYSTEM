from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("dashboard/candidate/", views.candidate_dashboard_page, name="candidate-dashboard"),
    path("dashboard/recruiter/", views.recruiter_dashboard_page, name="recruiter-dashboard"),
    path("jobs/", views.jobs_page, name="jobs-board"),
    path("applications/", views.applications_page, name="applications-board"),
    path("assessments/", views.assessments_page, name="assessments-board"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("logout/", views.logout_page, name="logout"),
]
