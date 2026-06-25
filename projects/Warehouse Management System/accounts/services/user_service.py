from django.contrib.auth import get_user_model

User = get_user_model()

class UserServices:
    @staticmethod
    def register_new_user(validated_data : dict):
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role = validated_data.get('role',User.Role.STAFF)
        )