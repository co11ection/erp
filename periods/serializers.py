from rest_framework import serializers
from .models import Periods


class PeriodSerializer(serializers.ModelSerializer):
    metric_count = serializers.SerializerMethodField()
    metric_category_count = serializers.SerializerMethodField()

    class Meta:
        model = Periods
        fields = "__all__"

    def get_metric_count(self, obj):
        return obj.goals.all().count()

    def get_metric_category_count(self, obj):
        return obj.goals.values_list("category", flat=True).distinct().count()
