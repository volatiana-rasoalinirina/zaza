from rest_framework import generics

from apps.accounts.permissions import IsDirector
from apps.children.serializers import GroupSerializer


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsDirector]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
