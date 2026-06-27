from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ClassBooking, AttendanceLog, GymClass
from users.models import Member

class GymBookingEngine:
    @staticmethod
    @transaction.atomic
    def deploy_booking_safeguard(member_id:int,gym_class_id:int) -> ClassBooking:
        
        target_class = GymClass.objects.get(id=gym_class_id)
        member = Member.objects.get(id=member_id)
        
        # Overapping booking safeguard:
        overlap_conflict = ClassBooking.objects.filter(
            member=member,
            gym_class__day_of_week=target_class.day_of_week,
            gym_class__start_time__lt=target_class.end_time,
            gym_class__end_time__gt=target_class.start_time
        ).exists()
        
        if overlap_conflict:
            raise ValidationError("Booking conflict: You already have a class booked that overlaps with this time slot.")
        
        new_booking = ClassBooking.objects.create(member=member, gym_class=target_class)   
        AttendanceLog.objects.create(booking=new_booking, status='PRESENT') 
        return new_booking