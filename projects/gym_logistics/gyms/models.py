from django.db import models

class GymCompany(models.Model):
    name = models.CharField(max_length=200)
    corporate_email = models.EmailField()  # Check spelling here
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Gym Companies"
    
    def __str__(self):
        return self.name
    
class Branch(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    gym_company = models.ForeignKey(GymCompany, on_delete=models.CASCADE, related_name='branches')  # Check spelling here

    class Meta:
        verbose_name_plural = "Branches"
        
    def __str__(self):
        return f"{self.gym_company.name} - {self.city} - {self.name}"
    
class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)
    ratings = models.FloatField(default=0.0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="trainers")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialty}"
    
class GymClass(models.Model):
    name = models.CharField(max_length=100)
    class_overview = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="classes")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="classes")
    Day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()  
    end_time = models.TimeField()    
    
    class Meta:
        verbose_name_plural = "Gym Classes"
    
    def __str__(self):
        return f"{self.name} - {self.branch.name} - {self.trainer.first_name} {self.trainer.last_name}"