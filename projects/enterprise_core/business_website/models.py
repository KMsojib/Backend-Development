from django.db import models
from django.utils.text import slugify

class WebPage(models.Model):
    # Setup specific layout templates for the frontend to render
    LAYOUT_CHOICES = [
        ('HOME', 'Home Page'),
        ('STANDARD', 'Standard Content Page'),
        ('CONTACT', 'Contact Form Page'),
        ('BLOG_LIST', 'Blog Index Layout'),
    ]

    title = models.CharField(max_length=200)
    
    # The slug is the URL-friendly version of the title (e.g., "About Us" -> "about-us")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    content = models.TextField(blank=True, help_text="HTML or Markdown body content")
    layout_type = models.CharField(
        max_length=20, 
        choices=LAYOUT_CHOICES, 
        default='STANDARD'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_layout_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)