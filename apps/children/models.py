from django.db import models

from apps.accounts.models import School


class Group(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return self.name
