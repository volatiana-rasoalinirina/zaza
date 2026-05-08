from rest_framework import generics, viewsets

from apps.accounts.permissions import IsDirector
from apps.children.models import Child
from apps.children.serializers import ChildSerializer, GroupSerializer


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
