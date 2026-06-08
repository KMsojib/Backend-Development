from rest_framework import serializers
from .models import TodoItem

class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        # This includes all fields from your model in the API JSON output
        fields = '__all__'