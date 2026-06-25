from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('The Email Field must be defined for enterprise users.')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active',True)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('role','ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser msut have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')
        
        return self.create_user(email, password,**extra_fields)
        

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN','Administrator'
        MANAGER = 'MANAGER','Manager'
        STAFF = 'STAFF','Staff'
        
    username = None
    email = models.EmailField(unique=True, max_length = 255)    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )
        
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    def __str__(self):
        return f"{self.username} ({self.role})"