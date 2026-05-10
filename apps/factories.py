import factory

from apps.accounts.models import School, User
from apps.activities.models import Activity
from apps.children.models import Child, ChildContact, ChildParent, Group


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


class TeacherFactory(UserFactory):
    role = User.Role.TEACHER
    group = factory.SubFactory('apps.factories.GroupFactory')


class ParentFactory(UserFactory):
    role = User.Role.PARENT


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
    school = factory.LazyAttribute(lambda obj: obj.group.school)
    allergies = []


class ChildParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChildParent

    child = factory.SubFactory(ChildFactory)
    parent = factory.SubFactory(ParentFactory, school=factory.SelfAttribute('..child.school'))


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    school = factory.SubFactory(SchoolFactory)
    child = factory.SubFactory(ChildFactory, school=factory.SelfAttribute('..school'))
    logged_by = factory.SubFactory(UserFactory, school=factory.SelfAttribute('..school'))
    type = Activity.Type.NOTE


class ChildContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChildContact

    child = factory.SubFactory(ChildFactory)
    school = factory.LazyAttribute(lambda obj: obj.child.school)
    name = factory.Sequence(lambda n: f'Contact {n}')
    phone = factory.Sequence(lambda n: f'+2613400{n:05d}')
    relation = ChildContact.Relation.OTHER
    is_authorized_pickup = True
    is_emergency_contact = False
