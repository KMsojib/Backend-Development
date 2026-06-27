from django.db import models
from django.contrib.auth.models import User

class StaffProfile(models.Model):
    ROLE_CHOICES = [('CASHIER', 'Cashier'), ('MANAGER', 'Manager'), ('OWNER', 'Owner')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CASHIER')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)