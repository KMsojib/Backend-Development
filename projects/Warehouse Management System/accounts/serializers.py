from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 8)
    class Meta:
        model = User
        fields = ['id','email','password','role']
    
    def validate_email(self,value):
        if User.objects.filter(email = value).exists():
            raise serializers.ValidationError("This Email is alredy registered in this system.")
        return value
