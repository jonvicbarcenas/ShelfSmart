from django.db import models


class AppSettings(models.Model):
    """
    Singleton model for application-wide settings.
    Only one row should exist with id=1.
    """
    library_name = models.CharField(
        max_length=255,
        default="ShelfSmart Library",
        help_text="Name of the library"
    )
    theme = models.CharField(
        max_length=50,
        default="default",
        help_text="UI theme preference"
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Enable email notifications"
    )
    default_borrow_days = models.IntegerField(
        default=14,
        help_text="Default number of days for borrowing books"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "App Settings"
        verbose_name_plural = "App Settings"
    
    def __str__(self):
        return f"Settings: {self.library_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'library_name': 'ShelfSmart Library',
                'theme': 'default',
                'email_notifications': True,
                'default_borrow_days': 14,
            }
        )
        return settings
