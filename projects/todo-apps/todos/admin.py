from django.contrib import admin
from django.utils import timezone
from .models import TodoItem

@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    # Show all columns in the main list table.
    list_display = ('title', 'category', 'priority', 'due_date', 'is_completed', 'is_overdue')
    
    # links to click to open the edit page
    list_display_links = ('title',)
    
    # Sidebar filtering panel options
    list_filter = ('is_completed', 'priority', 'category')
    
    # Search bar targets
    search_fields = ('title', 'description', 'category')
    
    # Allows editing these values directly from the list page view without opening the task!
    list_editable = ('is_completed', 'priority')
    
    @admin.display(boolean=True, description="Overdue?")
    def is_overdue(self, obj):
        if obj.due_date and not obj.is_completed:
            # Change < to > here:
            return timezone.now() > obj.due_date 
        return False