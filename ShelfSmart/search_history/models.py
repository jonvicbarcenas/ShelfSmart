from django.db import models
from django.conf import settings


class SearchHistory(models.Model):
    """Search history model to track user search queries"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
        help_text="User who performed the search"
    )
    search_query = models.CharField(max_length=255, help_text="Search query text")
    search_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Search'),
            ('title', 'Title Search'),
            ('author', 'Author Search'),
            ('category', 'Category Search')
        ],
        default='general',
        help_text="Type of search performed"
    )
    results_count = models.IntegerField(default=0, help_text="Number of results found")
    search_context = models.CharField(
        max_length=50,
        default='catalog',
        help_text="Context where search was performed (catalog, admin, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.search_query} by {self.user.username}"

    class Meta:
        db_table = 'search_history'
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ['-created_at']  # Most recent first
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['search_context', '-created_at']),
        ]
