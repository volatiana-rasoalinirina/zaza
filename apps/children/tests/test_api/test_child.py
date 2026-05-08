from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import School, User
from apps.children.models import Child, Group


class ChildCreateTests(APITestCase):

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

        self.group = Group.objects.create(name='TPS', school=self.school)
        self.other_group = Group.objects.create(name='TPS', school=self.other_school)

        self.url = reverse('child-list')
        self.payload = {
            'first_name': 'Lova',
            'last_name': 'Rakoto',
            'birth_date': '2022-03-15',
            'group': self.group.id,
        }

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

        self.group = Group.objects.create(name='TPS', school=self.school)
        self.other_group = Group.objects.create(name='TPS', school=self.other_school)

        self.child = Child.objects.create(
            first_name='Lova',
            last_name='Rakoto',
            birth_date='2022-03-15',
            group=self.group,
            allergies=[],
        )
        self.other_child = Child.objects.create(
            first_name='Hery',
            last_name='Andria',
            birth_date='2021-05-10',
            group=self.other_group,
            allergies=[],
        )

        self.url = reverse('child-detail', kwargs={'pk': self.child.id})

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

        self.group = Group.objects.create(name='TPS', school=self.school)
        self.other_group = Group.objects.create(name='TPS', school=self.other_school)

        self.child = Child.objects.create(
            first_name='Lova',
            last_name='Rakoto',
            birth_date='2022-03-15',
            group=self.group,
            allergies=[],
        )
        self.other_child = Child.objects.create(
            first_name='Hery',
            last_name='Andria',
            birth_date='2021-05-10',
            group=self.other_group,
            allergies=[],
        )

        self.url = reverse('child-detail', kwargs={'pk': self.child.id})

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
