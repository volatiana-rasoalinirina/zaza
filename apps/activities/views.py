from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.permissions import IsDirectorOrTeacher
from apps.children.models import ChildParent

from .models import Activity
from .serializers import ActivitySerializer


class ActivityViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ActivitySerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsDirectorOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.PARENT:
            child_ids = ChildParent.objects.filter(parent=user).values_list('child_id', flat=True)
            return Activity.objects.filter(school=user.school, child_id__in=child_ids)
        if user.role == User.Role.TEACHER:
            return Activity.objects.filter(school=user.school, child__group=user.group)
        return Activity.objects.filter(school=user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, logged_by=self.request.user)
