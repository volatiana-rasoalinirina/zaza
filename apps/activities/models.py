from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import School, User
from apps.children.models import Child, ChildContact


class Activity(models.Model):

    class Type(models.TextChoices):
        CHECKIN = 'CHECKIN', _('Arrivée')
        CHECKOUT = 'CHECKOUT', _('Départ')
        MEAL = 'MEAL', _('Repas')
        NAP = 'NAP', _('Sieste')
        NOTE = 'NOTE', _('Note')
        PHOTO = 'PHOTO', _('Photo')

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='activities')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='activities')
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logged_activities')
    type = models.CharField(max_length=20, choices=Type.choices)
    note = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    picked_up_by = models.ForeignKey(
        ChildContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickups',
    )

    def __str__(self):
        return f'{self.type} — {self.child} ({self.timestamp:%Y-%m-%d %H:%M})'
