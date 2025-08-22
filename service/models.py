from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
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


class Expense(models.Model):
    name = models.CharField(max_length=255)
    payer = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)], default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.payer.name}"

    def clean(self, **args):
        if self.event_id and self.payer_id:
            if self.payer not in self.event.participants.all():
                raise ValidationError(f"{self.payer.name} participant is not part of the event {self.event.name}.")

        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ('-created_at',)

