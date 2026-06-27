from rest_framework import serializers
from .models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    open_rate = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ['id', 'title', 'sent_count', 'open_count', 'open_rate']

    def get_open_rate(self, obj):
        if obj.sent_count == 0:
            return 0.0
        return round((obj.open_count / obj.sent_count) * 100, 2)