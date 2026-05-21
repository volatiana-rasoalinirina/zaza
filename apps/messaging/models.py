from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from apps.children.models import Child


class Thread(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='thread')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Thread — {self.child}'


class Message(models.Model):
    class Type(models.TextChoices):
        TEXT = 'TEXT', 'Text'
        IMAGE = 'IMAGE', 'Image'
        FILE = 'FILE', 'File'

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='messages')
    sent_at = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.TEXT)
    content = models.TextField(blank=True)
    file_url = models.URLField(blank=True)

    def clean(self):
        if self.type == self.Type.TEXT and not self.content:
            raise ValidationError({'content': 'A text message must have content.'})
        if self.type in (self.Type.IMAGE, self.Type.FILE) and not self.file_url:
            raise ValidationError({'file_url': 'An image or file message must have a file_url.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.sender} → {self.thread} ({self.sent_at:%Y-%m-%d %H:%M})'
