from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'creator'],
                name='unique_creator_participant_name'
            )
        ]


class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    participants = models.ManyToManyField(Participant, related_name='events')
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='events'
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='events'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.name
