from rest_framework import serializers # type: ignore
from .models import (
    GymCompany, Branch, Trainer, GymClass, 
    TrainerSalary, Member, ClassBooking, AttendanceLog, EquipmentAsset
)


class GymCompanySerializer(serializers.ModelSerializer):
    # branches = BranchSerializer(many=True, read_only=True)
    branch_count = serializers.IntegerField(source='branches.count', read_only=True)
    class Meta:
        model = GymCompany
        fields = ['id', 'name', 'corporate_email','branch_count', 'created_at', 'updated_at', 'branches']
  
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'city', 'address', 'gym_company']      
        
class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = ['id', 'first_name', 'last_name', 'specialty', 'ratings', 'branch']

class TrainerSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerSalary
        fields = ['id', 'trainer', 'gym_company', 'base_salary', 'hourly_bonus_rate', 'bank_account_info']
    
class GymClassSerializer(serializers.ModelSerializer):
    # Nested fields show descriptive structures on GET requests
    trainer_details = TrainerSerializer(source='trainer', read_only=True)
    
    class Meta:
        model = GymClass
        fields = ['id', 'name', 'branch', 'trainer', 'trainer_details', 'start_time', 'end_time']

    def validate(self, attrs):
        trainer = attrs.get('trainer')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be strictly after start time."})

        # Deep ORM Query: Find overlapping timeslots for this specific trainer
        overlapping_classes = GymClass.objects.filter(
            trainer=trainer,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        # If updating an existing class instance, don't count itself as a conflict
        if self.instance:
            overlapping_classes = overlapping_classes.exclude(pk=self.instance.pk)

        if overlapping_classes.exists():
            raise serializers.ValidationError(
                {"trainer": "Double-Booking Conflict! This trainer is already assigned to a class during this time."}
            )

        return attrs
    
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id','first_name','last_name','email','joined_date','gym_company']
    
class ClassBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassBooking
        fields = ['id', 'member', 'gym_class', 'booking_timestamp']


class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['id', 'booking', 'check_in_time', 'status']
        
class EquipmentAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentAsset
        fields = ['id', 'name', 'serial_number', 'branch', 'condition_status', 'last_inspected_date']