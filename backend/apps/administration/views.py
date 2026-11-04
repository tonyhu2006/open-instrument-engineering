"""
Administration API (§15.7) — every write goes through a service (§4.1.14)
and is authorized by the RBAC matrix (§15.2.4, D5).
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.exceptions import ServiceError
from apps.core.viewsets import ServiceModelViewSet

from .access import is_administrator, user_accessible_project_ids
from .models import Organization, ProjectTaskForce, Role
from .permissions import RoleMatrixPermission, TaskForceObjectPermission
from .serializers import (
    AddMemberSerializer,
    AssignProjectSerializer,
    MeSerializer,
    MyTaskForceSerializer,
    OrganizationListSerializer,
    OrganizationSerializer,
    PasswordResetSerializer,
    PreferencesSerializer,
    ProjectTaskForceSerializer,
    RoleListSerializer,
    RoleSerializer,
    StatusMessageSerializer,
    TaskForceMembershipSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserSerializer,
)
from .services import (
    MembershipService,
    OrganizationService,
    RoleService,
    TaskForceService,
    UserService,
)

User = get_user_model()

# User / role pickers are needed by whoever may create task forces (ADM-TF03).
_TASK_FORCE_MANAGERS = (("task_force", "create"),)


class OrganizationViewSet(ServiceModelViewSet):
    """Organizations (§15.4.7)."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    service_class = OrganizationService
    permission_classes = [RoleMatrixPermission]
    rbac_resource = "organization"
    filterset_fields = ["is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrganizationListSerializer
        return OrganizationSerializer


class RoleViewSet(ServiceModelViewSet):
    """Roles — Administrator only (§15.7)."""

    queryset = Role.objects.select_related("organization").all()
    serializer_class = RoleSerializer
    service_class = RoleService
    permission_classes = [RoleMatrixPermission]
    rbac_resource = "role"
    rbac_read_delegates = _TASK_FORCE_MANAGERS
    filterset_fields = ["organization", "level", "is_system_role"]
    search_fields = ["code", "name"]
    ordering_fields = ["level", "display_order", "name"]
    ordering = ["-level", "display_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer


class UserViewSet(ServiceModelViewSet):
    """Users — Administrator only (§15.7)."""

    queryset = User.objects.select_related("organization", "role").all()
    serializer_class = UserSerializer
    service_class = UserService
    permission_classes = [RoleMatrixPermission]
    rbac_resource = "user"
    rbac_read_delegates = _TASK_FORCE_MANAGERS
    rbac_action_map = {
        "activate": "update",
        "deactivate": "update",
        "reset_password": "update",
    }
    filterset_fields = ["organization", "role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["username"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def _set_active(self, request, active: bool):
        user = self.get_object()
        self.get_service().update(user, {"is_active": active})
        return Response(
            {"status": "User activated." if active else "User deactivated."}
        )

    @extend_schema(request=None, responses=StatusMessageSerializer)
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        return self._set_active(request, True)

    @extend_schema(request=None, responses=StatusMessageSerializer)
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        return self._set_active(request, False)

    @extend_schema(request=PasswordResetSerializer, responses=StatusMessageSerializer)
    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_service().set_password(user, serializer.validated_data["password"])
        return Response({"status": "Password reset."})


class MeViewSet(viewsets.GenericViewSet):
    """Current user endpoints (§15.7 / I18N-04): ``/me/``,
    ``/me/task-forces/``, ``/me/preferences/``."""

    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer
    queryset = User.objects.none()
    pagination_class = None

    @extend_schema(responses=MeSerializer)
    def list(self, request):
        return Response(MeSerializer(request.user).data)

    @extend_schema(responses=MyTaskForceSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="task-forces")
    def task_forces(self, request):
        user = request.user
        accessible = user_accessible_project_ids(user)
        queryset = ProjectTaskForce.objects.filter(is_active=True)
        if accessible is not None:
            queryset = queryset.filter(
                Q(memberships__user=user, memberships__is_active=True) | Q(leader=user)
            ).distinct()
        return Response(MyTaskForceSerializer(queryset, many=True).data)

    @staticmethod
    def _preferences(user):
        prefs = dict(user.ui_preferences or {})
        prefs["language"] = user.language
        prefs["timezone"] = user.timezone
        return prefs

    @extend_schema(
        request=PreferencesSerializer,
        responses={200: {"type": "object", "additionalProperties": True}},
    )
    @action(detail=False, methods=["get", "put", "patch"], url_path="preferences")
    def preferences(self, request):
        """GET returns preferences; PATCH deep-merges; PUT replaces."""
        user = request.user
        if request.method == "GET":
            return Response(self._preferences(user))
        incoming = request.data
        if not isinstance(incoming, dict):
            raise ServiceError(
                "Request body must be a JSON object.", code="ADM_PREFERENCES_INVALID"
            )
        incoming = dict(incoming)
        language = incoming.pop("language", None)
        timezone_name = incoming.pop("timezone", None)
        valid_languages = {code.lower() for code in settings.PREFERENCE_LANGUAGES}
        if language is not None and str(language).lower() not in valid_languages:
            raise ServiceError(
                f"Unsupported language '{language}'.",
                code="ADM_PREFERENCES_INVALID",
                field="language",
            )
        if request.method == "PUT":
            prefs = incoming
        else:
            prefs = dict(user.ui_preferences or {})
            for key, value in incoming.items():
                if isinstance(value, dict) and isinstance(prefs.get(key), dict):
                    prefs[key] = {**prefs[key], **value}
                else:
                    prefs[key] = value
        update = {"ui_preferences": prefs}
        if language is not None:
            update["language"] = language
        if timezone_name is not None:
            update["timezone"] = timezone_name
        UserService(request=request).update(user, update)
        user.refresh_from_db()
        return Response(self._preferences(user))


class ProjectTaskForceViewSet(ServiceModelViewSet):
    """Task forces (§15.3, ADM-TF01..03)."""

    queryset = ProjectTaskForce.objects.select_related("leader", "created_by").all()
    serializer_class = ProjectTaskForceSerializer
    service_class = TaskForceService
    permission_classes = [RoleMatrixPermission, TaskForceObjectPermission]
    rbac_resource = "task_force"
    # "CR*": creators may manage their own groups (object permission).
    rbac_action_map = {
        "update": "create",
        "partial_update": "create",
        "destroy": "create",
        "remove_member": "create",
        "assign_project": "create",
    }
    filterset_fields = ["project_id", "is_active"]
    search_fields = ["code", "name"]
    ordering = ["code"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        accessible = user_accessible_project_ids(user)
        if accessible is None:
            return queryset
        return queryset.filter(
            Q(project_id__in=accessible) | Q(created_by=user)
        ).distinct()

    @extend_schema(methods=["GET"], responses=TaskForceMembershipSerializer(many=True))
    @extend_schema(
        methods=["POST"],
        request=AddMemberSerializer,
        responses={201: TaskForceMembershipSerializer},
    )
    @action(detail=True, methods=["get", "post"])
    def members(self, request, pk=None):
        task_force = self.get_object()
        if request.method == "GET":
            memberships = task_force.memberships.select_related(
                "user", "role_in_project", "added_by"
            )
            return Response(TaskForceMembershipSerializer(memberships, many=True).data)
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(pk=serializer.validated_data["user_id"]).first()
        if user is None:
            raise ServiceError(
                "User not found.", code="ADM_USER_NOT_FOUND", field="user_id"
            )
        membership = MembershipService(request=request).add(
            task_force, user, serializer.validated_data.get("role_in_project")
        )
        return Response(
            TaskForceMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={204: None})
    @action(
        detail=True,
        methods=["delete"],
        url_path=r"members/(?P<user_id>[0-9]+)",
    )
    def remove_member(self, request, pk=None, user_id=None):
        task_force = self.get_object()
        MembershipService(request=request).remove(task_force, int(user_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=AssignProjectSerializer, responses=ProjectTaskForceSerializer
    )
    @action(detail=True, methods=["post"], url_path="assign-project")
    def assign_project(self, request, pk=None):
        """Assign the engineering project (Administrator only, §15.7)."""
        task_force = self.get_object()
        if not is_administrator(request.user):
            raise ServiceError(
                "Only administrators can assign projects.",
                code="AUTH_PERMISSION_DENIED",
                status_code=403,
            )
        serializer = AssignProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.get_service().assign_project(
            task_force, serializer.validated_data["project_id"]
        )
        return Response(ProjectTaskForceSerializer(updated).data)
