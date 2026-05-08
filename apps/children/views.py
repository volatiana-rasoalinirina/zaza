from rest_framework import viewsets

from apps.accounts.permissions import IsDirector, IsDirectorOrTeacher
from apps.children.models import Child, ChildContact, Group
from apps.children.serializers import ChildContactSerializer, ChildSerializer, GroupSerializer


class TenantViewSetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class GroupViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsDirectorOrTeacher()]
        return [IsDirector()]


class ChildViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsDirector]
    queryset = Child.objects.all()


class ChildContactViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ChildContactSerializer
    filterset_fields = ['child', 'is_emergency_contact', 'is_authorized_pickup']
    queryset = ChildContact.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsDirectorOrTeacher()]
        return [IsDirector()]
