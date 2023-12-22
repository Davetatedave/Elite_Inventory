# serializers.py
from rest_framework import serializers
from .models import trackingDb


class TrackingDbSerializer(serializers.ModelSerializer):
    class Meta:
        model = trackingDb
        fields = "__all__"
