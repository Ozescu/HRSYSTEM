from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_email = serializers.EmailField(source="candidate.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate",
            "candidate_email",
            "job",
            "job_title",
            "cover_letter",
            "cv",
            "status",
            "applied_at",
            "updated_at",
        )
        read_only_fields = ("id", "candidate", "applied_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not self.instance:
            return attrs

        user = request.user
        if getattr(user, "role", None) == "candidate" and self.instance.candidate_id == user.id and "status" in attrs:
            if attrs["status"] != self.instance.status:
                raise serializers.ValidationError({"status": "Candidates cannot change application status."})

        return attrs
