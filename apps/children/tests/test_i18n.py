from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.factories import GroupFactory, SchoolFactory, UserFactory


class I18nTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.other_group = GroupFactory(school=SchoolFactory())
        self.url = reverse('child-list')
        self.payload = {
            'first_name': 'Lova',
            'last_name': 'Rakoto',
            'birth_date': '2022-01-01',
            'group': self.other_group.id,
        }

    def test_error_message_in_french_by_default(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('votre école', str(response.data))

    def test_error_message_in_english_when_accept_language_en(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('votre école', str(response.data))
        self.assertIn('school', str(response.data))
