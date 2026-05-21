from unittest.mock import patch

from django.test import TestCase

from apps.accounts.models import User
from apps.factories import UserFactory


class ShouldNotifyTests(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_message_always_notified(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {}
        self.assertTrue(should_notify(self.user, 'MESSAGE'))

    def test_checkin_always_notified(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {}
        self.assertTrue(should_notify(self.user, 'CHECKIN'))

    def test_checkout_always_notified(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {}
        self.assertTrue(should_notify(self.user, 'CHECKOUT'))

    def test_meal_disabled_by_default(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {}
        self.assertFalse(should_notify(self.user, 'MEAL'))

    def test_meal_enabled_when_opted_in(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {'MEAL': True}
        self.assertTrue(should_notify(self.user, 'MEAL'))

    def test_nap_disabled_by_default(self):
        from apps.notifications.dispatcher import should_notify
        self.user.notification_preferences = {}
        self.assertFalse(should_notify(self.user, 'NAP'))


class DispatchTests(TestCase):

    def test_whatsapp_notifier_called_for_whatsapp_user(self):
        from apps.notifications.dispatcher import dispatch
        user = UserFactory(preferred_channel=User.Channel.WHATSAPP, notification_preferences={})
        with patch('apps.notifications.dispatcher.WhatsAppNotifier.send', return_value=True) as mock_send:
            dispatch(user, 'MESSAGE', {})
            mock_send.assert_called_once()

    def test_email_notifier_called_for_email_user(self):
        from apps.notifications.dispatcher import dispatch
        user = UserFactory(preferred_channel=User.Channel.EMAIL, notification_preferences={})
        with patch('apps.notifications.dispatcher.EmailNotifier.send', return_value=True) as mock_send:
            dispatch(user, 'MESSAGE', {})
            mock_send.assert_called_once()

    def test_fallback_to_email_when_whatsapp_fails(self):
        from apps.notifications.dispatcher import dispatch
        user = UserFactory(preferred_channel=User.Channel.WHATSAPP, notification_preferences={})
        with patch('apps.notifications.dispatcher.WhatsAppNotifier.send', return_value=False):
            with patch('apps.notifications.dispatcher.EmailNotifier.send', return_value=True) as mock_email:
                dispatch(user, 'MESSAGE', {})
                mock_email.assert_called_once()

    def test_no_fallback_when_whatsapp_succeeds(self):
        from apps.notifications.dispatcher import dispatch
        user = UserFactory(preferred_channel=User.Channel.WHATSAPP, notification_preferences={})
        with patch('apps.notifications.dispatcher.WhatsAppNotifier.send', return_value=True):
            with patch('apps.notifications.dispatcher.EmailNotifier.send') as mock_email:
                dispatch(user, 'MESSAGE', {})
                mock_email.assert_not_called()

    def test_no_notification_when_opted_out(self):
        from apps.notifications.dispatcher import dispatch
        user = UserFactory(preferred_channel=User.Channel.WHATSAPP, notification_preferences={})
        with patch('apps.notifications.dispatcher.WhatsAppNotifier.send') as mock_send:
            dispatch(user, 'MEAL', {})
            mock_send.assert_not_called()
