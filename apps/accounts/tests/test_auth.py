import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User, School


class LoginTokenTests(APITestCase):

    def setUp(self):
        self.school = School.objects.create(name='Crèche Les Petits', slug='creche-les-petits')
        self.director = User.objects.create_user(
            email='director@zaza.io',
            password='director123',
            role=User.Role.DIRECTOR,
            school=self.school,
        )
        self.url = reverse('login')

    def test_token_contains_role_and_school_id(self):
        response = self.client.post(self.url, {
            'email': 'director@zaza.io',
            'password': 'director123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        decoded_access_token = jwt.decode(
            response.data['access'],
            settings.SECRET_KEY,
            algorithms=['HS256'],
        )
        self.assertEqual(decoded_access_token['role'], 'DIRECTOR')
        self.assertEqual(decoded_access_token['school_id'], self.school.id)
