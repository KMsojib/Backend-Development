from django.contrib import admin
from django.utils import timezone
from .models import TodoItem

@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    fields = ('task_owner', 'title', 'description', 'is_completed', 'due_date', 'priority', 'category')
    list_display = ('task_owner', 'title', 'category', 'priority', 'due_date', 'is_completed', 'is_overdue')
    
    list_display_links = ('title',)
    
    list_filter = ('is_completed', 'priority', 'category')
    
    search_fields = ('title', 'description', 'category')
    
    list_editable = ('is_completed', 'priority')
    
    @admin.display(boolean=True, description="Overdue?")
    def is_overdue(self, obj):
        if obj.due_date and not obj.is_completed:
            return timezone.now() > obj.due_date 
        return False