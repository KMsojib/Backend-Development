from rest_framework import serializers #type:ignore
from .models import GymClass, ClassBooking, AttendanceLog, EquipmentAsset
from users.serializers import TrainerSerializer

class GymClassSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer(source='trainer',read_only=True)
    
    class Meta:
        model = GymClass
        fields = ['id', 'branch', 'trainer', 'name', 'day_of_week', 'start_time', 'end_time']
        
        def validate(self, data):
            start = data.get('start_time')
            end = data.get('end_time')
            trainer = data.get('trainer')
            day = data.get('day_of_week')
            
            if start >= end:
                raise serializers.ValidationError("Start time must be before end time.")

            conflicts = GymClass.objects.filter(
                trainer=trainer,
                day_of_week=day,
                start_time__lt=end,
                end_time__gt=start   
            )
            
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise serializers.ValidationError("This trainer has a conflicting class at the specified time.")

            return data

class ClassBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassBooking
        fields = ['id', 'member', 'gym_class', 'booking_timestamp']
        read_only_fields = ['booking_timestamp']
        
class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['id', 'booking', 'check_in_time', 'status']
        read_only_fields = ['check_in_time']