from django.db import models


class Password(models.Model):
    current_password = models.CharField(max_length=200)
    new_password = models.CharField(max_length=200)
    new_password_confirmation = models.CharField(max_length=200)
