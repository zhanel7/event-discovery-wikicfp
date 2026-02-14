from rest_framework import serializers
from .models import Conference

class ConferenceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Conference
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data