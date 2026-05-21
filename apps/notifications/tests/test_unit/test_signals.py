from unittest.mock import patch

from django.test import TestCase

from apps.accounts.models import User
from apps.factories import (
    ChildFactory,
    ChildParentFactory,
    GroupFactory,
    MessageFactory,
    ParentFactory,
    SchoolFactory,
    UserFactory,
)


class MessageNotificationSignalTests(TestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        ChildParentFactory(child=self.child, parent=self.parent)

    @patch('apps.notifications.signals.dispatch_notification.delay')
    def test_director_notified_when_parent_sends(self, mock_delay):
        MessageFactory(thread=self.child.thread, sender=self.parent)
        mock_delay.assert_called_once_with(self.director.id, 'MESSAGE', {
            'sender_email': self.parent.email,
            'child_name': str(self.child),
        })

    @patch('apps.notifications.signals.dispatch_notification.delay')
    def test_parent_notified_when_director_sends(self, mock_delay):
        MessageFactory(thread=self.child.thread, sender=self.director)
        mock_delay.assert_called_once_with(self.parent.id, 'MESSAGE', {
            'sender_email': self.director.email,
            'child_name': str(self.child),
        })

    @patch('apps.notifications.signals.dispatch_notification.delay')
    def test_all_parents_notified_when_director_sends(self, mock_delay):
        parent2 = ParentFactory(school=self.school)
        ChildParentFactory(child=self.child, parent=parent2)
        MessageFactory(thread=self.child.thread, sender=self.director)
        self.assertEqual(mock_delay.call_count, 2)

    @patch('apps.notifications.signals.dispatch_notification.delay')
    def test_no_notification_on_message_update(self, mock_delay):
        message = MessageFactory(thread=self.child.thread, sender=self.parent)
        mock_delay.reset_mock()
        message.content = 'updated'
        message.save()
        mock_delay.assert_not_called()
