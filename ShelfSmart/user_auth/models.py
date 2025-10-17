from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model matching the new schema requirements."""
    
    # Override the id field to match schema (user_id as primary key)
    id = models.AutoField(primary_key=True, db_column='user_id')
    
    # Required fields from schema
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Additional fields from schema
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='user'
    )
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override date_joined to use created_at
    date_joined = None
    
    class Meta:
        db_table = 'user'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def is_active_user(self):
        return self.status == 'active'
