from rest_framework import serializers
from reports.models import Reports


class AdminGeneralResultSerializer(serializers.Serializer):
    result = serializers.DecimalField(max_digits=5, decimal_places=2)
