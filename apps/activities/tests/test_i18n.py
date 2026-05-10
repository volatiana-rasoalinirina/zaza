from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.factories import ActivityFactory, ChildFactory, ChildParentFactory, GroupFactory, ParentFactory, SchoolFactory


class ActivityFeedI18nTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.group = GroupFactory(school=self.school)
        self.child = ChildFactory(group=self.group)
        self.parent = ParentFactory(school=self.school)
        ChildParentFactory(child=self.child, parent=self.parent)
        self.activity = ActivityFactory(school=self.school, child=self.child, type='CHECKOUT')
        self.url = reverse('activity-list')

    def test_type_label_in_french_by_default(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['type_label'], 'Départ')

    def test_type_label_in_english_when_accept_language_en(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['type_label'], 'Check-out')

    def test_type_label_in_malagasy_when_accept_language_mg(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='mg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['type_label'], 'Fivoahana')
