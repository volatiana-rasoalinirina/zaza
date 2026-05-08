from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import School, User
from apps.factories import SchoolFactory, UserFactory


class SchoolCreateTests(APITestCase):

    def setUp(self):
        self.director = UserFactory(role=User.Role.DIRECTOR, school=None)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=None)
        self.url = reverse('school_create')
        self.payload = {'name': 'Crèche Les Petits', 'slug': 'creche-les-petits'}

    def test_director_can_create_school(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 1)

    def test_director_is_associated_to_school(self):
        self.client.force_authenticate(user=self.director)
        self.client.post(self.url, self.payload)
        self.director.refresh_from_db()
        self.assertIsNotNone(self.director.school)

    def test_teacher_cannot_create_school(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_school(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_slug_is_rejected(self):
        SchoolFactory(slug='creche-les-petits')
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
