from django.contrib.auth.models import AbstractUser
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


class User(AbstractUser):
    username = None

    class Role(models.TextChoices):
        DIRECTOR = 'DIRECTOR', 'Director'
        TEACHER = 'TEACHER', 'Teacher'
        PARENT = 'PARENT', 'Parent'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email