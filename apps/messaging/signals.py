from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.children.models import Child


@receiver(post_save, sender=Child)
def create_thread_for_child(sender, instance, created, **kwargs):
    if created:
        from apps.messaging.models import Thread
        Thread.objects.create(child=instance)
