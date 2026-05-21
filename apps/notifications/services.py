from abc import ABC, abstractmethod


class NotificationService(ABC):

    @abstractmethod
    def send(self, recipient, event_type: str, context: dict) -> bool:
        pass


class WhatsAppNotifier(NotificationService):

    def send(self, recipient, event_type: str, context: dict) -> bool:
        # TODO: integrate Meta Cloud API
        return False


class EmailNotifier(NotificationService):

    def send(self, recipient, event_type: str, context: dict) -> bool:
        # TODO: integrate Resend
        return False
