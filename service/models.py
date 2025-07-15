from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    pass


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=255, unique=True)
    symbol = models.CharField(max_length=10)

    class Meta:
        ordering = ('name',)
        verbose_name = 'currency'
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f"{self.symbol} - {self.code}"


class Participant(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='participants'
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'


class Event(models.Model):
    name = models.CharField(max_length=100)
    participants = models.ManyToManyField(Participant, related_name='events')
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='events'
    )
    owner = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        related_name='events'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    session_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_event_name_user',
                condition=Q(owner__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['name', 'session_id'],
                name='unique_event_name_session',
                condition=Q(owner__isnull=True)
            ),
        ]

    def __str__(self):
        return self.name
