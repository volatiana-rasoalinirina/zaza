from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.children.models import Group
from apps.factories import GroupFactory, SchoolFactory, UserFactory


class GroupListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)

    def test_director_sees_only_own_school_groups(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('group-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [g['id'] for g in response.data]
        self.assertIn(self.group.id, ids)
        self.assertNotIn(self.other_group.id, ids)

    def test_teacher_can_list_groups(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('group-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_list_groups(self):
        response = self.client.get(reverse('group-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupCreateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.url = reverse('group-list')
        self.payload = {'name': 'TPS'}

    def test_director_can_create_group(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

    def test_group_is_associated_to_director_school(self):
        self.client.force_authenticate(user=self.director)
        self.client.post(self.url, self.payload)
        self.assertEqual(Group.objects.first().school, self.school)

    def test_director_cannot_force_another_school(self):
        self.client.force_authenticate(user=self.director)
        self.client.post(self.url, {**self.payload, 'school': self.other_school.id})
        self.assertEqual(Group.objects.first().school, self.school)

    def test_teacher_cannot_create_group(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_group(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupUpdateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.url = reverse('group-detail', kwargs={'pk': self.group.id})

    def test_director_can_update_group(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.patch(self.url, {'name': 'PS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'PS')

    def test_director_cannot_update_another_school_group(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('group-detail', kwargs={'pk': self.other_group.id})
        response = self.client.patch(url, {'name': 'PS'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_update_group(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(self.url, {'name': 'PS'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_update_group(self):
        response = self.client.patch(self.url, {'name': 'PS'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupDeleteTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.url = reverse('group-detail', kwargs={'pk': self.group.id})

    def test_director_can_delete_group(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Group.objects.count(), 1)

    def test_director_cannot_delete_another_school_group(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('group-detail', kwargs={'pk': self.other_group.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_delete_group(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_delete_group(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
