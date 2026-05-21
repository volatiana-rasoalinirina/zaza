from apps.accounts.models import User

from .constants import EventType
from .services import EmailNotifier, WhatsAppNotifier


def should_notify(recipient, event_type: str) -> bool:
    if event_type in EventType.ALWAYS_ON:
        return True
    return recipient.notification_preferences.get(event_type, False)


def dispatch(recipient, event_type: str, context: dict) -> None:
    if not should_notify(recipient, event_type):
        return

    if recipient.preferred_channel == User.Channel.WHATSAPP:
        sent = WhatsAppNotifier().send(recipient, event_type, context)
        if not sent:
            EmailNotifier().send(recipient, event_type, context)
    else:
        EmailNotifier().send(recipient, event_type, context)
