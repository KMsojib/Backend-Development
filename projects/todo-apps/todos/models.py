from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class TodoItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Task Title")
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False, verbose_name="Completed?")
    due_date = models.DateTimeField(blank=True, null=True, verbose_name="Deadline")
    
    PRIORITY_CHOICES = [
    (1, 'High'),
    (2, 'Medium'),
    (3, 'Low'),
    ]

    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1
    )
    category = models.CharField(max_length=50, default='General',help_text="Prayer, Work, Gym, Personal")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Todo Apps'
        verbose_name_plural = 'Todo Apps'
        
        # is complted? -> show it on last of the list, if not : stay on top
        # Priority-> 1 -> 2 -> 3 (High-Medium-Low)
        # Due Date -> Earliest deadlines stay on top.
        ordering = ['is_completed','priority','due_date']
    
    
    class TodoItem(models.Model):
        owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title
