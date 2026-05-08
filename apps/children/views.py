from rest_framework import generics, viewsets

from apps.accounts.permissions import IsDirector, IsDirectorOrTeacher
from apps.children.models import Child, ChildContact
from apps.children.serializers import ChildContactSerializer, ChildSerializer, GroupSerializer


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsDirector]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return Child.objects.filter(group__school=self.request.user.school)


class ChildContactViewSet(viewsets.ModelViewSet):
    serializer_class = ChildContactSerializer
    filterset_fields = ['child', 'is_emergency_contact', 'is_authorized_pickup']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsDirectorOrTeacher()]
        return [IsDirector()]

    def get_queryset(self):
        return ChildContact.objects.filter(child__group__school=self.request.user.school)
