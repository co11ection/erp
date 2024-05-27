from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


from goals.models import Goal
from reports.models import Reports
from users.models import User
from users.permissions import CanAccessPeriod, CanAccessStatistics

from .models import Periods

from .serializers import PeriodSerializer


class PeriodViews(ModelViewSet):
    """
    Класс представления для модели Periods.

    Позволяет выполнять различные операции с объектами модели Periods
    через REST API, такие как создание, просмотр, редактирование и удаление.

    Attributes:
        queryset (QuerySet): Запрос для получения всех объектов Periods.
        serializer_class (Serializer): Сериализатор для объектов Periods.
        permission_classes (list): Список классов разрешений для доступа к представлению.

    Methods:
        get_permissions(): Устанавливает соответствующие разрешения в зависимости от
        выполняемого действия (создание, просмотр, редактирование или удаление).

    Поля:
    title - название периода
    start_date
    end_date

    """

    queryset = Periods.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [
        CanAccessPeriod,
    ]


@api_view(["GET"])
@permission_classes([CanAccessStatistics, CanAccessPeriod])
def get_copmare_result_period(request):
    user: User = request.user
    
    last_period = Periods.objects.latest("end_date")
    last_period_revenue = (
        Reports.objects.filter(period=last_period, user=user).aggregate(
            last_period_revenue=Sum("revenue")
        )["last_period_revenue"]
        or 0)
        
    last_period_plan = (
        Goal.objects.filter(periods=last_period, responsible_user=user).aggregate(
            last_period_plan=Sum("number_range_finally")
        )["last_period_plan"]
        or 0)
        
    if last_period_plan is not None and last_period_plan != 0:
        result = round(last_period_revenue / last_period_plan * 100, 2)
    else:
        result = 0
        
    data = {"result": result}
    return Response(data, status=200)