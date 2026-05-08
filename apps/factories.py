import factory

from apps.accounts.models import School, User
from apps.children.models import Child, Group


class SchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = School

    name = factory.Sequence(lambda n: f'Crèche {n}')
    slug = factory.Sequence(lambda n: f'creche-{n}')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@zaza.io')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    role = User.Role.DIRECTOR
    school = factory.SubFactory(SchoolFactory)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f'Groupe {n}')
    school = factory.SubFactory(SchoolFactory)


class ChildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Child

    first_name = factory.Sequence(lambda n: f'Enfant{n}')
    last_name = 'Rakoto'
    birth_date = '2022-01-01'
    group = factory.SubFactory(GroupFactory)
    allergies = []
