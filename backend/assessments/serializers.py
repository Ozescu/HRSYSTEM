from rest_framework import serializers

from .models import Assessment, AssessmentResult, AssessmentSubmission, CandidateAnswer, Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "question", "text", "is_correct")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "assessment", "text", "question_type", "max_score", "order", "choices")


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = (
            "id",
            "application",
            "title",
            "instructions",
            "duration_minutes",
            "starts_at",
            "ends_at",
            "created_at",
            "questions",
        )
        read_only_fields = ("id", "created_at")


class CandidateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateAnswer
        fields = (
            "id",
            "application",
            "question",
            "selected_choice",
            "text_answer",
            "score",
            "submitted_at",
        )
        read_only_fields = ("id", "submitted_at")

    def validate(self, attrs):
        request = self.context.get("request")
        if not request:
            return attrs

        user = request.user
        if user.is_authenticated and getattr(user, "role", None) == "candidate" and "score" in attrs:
            raise serializers.ValidationError({"score": "Candidates cannot set or edit score."})

        return attrs


class AssessmentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentResult
        fields = ("id", "application", "total_score", "percentage", "passed", "evaluated_at")
        read_only_fields = ("id", "evaluated_at")


class AssessmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSubmission
        fields = ("id", "assessment", "submission_file", "python_code", "submitted_at", "updated_at")
        read_only_fields = ("id", "submitted_at", "updated_at")

    def validate(self, attrs):
        if not attrs.get("submission_file") and not attrs.get("python_code"):
            raise serializers.ValidationError({"python_code": "Submit either a PDF file or Python code."})
        return attrs
