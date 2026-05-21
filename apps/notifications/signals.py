from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.children.models import ChildParent
from apps.messaging.models import Message
from apps.notifications.constants import EventType
from apps.notifications.tasks import dispatch_notification


@receiver(post_save, sender=Message)
def notify_on_new_message(sender, instance, created, **kwargs):
    if not created:
        return

    child = instance.thread.child
    context = {
        'sender_email': instance.sender.email,
        'child_name': str(child),
    }

    if instance.sender.role == User.Role.PARENT:
        director = User.objects.filter(school=child.school, role=User.Role.DIRECTOR).first()
        if director:
            dispatch_notification.delay(director.id, EventType.MESSAGE, context)
    else:
        parent_ids = ChildParent.objects.filter(child=child).values_list('parent_id', flat=True)
        for parent_id in parent_ids:
            dispatch_notification.delay(parent_id, EventType.MESSAGE, context)
