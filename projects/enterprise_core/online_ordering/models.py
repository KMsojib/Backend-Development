from django.db import models
from django.contrib.auth.models import User

class Storefront(models.Model):
    domain_name = models.CharField(max_length=255, unique=True)
    brand_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE)