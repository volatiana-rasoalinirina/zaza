from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.children.models import ChildParent

from .models import Message, Thread
from .serializers import MessageSerializer, ThreadSerializer


def _accessible_threads(user):
    if user.role == User.Role.PARENT:
        child_ids = ChildParent.objects.filter(parent=user).values_list('child_id', flat=True)
        return Thread.objects.filter(child_id__in=child_ids, child__school=user.school)
    if user.role == User.Role.TEACHER:
        return Thread.objects.filter(child__group=user.group, child__school=user.school)
    return Thread.objects.filter(child__school=user.school)


class ThreadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _accessible_threads(self.request.user)


class MessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def _get_thread(self):
        return get_object_or_404(_accessible_threads(self.request.user), pk=self.kwargs['thread_pk'])

    def get_queryset(self):
        return Message.objects.filter(thread=self._get_thread())

    def perform_create(self, serializer):
        serializer.save(thread=self._get_thread(), sender=self.request.user)
