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


class Author(models.Model):
    """Author model for storing book author information"""
    # author_id is automatically created as 'id' by Django
    first_name = models.CharField(max_length=50, help_text="Author's first name")
    last_name = models.CharField(max_length=50, help_text="Author's last name")
    biography = models.TextField(blank=True, null=True, help_text="Author biography")
    nationality = models.CharField(max_length=50, blank=True, null=True, help_text="Author nationality")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def author_id(self):
        """Alias for id to match schema naming"""
        return self.id
    
    @property
    def full_name(self):
        """Get the full name of the author"""
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        ordering = ['last_name', 'first_name']


class Category(models.Model):
    """Category model for book categorization with support for hierarchical categories"""
    # category_id is automatically created as 'id' by Django
    category_name = models.CharField(max_length=100, unique=True, help_text="Category name")
    description = models.TextField(blank=True, null=True, help_text="Category description")
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category for hierarchical structure"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category.category_name} > {self.category_name}"
        return self.category_name

    @property
    def category_id(self):
        """Alias for id to match schema naming"""
        return self.id
    
    @property
    def parent_category_id(self):
        """Alias for parent_category foreign key to match schema naming"""
        return self.parent_category.id if self.parent_category else None
    
    def get_full_path(self):
        """Get the full hierarchical path of the category"""
        if self.parent_category:
            return f"{self.parent_category.get_full_path()} > {self.category_name}"
        return self.category_name

    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_name']


class Publisher(models.Model):
    """Publisher model for storing book publisher information"""
    # publisher_id is automatically created as 'id' by Django
    publisher_name = models.CharField(max_length=100, unique=True, help_text="Publisher name")
    address = models.TextField(blank=True, null=True, help_text="Publisher address")
    phone = models.CharField(max_length=15, blank=True, null=True, help_text="Contact phone number")
    email = models.EmailField(max_length=100, blank=True, null=True, help_text="Contact email")
    website = models.URLField(max_length=255, blank=True, null=True, help_text="Publisher website")
    established_year = models.IntegerField(
        blank=True,
        null=True,
        help_text="Year the publisher was established"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.publisher_name

    @property
    def publisher_id(self):
        """Alias for id to match schema naming"""
        return self.id

    class Meta:
        db_table = 'publisher'
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
        ordering = ['publisher_name']
