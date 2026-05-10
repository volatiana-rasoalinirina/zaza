from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.children.models import ChildParent
from apps.factories import (
    ActivityFactory,
    ChildContactFactory,
    ChildFactory,
    ChildParentFactory,
    GroupFactory,
    ParentFactory,
    SchoolFactory,
    TeacherFactory,
    UserFactory,
)


class ActivityCreateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = TeacherFactory(school=self.school, group=self.group)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        self.url = reverse('activity-list')
        self.payload = {
            'child': self.child.id,
            'type': 'MEAL',
            'note': 'A bien mangé',
        }

    def test_director_can_create_activity(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_can_create_activity(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_parent_cannot_create_activity(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_checkout_without_picked_up_by_returns_400(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'type': 'CHECKOUT'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_with_picked_up_by_returns_201(self):
        contact = ChildContactFactory(child=self.child, is_authorized_pickup=True)
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'type': 'CHECKOUT', 'picked_up_by': contact.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ActivityListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = TeacherFactory(school=self.school, group=self.group)
        self.parent = ParentFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        self.other_child = ChildFactory(group=GroupFactory(school=self.other_school))
        ChildParentFactory(child=self.child, parent=self.parent)
        self.activity = ActivityFactory(school=self.school, child=self.child)
        self.other_activity = ActivityFactory(school=self.other_school, child=self.other_child)
        self.url = reverse('activity-list')

    def test_director_sees_own_school_activities(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [a['id'] for a in response.data]
        self.assertIn(self.activity.id, ids)
        self.assertNotIn(self.other_activity.id, ids)

    def test_teacher_sees_only_own_group_activities(self):
        other_group = GroupFactory(school=self.school)
        other_child = ChildFactory(group=other_group)
        other_group_activity = ActivityFactory(school=self.school, child=other_child)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [a['id'] for a in response.data]
        self.assertIn(self.activity.id, ids)
        self.assertNotIn(self.other_activity.id, ids)
        self.assertNotIn(other_group_activity.id, ids)

    def test_parent_sees_only_own_children_activities(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [a['id'] for a in response.data]
        self.assertIn(self.activity.id, ids)
        self.assertNotIn(self.other_activity.id, ids)

    def test_parent_does_not_see_unlinked_child_activity(self):
        other_child_same_school = ChildFactory(group=self.group)
        other_activity = ActivityFactory(school=self.school, child=other_child_same_school)
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url)
        ids = [a['id'] for a in response.data]
        self.assertNotIn(other_activity.id, ids)


class ActivityReadOnlyTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.child = ChildFactory(group=self.group)
        self.activity = ActivityFactory(school=self.school, child=self.child)

    def test_put_not_allowed(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('activity-detail', kwargs={'pk': self.activity.id})
        response = self.client.put(url, {'type': 'NOTE'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_not_allowed(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('activity-detail', kwargs={'pk': self.activity.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
