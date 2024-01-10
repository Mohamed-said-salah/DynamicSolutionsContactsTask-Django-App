from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_contacts')

