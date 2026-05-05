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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
