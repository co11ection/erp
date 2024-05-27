from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import (
    Count,
    F,
    Q,
    fields,
    Value,
    Subquery,
    OuterRef,
    IntegerField,
    functions,
    DateField,
    FloatField,
    Sum
)
from django.db.models.functions import Round, Coalesce
from rest_framework.response import Response
from datetime import datetime, timedelta
from .serializers import (
    ReportSerializers,
    ReportCommentSerializer,
    UserReportSerializer,
)
from .models import Reports, ReportComments
from periods.models import Periods
from users.permissions import (
    CanApproveReport,
    CanEditReport,
    CanCreateReports,
    CanAccessReports,
)
from users.permissions import IsAuthor
from goals.models import Goal

User = get_user_model()


class ReportsViewSet(ModelViewSet):
    """
    Представление для отчетов

    Методы:
    -get - получение всех отчетов /reports/
    -post(request) - создание отчетов /reports/
    -get(id) - получение отчета по id /reports/{id}
    -put(id) - обновление отчетов(полное) /reports/{id}
    -patch(id) - обновление отчетов(частичное) /reports/{id}
    -delete(id) - удаление отчетов /reports/{id}

    Поля:
    id
    user
    hire_maid - нанять горничную choise [True, False]
    hire_maid_comment
    created_date
    period - id периода к которому этот отчет привязан
    goal - id цели к которой этот отчет привязан
    """

    queryset = Reports.objects.all()
    serializer_class = ReportSerializers

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [CanAccessReports]
        elif self.action in ["create"]:
            self.permission_classes = [CanCreateReports]
        elif self.action in ["destroy"]:
            self.permission_classes = [CanCreateReports]
        else:
            self.permission_classes = [CanCreateReports]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET"], detail=False)
    def get_user_reports(self, request):
        user_email = request.query_params.get("user")

        if user_email:
            user = get_object_or_404(User, email=user_email)

            report_counts = user_reports = Reports.objects.filter(user=user).count()

            user_goals_count = Goal.objects.filter(responsible_user=user).count()

            user_reports = (
                Reports.objects.filter(user=user)
                .annotate(
                    created_date_only=functions.Cast(
                        "created_date", output_field=DateField()
                    )
                )
                .values("created_date_only", "user__first_name", "user__last_name")
                .annotate(
                    period_title=F("period__title"),
                    start_date=F("period__start_date"),
                    end_date=F("period__end_date"),
                    goals_count=Count("goal", distinct=True),
                )
                .order_by("created_date_only")
            )

            today = datetime.today()
            current_day_of_week = today.weekday()
            delta_to_monday = timedelta(days=current_day_of_week)
            start_of_week = today - delta_to_monday
            end_of_week = start_of_week + timedelta(days=6)

            last_period = Periods.objects.latest("end_date")
            last_period_reports_count = Reports.objects.filter(
                period=last_period
            ).count()
            user_last_period_reports_count = Reports.objects.filter(
                period=last_period, user=user
            ).count()
            reports_current_week = Reports.objects.filter(
                created_date__range=[start_of_week, end_of_week]
            ).count()
            user_reports_current_week = Reports.objects.filter(
                created_date__range=[start_of_week, end_of_week], user=user
            ).count()
            total_reports = float(self.queryset.count())

            if total_reports and reports_current_week and last_period_reports_count:
                average_result_for_periods_percent = round(
                    report_counts / total_reports * 100, 2
                )
                result_for_last_periods_percent = round(
                    user_last_period_reports_count / last_period_reports_count * 100, 2
                )
                result_for_last_week_percent = round(
                    user_reports_current_week / reports_current_week * 100, 2
                )
                statistics_data = {
                    "average_result_for_periods_percent": average_result_for_periods_percent,
                    "average_result_for_last_periods_percent": result_for_last_periods_percent,
                    "average_result_for_last_week_percent": result_for_last_week_percent,
                }

            else:
                average_result_for_periods_percent = round(report_counts / 1 * 100, 2)
                result_for_last_periods_percent = round(
                    user_last_period_reports_count / 1 * 100, 2
                )
                result_for_last_week_percent = round(
                    user_reports_current_week / 1 * 100, 2
                )

                statistics_data = {
                    "average_result_for_periods_percent": average_result_for_periods_percent,
                    "average_result_for_last_periods_percent": result_for_last_periods_percent,
                    "average_result_for_last_week_percent": result_for_last_week_percent,
                }

            data = {
                "report_counts": report_counts,
                "user_goals_count": user_goals_count,
                "user_reports": user_reports,
                "statistics_data": statistics_data,
            }

            return Response(data, status=200)
        else:
            return Response({"error": "User email is required"}, status=400)

    @action(methods=["GET"], detail=False)
    def get_user_all_reports(self, request):
        user_email = request.query_params.get("user")
        period_title = request.query_params.get("period_title")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if user_email and period_title and start_date and end_date:
            user = get_object_or_404(User, email=user_email)
            user_reports = Reports.objects.filter(
                user=user,
                period__title=period_title,
                period__start_date__gte=start_date,
                period__end_date__lte=end_date,
            )  # Получаем все отчеты для этого пользователя
            serializer = UserReportSerializer(user_reports, many=True)

            return Response(serializer.data, status=200)

        else:
            return Response({"error": "User email is required"}, status=400)

    @action(methods=["GET"], detail=False)
    def report_count(self, request):
        """
        Метод для получение статистики отчетов

        Получаемые поля:
        user,
        report_count,
        first_name,
        middle_name,
        last_name,
        period_count,
        average_result_for_periods - средний результат за период,
        average_result_for_periods_percent - средний результат за период в процентах,
        last_period_reports_count_percent - ,
        comparison_with_other,
        reports_in_last_period,
        user_reports_this_week
        """
        
        user = request.user
        today = datetime.today()
        current_day_of_week = today.weekday()
        delta_to_monday = timedelta(days=current_day_of_week)
        start_of_week = today - delta_to_monday
        end_of_week = start_of_week + timedelta(days=6)

        user_goals = Goal.objects.filter(responsible_user=user)
    
    
        periods_ids = user_goals.values_list('periods__id', flat=True).distinct()

    
        last_period = Periods.objects.filter(id__in=periods_ids).order_by('-end_date').first()

        last_period_reports_count = Reports.objects.filter(period=last_period) \
        .annotate(date=functions.TruncDay('created_date')) \
        .values('date') \
        .distinct() \
        .count()
        reports_current_week = (
        Reports.objects.filter(
        created_date__range=[start_of_week, end_of_week],
        user=OuterRef("user"),
        )
        .annotate(date=functions.TruncDay('created_date'))
        .values('date', 'user')
        .annotate(daily_reports=Count('id'))
        .values('user')
        .annotate(total_unique_days=Count('date'))
        .values('total_unique_days')
        )

        total_reports = float(self.queryset.count())

        if (
            total_reports != 0
            and reports_current_week != 0
            and last_period_reports_count != 0
        ):
            user_reports_this_week = (
                Reports.objects.filter(
                    created_date__range=[start_of_week, end_of_week],
                    user=OuterRef("user"),
                )
                .values("user")
                .annotate(total_reports=Count("id"))
                .values("total_reports")
            )

            report_counts = self.queryset \
                .order_by() \
                .values('user') \
                .annotate(
                report_count=Count('created_date', distinct=True),
                first_name=F('user__first_name'),
                middle_name=F('user__middle_name'),
                last_name=F('user__last_name'),

                period_count=functions.Coalesce(Count("period", distinct=True), 1),
                metric_count=Count("goal", distinct=True),
                average_result_for_periods=Round(
                    F("report_count") / F("period_count"), 2
                ),
                average_result_for_periods_percent=Round(
                    F("report_count") * 100 / total_reports, 2
                ),
                last_period_reports_count_percent=Round(
                    F("report_count") * 100 / last_period_reports_count, 2
                ),
                comparison_with_other=Round(F("report_count") / total_reports, 2),
                reports_in_last_period=Value(
                    last_period_reports_count, output_field=fields.IntegerField()
                ),
                user_reports_this_week=Coalesce(Subquery(user_reports_this_week[:1]), 0)
                * 100
                / reports_current_week
                if reports_current_week != 0
                else Value(0, output_field=FloatField()),
            )
        else:
            total_reports = 1
            last_period_reports_count = 1
            report_counts = self.queryset.values("user").annotate(
                report_count=Count("user"),
                first_name=F("user__first_name"),
                middle_name=F("user__middle_name"),
                last_name=F("user__last_name"),
                period_count=functions.Coalesce(Count("period", distinct=True), 1),
                average_result_for_periods=Round(
                    F("report_count") / F("period_count"), 2
                ),
                average_result_for_periods_percent=Round(
                    F("report_count") * 100 / total_reports, 2
                ),
                last_period_reports_count_percent=Round(
                    F("report_count") * 100 / last_period_reports_count, 2
                ),
                comparison_with_other=Round(F("report_count") / total_reports, 2),
                reports_in_last_period=Value(
                    last_period_reports_count, output_field=fields.IntegerField()
                ),
                user_reports_this_week=Value(0, output_field=IntegerField()),
            )

        user_report_data = list(report_counts)
        return Response(user_report_data, status=200)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = ReportComments.objects.all()
    serializer_class = ReportCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([CanAccessReports])
