from rest_framework import serializers
from decimal import Decimal
from .models import Goal, PendingEditRequest


class GoalSerializer(serializers.ModelSerializer):
    user_created = serializers.ReadOnlyField(source="user_created.email")
    inverse_division_value = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = "__all__"

    def get_inverse_division_value(self, obj):
        if obj.reverse_calculation:
            if float(obj.number_range_initial) > float(0):
                return round(
                    Decimal(obj.number_range_finally)
                    / Decimal(obj.number_range_initial),
                    2,
                )
        else:
            return 0


class EditSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    goals = GoalSerializer(read_only=True)

    class Meta:
        model = PendingEditRequest
        fields = "__all__"


class EditApproveSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")
    goals = GoalSerializer(read_only=True)
    data_to_update = serializers.JSONField()

    class Meta:
        model = PendingEditRequest
        fields = ["user", "goals", "request_date", "approved", "data_to_update"]


class PeriodSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=80)
    goals_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    goals__is_active = serializers.BooleanField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class UserGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            "name", "metrics_name", 
            "number_range_initial", 
            "number_range_finally",
            "digit_range", "id"
            ]