from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nif = models.CharField("NIF", max_length=20, unique=True)
    tlf = models.CharField("Teléfono", max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.username
