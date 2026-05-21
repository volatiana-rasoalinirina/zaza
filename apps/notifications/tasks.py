from celery import shared_task


@shared_task
def dispatch_notification(recipient_id: int, event_type: str, context: dict) -> None:
    from apps.accounts.models import User
    from apps.notifications.dispatcher import dispatch

    recipient = User.objects.get(pk=recipient_id)
    dispatch(recipient, event_type, context)
