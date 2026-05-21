from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.factories import ChildFactory, MessageFactory, ThreadFactory, UserFactory
from apps.messaging.models import Message


class ThreadSignalTests(TestCase):

    def test_thread_auto_created_on_child_creation(self):
        child = ChildFactory()
        self.assertTrue(hasattr(child, 'thread'))
        self.assertEqual(child.thread.child, child)


class MessageValidationTest(TestCase):

    def setUp(self):
        self.thread = ThreadFactory()
        self.sender = UserFactory(school=self.thread.child.school)

    def test_text_message_without_content_raises_error(self):
        message = MessageFactory.build(type=Message.Type.TEXT, content='', file_url='', thread=self.thread, sender=self.sender)
        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_file_message_without_file_url_raises_error(self):
        message = MessageFactory.build(type=Message.Type.FILE, content='', file_url='', thread=self.thread, sender=self.sender)
        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_image_message_without_file_url_raises_error(self):
        message = MessageFactory.build(type=Message.Type.IMAGE, content='', file_url='', thread=self.thread, sender=self.sender)
        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_valid_text_message_saves(self):
        message = MessageFactory(type=Message.Type.TEXT, content='Bonjour', file_url='')
        self.assertIsNotNone(message.pk)

    def test_valid_image_message_saves(self):
        message = MessageFactory(type=Message.Type.IMAGE, content='', file_url='https://s3.amazonaws.com/photo.jpg')
        self.assertIsNotNone(message.pk)
