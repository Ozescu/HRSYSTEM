from django.urls import path

from .views import (
    AssessmentDetailView,
    AssessmentListCreateView,
    AssessmentResultDetailView,
    AssessmentResultListCreateView,
    AssessmentSubmissionDetailView,
    AssessmentSubmissionListCreateView,
    CandidateAnswerDetailView,
    CandidateAnswerListCreateView,
    ChoiceListCreateView,
    QuestionListCreateView,
)

urlpatterns = [
    path("", AssessmentListCreateView.as_view(), name="assessment-list-create"),
    path("<int:pk>/", AssessmentDetailView.as_view(), name="assessment-detail"),
    path("questions/", QuestionListCreateView.as_view(), name="question-list-create"),
    path("choices/", ChoiceListCreateView.as_view(), name="choice-list-create"),
    path("answers/", CandidateAnswerListCreateView.as_view(), name="answer-list-create"),
    path("answers/<int:pk>/", CandidateAnswerDetailView.as_view(), name="answer-detail"),
    path("results/", AssessmentResultListCreateView.as_view(), name="result-list-create"),
    path("results/<int:pk>/", AssessmentResultDetailView.as_view(), name="result-detail"),
    path("submissions/", AssessmentSubmissionListCreateView.as_view(), name="submission-list-create"),
    path("submissions/<int:pk>/", AssessmentSubmissionDetailView.as_view(), name="submission-detail"),
]
