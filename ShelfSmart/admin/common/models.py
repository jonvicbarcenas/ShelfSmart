from django.db import models

class Book(models.Model):
    # Primary key is automatically created as 'id' by Django
    name = models.CharField(max_length=255, help_text="Book title/name")
    type = models.CharField(max_length=100, help_text="Book type/genre")
    language = models.CharField(max_length=50, default='English', help_text="Book language")
    quantity = models.IntegerField(default=1, help_text="Total number of copies")
    availability = models.CharField(
        max_length=20,
        choices=[('Available', 'Available'), ('Borrowed', 'Borrowed')],
        default='Available',
        help_text="Current availability status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def book_id(self):
        """Alias for id to match schema naming"""
        return self.id

    class Meta:
        db_table = 'dashboard_book'  # Keep the same table name for compatibility

class BorrowRecord(models.Model):
    user_id = models.IntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - User {self.user_id}"

    class Meta:
        db_table = 'dashboard_borrowrecord'  # Keep the same table name for compatibility
