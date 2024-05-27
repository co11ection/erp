from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Sum, Count, Value, CharField
from django.db.models.functions import Round, Concat
from rest_framework.response import Response
from datetime import datetime, timedelta

from goals.models import Goal
from profiles.models import UserProfile
from periods.models import Periods
from users.permissions import CanAccessUsersAndRoles, CanAccessStatistics
from users.models import User
from reports.models import Reports
from .utils import compare_completion_percentage, get_data, get_user_data, get_data_user


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanAccessStatistics])
def general_results(request):
    """
    Получение общих результатов для пользователя с учетом его роли.

    Аргументы:
        request (Request): Запрос от клиента.

    Возвращает:
        Response: JSON-ответ, содержащий общие результаты и данные метрик.
    """


    user: User = request.user
    user_profile = UserProfile.objects.get(user=request.user)

    period_id = request.query_params.get("id")
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    selected_period = get_object_or_404(
            Periods, start_date=start_date, end_date=end_date, id=period_id
        )

    if user.role == "user":
        general_data = get_data_user(user=user, user_profile=user_profile, selected_period=selected_period)
        return Response(general_data)

    elif user.role in ("admin", "owner"):
        total_number_range_finally = (
            Goal.objects.filter(periods__id=selected_period.pk).aggregate(
                total_number_range_finally=Sum("number_range_finally")
            )["total_number_range_finally"]
            or 0
        )

        total_number_of_revenue = (
            Reports.objects.filter(period=selected_period).aggregate(total_number_of_revenue=Sum("revenue"))[
                "total_number_of_revenue"
            ]
            or 0
        )

        if total_number_range_finally:
            result = round(
                (total_number_of_revenue * 100) / total_number_range_finally, 2
            )
        else:
            result = 0

        goal_data = get_data(selected_period)

        data = {"result": result, "data": goal_data}

        return Response(data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanAccessStatistics])
def results_for_period(request):
    try:
        user = request.user
        period_title = request.query_params.get("title")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        selected_period = get_object_or_404(
            Periods, start_date=start_date, end_date=end_date, title=period_title
        )

        if user.role in ("admin", "owner"):
            total_number_range_finally = (
                selected_period.goals.aggregate(
                    total_number_range_finally=Sum("number_range_finally")
                )["total_number_range_finally"]
                or 0
            )

            revenue = (
                Reports.objects.filter(period=selected_period).aggregate(
                    revenue=Sum("revenue")
                )["revenue"]
                or 0
            )

            result = 0
            if total_number_range_finally:
                result = round((revenue * 100) / total_number_range_finally, 2)

            goal_data = get_data(selected_period)

            data = {"result": result, "data": goal_data}

            return Response(data, status=200)
        else:
            return Response({"error": "Access denied"}, status=403)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(["GET"])
@permission_classes([IsAuthenticated, CanAccessStatistics])
def compare_periods(request):
    """
    Сравнение процентов завершения целей между двумя периодами.

    Параметры:
    - request: Объект запроса Django.

    Параметры запроса:
    - period_name_1 (str): Название первого периода.
    - period_name_2 (str): Название второго периода.

    Возвращает:
    - Response: JSON-ответ, содержащий данные сравнения.

    Пример:
    GET /compare_periods/?period_name_1=Период1&period_name_2=Период2
    """

    period_id_1 = request.query_params.get("id_1")
    period_id_2 = request.query_params.get("id_2")

    try:
        period1 = Periods.objects.get(id=period_id_1)
        period2 = Periods.objects.get(id=period_id_2)
    except Periods.DoesNotExist:
        return Response({"message": "One or both periods not found"}, status=404)

    goals_period1 = Goal.objects.filter(periods=period1)
    goals_period2 = Goal.objects.filter(periods=period2)

    comparison_data = compare_completion_percentage(goals_period1, goals_period2)

    return Response({"comparison_data": comparison_data})