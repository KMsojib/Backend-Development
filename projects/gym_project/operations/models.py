from django.db import models
from companies.models import Branch
from users.models import Trainer, Member


class GymClass(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="classes")
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name="classes")    
    name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=20, db_index=True)
    start_time = models.TimeField()  
    end_time = models.TimeField()    
    
    class Meta:
        verbose_name_plural = "Gym Classes"
    
    def __str__(self):
        return f"{self.name} ({self.day_of_week})"
    
    
class ClassBooking(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="bookings")
    gym_class = models.ForeignKey(GymClass, on_delete=models.PROTECT, related_name="reservations")
    booking_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('member', 'gym_class')
        
    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} booked {self.gym_class.name}"

class AttendanceLog(models.Model):
    booking = models.OneToOneField(ClassBooking, on_delete=models.CASCADE, related_name="attendance")
    check_in_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent')], default='PRESENT')

class EquipmentAsset(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="assets")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    serial_number = models.CharField(max_length=100, unique=True)
    condition_status = models.CharField(
        max_length=30, 
        choices=[
            ('OPERATIONAL', 'Operational'),
            ('MAINTENANCE_REQUIRED', 'Needs Repair'),
            ('BROKEN', 'Out of Order')
        ],
        default='OPERATIONAL'
    )
    last_inspected_date = models.DateField()
    