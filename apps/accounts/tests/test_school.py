from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User, School


class SchoolCreateTests(APITestCase):

    def setUp(self):
        self.director = User.objects.create_user(
            email='director@zaza.io',
            password='director123',
            role=User.Role.DIRECTOR,
        )
        self.teacher = User.objects.create_user(
            email='teacher@zaza.io',
            password='teacher123',
            role=User.Role.TEACHER,
        )
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
        School.objects.create(name='Existing', slug='creche-les-petits')
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
