from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.factories import (
    ChildFactory,
    ChildParentFactory,
    GroupFactory,
    MessageFactory,
    ParentFactory,
    SchoolFactory,
    TeacherFactory,
    UserFactory,
)


class ThreadListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = TeacherFactory(school=self.school, group=self.group)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        ChildParentFactory(child=self.child, parent=self.parent)
        self.other_child = ChildFactory(group=GroupFactory(school=self.other_school))
        self.url = reverse('thread-list')

    def test_director_sees_all_school_threads(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [t['id'] for t in response.data]
        self.assertIn(self.child.thread.id, ids)
        self.assertNotIn(self.other_child.thread.id, ids)

    def test_teacher_sees_only_own_group_threads(self):
        other_child = ChildFactory(group=GroupFactory(school=self.school))
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        ids = [t['id'] for t in response.data]
        self.assertIn(self.child.thread.id, ids)
        self.assertNotIn(other_child.thread.id, ids)

    def test_parent_sees_only_own_children_threads(self):
        other_child = ChildFactory(group=self.group)
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url)
        ids = [t['id'] for t in response.data]
        self.assertIn(self.child.thread.id, ids)
        self.assertNotIn(other_child.thread.id, ids)


class MessageListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = TeacherFactory(school=self.school, group=self.group)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        ChildParentFactory(child=self.child, parent=self.parent)
        self.message = MessageFactory(thread=self.child.thread, sender=self.director)

    def _url(self, thread_id):
        return reverse('thread-messages-list', kwargs={'thread_pk': thread_id})

    def test_director_can_list_messages(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(self._url(self.child.thread.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_teacher_can_list_messages_in_group_thread(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self._url(self.child.thread.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_parent_can_list_messages_in_own_child_thread(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self._url(self.child.thread.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_parent_cannot_access_other_child_thread(self):
        other_child = ChildFactory(group=self.group)
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self._url(other_child.thread.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_access_outside_group_thread(self):
        other_child = ChildFactory(group=GroupFactory(school=self.school))
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self._url(other_child.thread.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MessageCreateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = TeacherFactory(school=self.school, group=self.group)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        ChildParentFactory(child=self.child, parent=self.parent)
        self.payload = {'type': 'TEXT', 'content': 'Bonjour'}

    def _url(self, thread_id):
        return reverse('thread-messages-list', kwargs={'thread_pk': thread_id})

    def test_director_can_send_message(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self._url(self.child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_can_send_message(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self._url(self.child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_parent_can_send_message(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.post(self._url(self.child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_cannot_send_message(self):
        response = self.client.post(self._url(self.child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_parent_cannot_send_to_other_child_thread(self):
        other_child = ChildFactory(group=self.group)
        self.client.force_authenticate(user=self.parent)
        response = self.client.post(self._url(other_child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_text_message_requires_content(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self._url(self.child.thread.id), {'type': 'TEXT', 'content': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sender_is_set_automatically(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.post(self._url(self.child.thread.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender'], self.parent.id)
