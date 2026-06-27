from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from companies.models import GymCompany, Branch


# Trainer
class Trainer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100,db_index=True)
    ratings = models.FloatField(default = 0.0, validators = [MinValueValidator(0.0), MaxValueValidator(5.0)])
    branches = models.ManyToManyField(Branch, related_name='trainers')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.speciality}"
    
# Trainer Salary Section
class TrainerSalary(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='salaries')
    gym_company = models.ForeignKey(GymCompany, on_delete=models.CASCADE, related_name='trainer_salaries')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.trainer.first_name} {self.trainer.last_name} - {self.salary} on {self.date}"
    
    
# User
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    gym_company = models.ForeignKey(GymCompany, on_delete=models.CASCADE, related_name='members')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='members')
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"