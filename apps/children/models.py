from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.accounts.models import School


class Group(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return self.name


class Child(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='children')
    allergies = ArrayField(models.CharField(max_length=100), default=list, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ChildContact(models.Model):
    class Relation(models.TextChoices):
        FATHER = 'FATHER', 'Père'
        MOTHER = 'MOTHER', 'Mère'
        GRANDFATHER = 'GRANDFATHER', 'Grand-père'
        GRANDMOTHER = 'GRANDMOTHER', 'Grand-mère'
        UNCLE = 'UNCLE', 'Oncle'
        AUNT = 'AUNT', 'Tante'
        SIBLING = 'SIBLING', 'Frère/Sœur'
        NANNY = 'NANNY', 'Nounou'
        NEIGHBOR = 'NEIGHBOR', 'Voisin'
        OTHER = 'OTHER', 'Autre'

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    relation = models.CharField(max_length=20, choices=Relation.choices)
    photo_url = models.URLField(blank=True)
    is_authorized_pickup = models.BooleanField(default=False)
    is_emergency_contact = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.child})'
