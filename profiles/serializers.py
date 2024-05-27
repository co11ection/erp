from rest_framework import serializers
from .models import UserProfile, Schedule
from reports.models import Reports


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)
    user = serializers.ReadOnlyField(source="user.email")
    photo = serializers.ImageField(source="user.photo")
    telegram_username = serializers.CharField(source="user.telegram_username")
    user_schedule = ScheduleSerializer(many=True, read_only=True)
    medals = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    medal_names = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def get_medal_names(self, obj):
        return [medal.name for medal in obj.medals.all()]


class UserProfileEditSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)
    user = serializers.ReadOnlyField(source="user.email")
    user_schedule = ScheduleSerializer(many=True, read_only=True)
    category_metrics_permission = serializers.BooleanField(
        source="user.category_metrics_permission"
    )
    create_reports_permission = serializers.BooleanField(
        source="user.create_reports_permission"
    )
    period_permission = serializers.BooleanField(source="user.period_permission")
    statistick_permission = serializers.BooleanField(
        source="user.statistick_permission"
    )
    metrics_permission = serializers.BooleanField(source="user.metrics_permission")
    users_and_roles_permission = serializers.BooleanField(
        source="user.users_and_roles_permission"
    )
    reports_permission = serializers.BooleanField(source="user.reports_permission")

    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileListSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)
    email = serializers.CharField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    is_active = serializers.BooleanField(source="user.is_active")
    average_result_for_periods_percent = serializers.SerializerMethodField()
    medal_names = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def get_average_result_for_periods_percent(self, obj):
        user_count_report = obj.user.reports.all().count()
        total_report = Reports.objects.all().count()
        if total_report == 0:
            total_report = 1
        return round(user_count_report * 100 / total_report, 2)

    def get_medal_names(self, obj):
        return [medal.name for medal in obj.medals.all()]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
