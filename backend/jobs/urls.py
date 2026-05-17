from django.urls import path

from .views import (
    JobCategoryDetailView,
    JobCategoryListCreateView,
    JobDetailView,
    JobListCreateView,
    SkillDetailView,
    SkillListCreateView,
)

urlpatterns = [
    path("categories/", JobCategoryListCreateView.as_view(), name="job-category-list-create"),
    path("categories/<int:pk>/", JobCategoryDetailView.as_view(), name="job-category-detail"),
    path("skills/", SkillListCreateView.as_view(), name="skill-list-create"),
    path("skills/<int:pk>/", SkillDetailView.as_view(), name="skill-detail"),
    path("", JobListCreateView.as_view(), name="job-list-create"),
    path("<int:pk>/", JobDetailView.as_view(), name="job-detail"),
]
