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

# ================== Trainer Section ======================#
 
class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)
    ratings = models.FloatField(default=0.0)
    branch = models.ManyToManyField(Branch, related_name="trainers")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialty}"
 
class TrainerSalary(models.Model):
    trainer = models.OneToOneField(Trainer, on_delete=models.CASCADE, related_name = "salary_record")
    gym_company = models.ForeignKey(GymCompany, on_delete=models.CASCADE, related_name = "trainer_payrolls")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_bonus_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    bank_account_info = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Trainer Salaries"
        
    def __str__(self):
        return f"Salary: {self.trainer.first_name} ({self.gym_company.name})"
  
 
# ===================== Member =========================
class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    joined_date = models.DateField(auto_now_add=True) # When Member ship application done.. it will update it joining status.
    gym_company = models.ForeignKey(GymCompany, on_delete=models.CASCADE,related_name="members")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
   
class GymClass(models.Model):
    name = models.CharField(max_length=100)
    class_overview = models.TextField()
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="classes")
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name="classes")    
    day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()  
    end_time = models.TimeField()    
    
    class Meta:
        verbose_name_plural = "Gym Classes"
    
    def __str__(self):
        if self.trainer:
            trainer_name = f"{self.trainer.first_name} {self.trainer.last_name}"
        else:
            trainer_name = "No Trainer Assigned"
        return f"{self.name} - {self.branch.name} - {self.trainer.first_name} {self.trainer.last_name}"
    

# ========================= Member Book Class =========================#
class ClassBooking(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="booking")
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name="reservations")
    booking_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('member','gym_class')
    
    def __str__(self):
        return f"{self.member.last_name} booked {self.gym_class.name}"
    
    
# ========================= Automated Attendecne Update =========================#
class AttendanceLog(models.Model):
    booking = models.OneToOneField(ClassBooking, on_delete=models.CASCADE, related_name="attendance")
    check_in_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent')], 
        default='PRESENT'
    )
    
    def __str__(self):
        return f"{self.booking.member} - {self.booking.gym_class} : {self.status}"
    


# ========================= Equipment ============================
class EquipmentAsset(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    branch = models.ForeignKey(Branch,on_delete=models.CASCADE, related_name="assets")
    condition_status = models.CharField(
        max_length=30,
        choices=[
            ('OPERATIONAL','Operational'),
            ('MAINTENANCE_REQUIRED','Needs Repair'),
            ('BROKEN', 'Out of Order')
            ],
        default='OPERATIONAL'
    )
    last_inspected_date = models.DateField()
    
    def __str__(self):
        return f"{self.name} - {self.branch.name} ({self.condition_status})"