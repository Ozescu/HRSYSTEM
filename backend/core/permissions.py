from rest_framework.permissions import SAFE_METHODS, BasePermission


class RolePermissionMixin:
    @staticmethod
    def is_authenticated(user):
        return bool(user and user.is_authenticated)

    @staticmethod
    def is_admin(user):
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_staff or getattr(user, "role", None) == "admin")
        )

    @staticmethod
    def is_recruiter(user):
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "recruiter")

    @staticmethod
    def is_candidate(user):
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "candidate")

    @staticmethod
    def get_application_candidate_id(obj):
        if hasattr(obj, "candidate_id"):
            return obj.candidate_id
        application = getattr(obj, "application", None)
        return getattr(application, "candidate_id", None)

    @staticmethod
    def get_application_recruiter_id(obj):
        if hasattr(obj, "job"):
            return getattr(obj.job, "recruiter_id", None)

        application = getattr(obj, "application", None)
        if application and getattr(application, "job", None):
            return getattr(application.job, "recruiter_id", None)

        assessment = getattr(obj, "assessment", None)
        if assessment and getattr(assessment, "application", None) and getattr(assessment.application, "job", None):
            return getattr(assessment.application.job, "recruiter_id", None)

        question = getattr(obj, "question", None)
        if question and getattr(question, "assessment", None):
            assessment = question.assessment
            if getattr(assessment, "application", None) and getattr(assessment.application, "job", None):
                return getattr(assessment.application.job, "recruiter_id", None)

        return None


class ReadOnlyOrRecruiterAdmin(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return self.is_recruiter(request.user) or self.is_admin(request.user)


class JobPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return self.is_recruiter(request.user) or self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return self.is_admin(request.user) or obj.recruiter_id == request.user.id


class ApplicationPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if not self.is_authenticated(request.user):
            return False

        if request.method == "POST":
            return self.is_candidate(request.user)

        return True

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request.user):
            return True

        is_candidate_owner = obj.candidate_id == request.user.id
        is_recruiter_owner = obj.job.recruiter_id == request.user.id

        if request.method in SAFE_METHODS:
            return is_candidate_owner or is_recruiter_owner

        if is_recruiter_owner:
            return True

        if is_candidate_owner and request.method in {"PUT", "PATCH", "DELETE"}:
            return obj.status in {"pending", "reviewing"}

        return False


class AssessmentPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if not self.is_authenticated(request.user):
            return False

        if request.method in SAFE_METHODS:
            return True

        return self.is_recruiter(request.user) or self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request.user):
            return True

        recruiter_id = self.get_application_recruiter_id(obj)
        candidate_id = self.get_application_candidate_id(obj)

        if request.method in SAFE_METHODS:
            return request.user.id in {recruiter_id, candidate_id}

        return request.user.id == recruiter_id


class CandidateAnswerPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if not self.is_authenticated(request.user):
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            return self.is_candidate(request.user) or self.is_recruiter(request.user) or self.is_admin(request.user)

        return True

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request.user):
            return True

        recruiter_id = self.get_application_recruiter_id(obj)
        candidate_id = self.get_application_candidate_id(obj)

        if request.method in SAFE_METHODS:
            return request.user.id in {recruiter_id, candidate_id}

        if request.user.id == recruiter_id:
            return True

        return request.user.id == candidate_id


class AssessmentResultPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if not self.is_authenticated(request.user):
            return False

        if request.method in SAFE_METHODS:
            return True

        return self.is_recruiter(request.user) or self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request.user):
            return True

        recruiter_id = self.get_application_recruiter_id(obj)
        candidate_id = self.get_application_candidate_id(obj)

        if request.method in SAFE_METHODS:
            return request.user.id in {recruiter_id, candidate_id}

        return request.user.id == recruiter_id


class AssessmentSubmissionPermission(RolePermissionMixin, BasePermission):
    def has_permission(self, request, view):
        if not self.is_authenticated(request.user):
            return False

        if request.method in SAFE_METHODS:
            return True

        return self.is_candidate(request.user) or self.is_recruiter(request.user) or self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if self.is_admin(request.user):
            return True

        recruiter_id = self.get_application_recruiter_id(getattr(obj, "assessment", obj))
        candidate_id = self.get_application_candidate_id(getattr(obj, "assessment", obj))

        if request.method in SAFE_METHODS:
            return request.user.id in {recruiter_id, candidate_id}

        if request.user.id == recruiter_id:
            return True

        return request.user.id == candidate_id
