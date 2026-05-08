from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.children.models import ChildContact
from apps.factories import ChildContactFactory, ChildFactory, GroupFactory, SchoolFactory, UserFactory


class ChildContactCreateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.child = ChildFactory(group=GroupFactory(school=self.school))
        self.other_child = ChildFactory(group=GroupFactory(school=self.other_school))
        self.url = reverse('childcontact-list')
        self.payload = {
            'child': self.child.id,
            'name': 'Jean Rakoto',
            'relation': ChildContact.Relation.FATHER,
            'is_authorized_pickup': True,
            'is_emergency_contact': False,
        }

    def test_director_can_create_pickup_contact(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChildContact.objects.count(), 1)

    def test_director_can_create_emergency_contact(self):
        self.client.force_authenticate(user=self.director)
        payload = {**self.payload, 'is_authorized_pickup': False, 'is_emergency_contact': True}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChildContact.objects.first().is_emergency_contact)

    def test_director_can_create_contact_that_is_both(self):
        self.client.force_authenticate(user=self.director)
        payload = {**self.payload, 'is_authorized_pickup': True, 'is_emergency_contact': True}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contact = ChildContact.objects.first()
        self.assertTrue(contact.is_authorized_pickup)
        self.assertTrue(contact.is_emergency_contact)

    def test_both_booleans_false_is_rejected(self):
        self.client.force_authenticate(user=self.director)
        payload = {**self.payload, 'is_authorized_pickup': False, 'is_emergency_contact': False}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_phone_is_optional(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'phone': ''})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_director_cannot_create_contact_for_another_school_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'child': self.other_child.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_cannot_create_contact(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_contact(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChildContactListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.child = ChildFactory(group=GroupFactory(school=self.school))
        self.other_child_same_school = ChildFactory(group=GroupFactory(school=self.school))
        self.other_school_child = ChildFactory(group=GroupFactory(school=self.other_school))
        self.pickup = ChildContactFactory(child=self.child, is_authorized_pickup=True, is_emergency_contact=False)
        self.emergency = ChildContactFactory(child=self.child, is_authorized_pickup=False, is_emergency_contact=True)
        self.other_child_contact = ChildContactFactory(child=self.other_child_same_school, is_authorized_pickup=True, is_emergency_contact=False)
        self.other_school_contact = ChildContactFactory(child=self.other_school_child, is_authorized_pickup=True, is_emergency_contact=False)

    def test_director_sees_only_own_school_contacts(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('childcontact-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertNotIn(self.other_school_contact.id, ids)

    def test_director_can_filter_by_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('childcontact-list'), {'child': self.child.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.pickup.id, ids)
        self.assertIn(self.emergency.id, ids)
        self.assertNotIn(self.other_child_contact.id, ids)

    def test_director_can_filter_by_emergency_contact(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('childcontact-list'), {'is_emergency_contact': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.emergency.id, ids)
        self.assertNotIn(self.pickup.id, ids)

    def test_director_can_filter_by_authorized_pickup(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('childcontact-list'), {'is_authorized_pickup': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.pickup.id, ids)
        self.assertNotIn(self.emergency.id, ids)

    def test_teacher_can_list_contacts(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('childcontact-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_sees_only_own_school_contacts(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('childcontact-list'))
        ids = [c['id'] for c in response.data]
        self.assertNotIn(self.other_school_contact.id, ids)

    def test_teacher_can_filter_by_child(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('childcontact-list'), {'child': self.child.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.pickup.id, ids)
        self.assertNotIn(self.other_child_contact.id, ids)

    def test_teacher_can_filter_by_emergency_contact(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('childcontact-list'), {'is_emergency_contact': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.emergency.id, ids)
        self.assertNotIn(self.pickup.id, ids)

    def test_teacher_can_filter_by_authorized_pickup(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('childcontact-list'), {'is_authorized_pickup': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.pickup.id, ids)
        self.assertNotIn(self.emergency.id, ids)

    def test_unauthenticated_cannot_list_contacts(self):
        response = self.client.get(reverse('childcontact-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChildContactUpdateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.child = ChildFactory(group=GroupFactory(school=self.school))
        self.other_child = ChildFactory(group=GroupFactory(school=self.other_school))
        self.contact = ChildContactFactory(child=self.child, is_authorized_pickup=True, is_emergency_contact=False)
        self.other_contact = ChildContactFactory(child=self.other_child, is_authorized_pickup=True, is_emergency_contact=False)
        self.url = reverse('childcontact-detail', kwargs={'pk': self.contact.id})

    def test_director_can_update_contact(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.patch(self.url, {'name': 'Marie Rakoto', 'is_emergency_contact': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, 'Marie Rakoto')
        self.assertTrue(self.contact.is_emergency_contact)

    def test_director_cannot_update_another_school_contact(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('childcontact-detail', kwargs={'pk': self.other_contact.id})
        response = self.client.patch(url, {'name': 'Marie Rakoto'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_update_contact(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(self.url, {'name': 'Marie Rakoto'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_update_contact(self):
        response = self.client.patch(self.url, {'name': 'Marie Rakoto'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChildContactDeleteTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.child = ChildFactory(group=GroupFactory(school=self.school))
        self.other_child = ChildFactory(group=GroupFactory(school=self.other_school))
        self.contact = ChildContactFactory(child=self.child, is_authorized_pickup=True, is_emergency_contact=False)
        self.other_contact = ChildContactFactory(child=self.other_child, is_authorized_pickup=True, is_emergency_contact=False)
        self.url = reverse('childcontact-detail', kwargs={'pk': self.contact.id})

    def test_director_can_delete_contact(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChildContact.objects.count(), 1)

    def test_director_cannot_delete_another_school_contact(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('childcontact-detail', kwargs={'pk': self.other_contact.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_delete_contact(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_delete_contact(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
