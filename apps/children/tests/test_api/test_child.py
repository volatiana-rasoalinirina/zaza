from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.children.models import Child
from apps.factories import ChildFactory, GroupFactory, ParentFactory, SchoolFactory, UserFactory


class ChildListTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.parent = ParentFactory(school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.child = ChildFactory(group=self.group)
        self.other_child = ChildFactory(group=self.other_group)

    def test_parent_cannot_list_children(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.get(reverse('child-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_sees_only_own_school_children(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('child-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.child.id, ids)
        self.assertNotIn(self.other_child.id, ids)

    def test_director_cannot_retrieve_another_school_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.get(reverse('child-detail', kwargs={'pk': self.other_child.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ChildCreateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.parent = ParentFactory(school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.url = reverse('child-list')
        self.payload = {
            'first_name': 'Lova',
            'last_name': 'Rakoto',
            'birth_date': '2022-03-15',
            'group': self.group.id,
        }

    def test_parent_cannot_create_child(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_create_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Child.objects.count(), 1)

    def test_teacher_cannot_create_child(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_child(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_director_cannot_assign_child_to_another_school_group(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'group': self.other_group.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_director_can_create_child_with_allergies(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, {**self.payload, 'allergies': ['arachides', 'gluten']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Child.objects.first().allergies, ['arachides', 'gluten'])

    def test_allergies_defaults_to_empty_list(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Child.objects.first().allergies, [])


class ChildUpdateTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.parent = ParentFactory(school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.child = ChildFactory(group=self.group)
        self.other_child = ChildFactory(group=self.other_group)
        self.url = reverse('child-detail', kwargs={'pk': self.child.id})

    def test_parent_cannot_update_child(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.patch(self.url, {'first_name': 'Mamy'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_update_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.patch(self.url, {'first_name': 'Mamy', 'allergies': ['lactose']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.first_name, 'Mamy')
        self.assertEqual(self.child.allergies, ['lactose'])

    def test_teacher_cannot_update_child(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(self.url, {'first_name': 'Mamy'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_update_child(self):
        response = self.client.patch(self.url, {'first_name': 'Mamy'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_director_cannot_update_another_school_child(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('child-detail', kwargs={'pk': self.other_child.id})
        response = self.client.patch(url, {'first_name': 'Mamy'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ChildDeleteTests(APITestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.other_school = SchoolFactory()
        self.director = UserFactory(role=User.Role.DIRECTOR, school=self.school)
        self.teacher = UserFactory(role=User.Role.TEACHER, school=self.school)
        self.parent = ParentFactory(school=self.school)
        self.group = GroupFactory(school=self.school)
        self.other_group = GroupFactory(school=self.other_school)
        self.child = ChildFactory(group=self.group)
        self.other_child = ChildFactory(group=self.other_group)
        self.url = reverse('child-detail', kwargs={'pk': self.child.id})

    def test_parent_cannot_delete_child(self):
        self.client.force_authenticate(user=self.parent)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_delete_child(self):
        self.client.force_authenticate(user=self.director)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Child.objects.count(), 1)

    def test_teacher_cannot_delete_child(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_delete_child(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_director_cannot_delete_another_school_child(self):
        self.client.force_authenticate(user=self.director)
        url = reverse('child-detail', kwargs={'pk': self.other_child.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
