from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('User', 'User'),
    ]
  
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    # is_active= models.BooleanField(default=False)

    def __str__(self):
        return self.username

class RevokedToken(models.Model):
    token = models.CharField(max_length=255)
    revoked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Token {self.token} revoked at {self.revoked_at}'