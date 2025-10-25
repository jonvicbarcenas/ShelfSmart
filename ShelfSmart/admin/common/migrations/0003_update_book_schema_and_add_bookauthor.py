# Generated manually for ShelfSmart Book schema update

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_author_publisher_category'),
    ]

    operations = [
        # Note: Old Book and BorrowRecord tables were manually deleted in Supabase
        # We're creating fresh tables with the new schema
        
        # Create new Book model with updated schema
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(blank=True, help_text='ISBN-13 number', max_length=13, null=True, unique=True)),
                ('title', models.CharField(help_text='Book title', max_length=255)),
                ('subtitle', models.CharField(blank=True, help_text='Book subtitle', max_length=255, null=True)),
                ('description', models.TextField(blank=True, help_text='Book description', null=True)),
                ('publication_date', models.DateField(blank=True, help_text='Publication date', null=True)),
                ('edition', models.CharField(blank=True, help_text='Book edition', max_length=50, null=True)),
                ('pages', models.IntegerField(blank=True, help_text='Number of pages', null=True)),
                ('language', models.CharField(default='English', help_text='Book language', max_length=50)),
                ('total_copies', models.IntegerField(default=1, help_text='Total number of copies')),
                ('quantity', models.IntegerField(default=1, help_text='Available quantity')),
                ('price', models.DecimalField(blank=True, decimal_places=2, help_text='Book price', max_digits=10, null=True)),
                ('cover_image_url', models.URLField(blank=True, help_text='Cover image URL', max_length=500, null=True)),
                ('availability', models.CharField(choices=[('available', 'Available'), ('borrowed', 'Borrowed')], default='available', help_text='Current availability status', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(help_text='Book category', on_delete=django.db.models.deletion.PROTECT, related_name='books', to='common.category')),
                ('publisher', models.ForeignKey(help_text='Book publisher', on_delete=django.db.models.deletion.PROTECT, related_name='books', to='common.publisher')),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
                'db_table': 'book',
                'ordering': ['title'],
            },
        ),
        
        # Create BookAuthor junction table
        migrations.CreateModel(
            name='BookAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_role', models.CharField(choices=[('primary', 'Primary Author'), ('co-author', 'Co-Author'), ('editor', 'Editor'), ('translator', 'Translator')], default='primary', help_text='Role of the author in this book', max_length=20)),
                ('author', models.ForeignKey(help_text='Author reference', on_delete=django.db.models.deletion.CASCADE, related_name='book_authors', to='common.author')),
                ('book', models.ForeignKey(help_text='Book reference', on_delete=django.db.models.deletion.CASCADE, related_name='book_authors', to='common.book')),
            ],
            options={
                'verbose_name': 'Book Author',
                'verbose_name_plural': 'Book Authors',
                'db_table': 'book_author',
                'ordering': ['book', 'author'],
                'unique_together': {('book', 'author')},
            },
        ),
        
        # Recreate BorrowRecord with reference to new Book model
        migrations.CreateModel(
            name='BorrowRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('borrowed_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('return_date', models.DateField(blank=True, null=True)),
                ('is_returned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.book')),
            ],
            options={
                'db_table': 'dashboard_borrowrecord',
            },
        ),
    ]
