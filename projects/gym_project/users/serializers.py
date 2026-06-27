from rest_framework import serializers # type: ignore
from .models import Trainer, TrainerSalary, Member
from companies.models import Branch

class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = '__all__'

class TrainerSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerSalary
        fields = ['id', 'first_name', 'last_name', 'specialty', 'ratings', 'branches']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'gym_company', 'first_name', 'last_name', 'email', 'joined_date']