def report_comments(request, report_id):
    request_data = request.data.copy()
    request_data["report"] = report_id

    serializer = ReportCommentSerializer(data=request_data)
    if serializer.is_valid():
        # Assuming you have the report_id in the request data
        report_id = request.data.get("report")
        # You might want to add some validation for the report_id here

        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReportComments.objects.all()
    serializer_class = ReportCommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)


from django.utils import timezone


@api_view(["GET"])
@permission_classes([CanAccessReports])
def get_reports_result(request):
    latest_period = Periods.objects.latest("start_date")
    total_goal_number_range = (
        Goal.objects.aggregate(total_goal_number_range=Sum("number_range_finally"))[
            "total_goal_number_range"
        ]
        or 0
    )
    total_reports_revenue = (
        Reports.objects.aggregate(total_reports_revenue=Sum("revenue"))[
            "total_reports_revenue"
        ]
        or 1
    )
    total_goal_number_range_latest_period = (
        Goal.objects.filter(periods=latest_period).aggregate(
            total_goal_number_range=Sum("number_range_finally")
        )["total_goal_number_range"]
        or 0
    )
    total_reports_revenue_latest_period = (
        Reports.objects.filter(period=latest_period).aggregate(
            total_reports_revenue=Sum("revenue")
        )["total_reports_revenue"]
        or 1
    )
    start_of_week = timezone.now().date() - timezone.timedelta(
        days=timezone.now().date().weekday()
    )
    end_of_week = start_of_week + timezone.timedelta(days=6)

    total_goal_number_range_corresponding_week = (
        Goal.objects.filter(
            periods__start_date__range=[start_of_week, end_of_week]
        ).aggregate(total_goal_number_range=Sum("number_range_finally"))[
            "total_goal_number_range"
        ]
        or 0
    )

    total_reports_revenue_corresponding_week = (
        Reports.objects.filter(
            period__start_date__range=[start_of_week, end_of_week]
        ).aggregate(total_reports_revenue=Sum("revenue"))["total_reports_revenue"]
        or 1
    )

    result = round((total_goal_number_range / total_reports_revenue) * 100, 2)
    result_latest_period = round(
        (total_goal_number_range_latest_period / total_reports_revenue_latest_period)
        * 100,
        2,
    )
    result_corresponding_week = round(
        (
            total_goal_number_range_corresponding_week
            / total_reports_revenue_corresponding_week
        )
        * 100,
        2,
    )

    return Response(
        {
            "result": result,
            "result_latest_period": result_latest_period,
            "result_corresponding_week": result_corresponding_week,
        }
    )


