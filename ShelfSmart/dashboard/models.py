from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model (optional, or use default)
class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("student", "Student"),
        ("user", "User"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

class BorrowRecord(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    def overdue(self):
        from datetime import date
        return not self.is_returned and (date.today() - self.borrowed_date).days > 14
