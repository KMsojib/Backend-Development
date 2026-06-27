from rest_framework import serializers
from .models import WebPage

class WebPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebPage
        fields = ['id', 'title', 'slug', 'content', 'layout_type']
        
        read_only_fields = ['id']