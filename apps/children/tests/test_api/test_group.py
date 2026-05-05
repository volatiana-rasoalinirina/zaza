from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import School, User
from apps.children.models import Group


class GroupCreateTests(APITestCase):

    def setUp(self):
        self.school = School.objects.create(name='Crèche Les Petits', slug='creche-les-petits')
        self.other_school = School.objects.create(name='Autre Crèche', slug='autre-creche')

        self.director = User.objects.create_user(
            email='director@zaza.io',
            password='director123',
            role=User.Role.DIRECTOR,
            school=self.school,
        )
        self.teacher = User.objects.create_user(
            email='teacher@zaza.io',
            password='teacher123',
            role=User.Role.TEACHER,
            school=self.school,
        )

        self.url = reverse('group_create')
        self.payload = {'name': 'TPS'}

    def test_director_can_create_group(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

    def test_group_is_associated_to_director_school(self):
        self.client.force_authenticate(user=self.director)
        self.client.post(self.url, self.payload)
        group = Group.objects.first()
        self.assertEqual(group.school, self.school)

    def test_teacher_cannot_create_group(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_group(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_director_cannot_create_group_in_another_school(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'school': self.other_school.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = Group.objects.first()
        self.assertEqual(group.school, self.school)
