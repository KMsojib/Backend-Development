from django.db import models

class GymCompany(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    corporate_email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Gym Companies"
    
    def __str__(self):
        return self.name
    
class Branch(models.Model):
    gym_company = models.ForeignKey(GymCompany, on_delete=models.PROTECT, related_name="branches")
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50, db_index=True)
    address = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = "Branches"
    
    def __str__(self):
        return f"{self.gym_company.name} - {self.name}"