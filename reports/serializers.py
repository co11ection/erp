from rest_framework import serializers
from .models import Reports, ReportComments


class ReportCommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = ReportComments
        fields = ("id", "body", "user", "report")


class ReportSerializers(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Reports
        fields = "__all__"


class UserReportSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="created_date")
    metric_title = serializers.CharField(source="goal.metrics_name")
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    comments = ReportCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Reports
        fields = ("date", "metric_title", "comments", "revenue", "id")

    # def get_comments(self, obj):
    #     comments = obj.comments.all()
    #     return [comment.body for comment in comments]
