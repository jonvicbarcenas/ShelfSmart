from django.db import models

class Book(models.Model):
    """Book model with comprehensive schema for library management"""
    # Primary key is automatically created as 'id' by Django
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, help_text="ISBN-13 number")
    title = models.CharField(max_length=255, help_text="Book title")
    subtitle = models.CharField(max_length=255, blank=True, null=True, help_text="Book subtitle")
    description = models.TextField(blank=True, null=True, help_text="Book description")
    publication_date = models.DateField(blank=True, null=True, help_text="Publication date")
    edition = models.CharField(max_length=50, blank=True, null=True, help_text="Book edition")
    pages = models.IntegerField(blank=True, null=True, help_text="Number of pages")
    language = models.CharField(max_length=50, default='English', help_text="Book language")
    
    # Foreign Keys
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.PROTECT,
        null=False,
        related_name='books',
        help_text="Book publisher"
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        null=False,
        related_name='books',
        help_text="Book category"
    )
    
    # Inventory fields
    total_copies = models.IntegerField(default=1, help_text="Total number of copies")
    quantity = models.IntegerField(default=1, help_text="Available quantity")
    
    # Media
    cover_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Cover image URL")
    
    # Availability
    availability = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('borrowed', 'Borrowed')],
        default='available',
        help_text="Current availability status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def book_id(self):
        """Alias for id to match schema naming"""
        return self.id
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.quantity > 0 and self.availability == 'available'

    class Meta:
        db_table = 'book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']


class BookAuthor(models.Model):
    """Junction table for Book-Author many-to-many relationship with role information"""
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        null=False,
        related_name='book_authors',
        help_text="Book reference"
    )
    author = models.ForeignKey(
        'Author',
        on_delete=models.CASCADE,
        null=False,
        related_name='book_authors',
        help_text="Author reference"
    )
    author_role = models.CharField(
        max_length=20,
        choices=[
            ('primary', 'Primary Author'),
            ('co-author', 'Co-Author'),
            ('editor', 'Editor'),
            ('translator', 'Translator')
        ],
        default='primary',
        help_text="Role of the author in this book"
    )

    def __str__(self):
        return f"{self.book.title} - {self.author.full_name} ({self.author_role})"

    class Meta:
        db_table = 'book_author'
        verbose_name = 'Book Author'
        verbose_name_plural = 'Book Authors'
        unique_together = [['book', 'author']]  # Composite primary key
        ordering = ['book', 'author']


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
    first_name = models.CharField(max_length=50, null=False, blank=False, help_text="Author's first name")
    last_name = models.CharField(max_length=50, null=False, blank=False, help_text="Author's last name")
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
    category_name = models.CharField(max_length=100, unique=True, null=False, blank=False, help_text="Category name")
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
    publisher_name = models.CharField(max_length=100, unique=True, null=False, blank=False, help_text="Publisher name")
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
