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
        return f"{self.code} - {self.name} - {self.symbol}"
