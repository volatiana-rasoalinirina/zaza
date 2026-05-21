from django.apps import AppConfig


class MessagingConfig(AppConfig):
    name = 'apps.messaging'

    def ready(self):
        import apps.messaging.signals  # noqa
