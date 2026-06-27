from rest_framework import serializers # type:ignore
from .models import GymCompany, Branch

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id','gym_company','name','city','address']
        
class GymCompanySerializer(serializers.ModelSerializer):
    branch_count = serializers.IntegerField(source='branches.count',read_only=True)
    
    class Meta:
        model = GymCompany
        fields = ['id', 'name', 'corporate_email', 'branch_count', 'created_at', 'updated_at']