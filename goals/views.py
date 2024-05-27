from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes, api_view
from django.db.models import Sum, F, Count
from django.http import JsonResponse
from django.db.models.functions import Round


from metrics_category.models import Category
from rest_framework.permissions import AllowAny

from users.permissions import CanAccessMetrics, CanAccessReports, CanCreateReports
from periods.models import Periods

from .models import Goal, PendingEditRequest
from .serializers import (
    GoalSerializer,
    EditSerializer,
    EditApproveSerializer,
    PeriodSerializer,
    UserGoalSerializer
)


class GoalViewset(ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [
        CanAccessMetrics,
    ]

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user_created=self.request.user)

    @action(methods=["GET"], detail=False)
    def get_list_goal(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        title = request.query_params.get("title")

        if not all([start_date, end_date, title]):
            return Response({"error": "Missing query parameters"}, status=400)

        try:
            period = Periods.objects.get(
                start_date=start_date, end_date=end_date, title=title
            )

            goals_data = (
                Goal.objects.filter(periods=period)
                .annotate(
                    total_revenue=Sum("reports__revenue"),
                    completion_percentage=Round(
                        F("total_revenue") / F("number_range_finally") * 100, 2
                    ),
                    weights=Sum("weight"),
                )
                .values(
                    "id",
                    "metrics_name",
                    "category",
                    "weights",
                    "total_revenue",
                    "number_range_finally",
                    "completion_percentage",
                    "is_active",
                )
            )

            return Response({"goals_data": list(goals_data)}, status=200)

        except Periods.DoesNotExist:
            return Response({"error": "Period not found"}, status=404)


class EditRequestListView(generics.ListAPIView):
    """
    Класс для отображения списка ожидающих запросов на редактирование метрик.

    Поля:
    metric
    user
    request_date
    data_to_update
    approved
    """

    queryset = PendingEditRequest.objects.all()
    serializer_class = EditSerializer
    permission_classes = [CanAccessMetrics]


@api_view(["GET"])
@permission_classes([CanAccessMetrics])
def edit_request_list(request):
    period_id = request.query_params.get("id")
    pending = PendingEditRequest.objects.filter(goals__periods=period_id)
    serializer = EditSerializer(pending, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([CanAccessMetrics])
def count_pending_edit_request(request):
    count_pending = PendingEditRequest.objects.all().count()
    return Response({"count": count_pending}, status=200)


@api_view(["GET"])
@permission_classes([CanAccessMetrics])
def get_list_edit_request(request):
    periods_data = (
        Periods.objects.filter(goals__pendingeditrequest__isnull=False)
        .annotate(
            goals_count=Count("goals__pendingeditrequest", distinct=True),
            categories_count=Count("goals__category", distinct=True),
        )
        .values(
            "id",
            "title",
            "goals_count",
            "categories_count",
            "goals__is_active",
            "start_date",
            "end_date",
        )
        .distinct()
    )

    serializer = PeriodSerializer(periods_data, many=True)

    return JsonResponse(serializer.data, safe=False)


class EditRequestCreateView(generics.CreateAPIView):
    """
    Класс для создания нового запроса на редактирование метрики.

    Методы:
    post(id) - создание нового запроса на редактирования
    Attributes:
        queryset (QuerySet): QuerySet, содержащий все ожидающие запросы на редактирование метрик.
        serializer_class (Serializer): Сериализатор для запросов на редактирование.
    """

    queryset = PendingEditRequest.objects.all()
    serializer_class = EditSerializer
    permission_classes = [CanAccessMetrics]

    def perform_create(self, serializer):
        goal_id = self.kwargs.get("goal_id")
        user = self.request.user
        goal = Goal.objects.filter(pk=goal_id).first()

        if goal:
            serializer.save(
                user=user,
                goals=goal,
                data_to_update=serializer.validated_data.get("data_to_update"),
            )


class EditRequestApprovalView(generics.UpdateAPIView):
    """
    Класс для утверждения запроса на редактирование метрики.
    Метод:
    put(id) подтверждение изменения на редактирование метрик

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все ожидающие запросы на редактирование метрик.
        serializer_class (Serializer): Сериализатор для запросов на редактирование.
    """

    queryset = PendingEditRequest.objects.all()
    serializer_class = EditApproveSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        edit_request = serializer.instance

        if not edit_request.approved:
            edit_request.approved = True
            edit_request.save()

            goal = edit_request.goals

            data_to_update = edit_request.data_to_update
            for field, new_data in data_to_update.items():
                if field == "category":
                    new_data = Category.objects.get(slug=new_data)
                setattr(goal, field, new_data)

            goal.is_change = True
            goal.save()
            edit_request.delete()

            return Response({"msg": "Запрос на изменение утвержден"}, status=200)

        return Response({"msg": "Запрос на изменение уже утвержден"}, status=400)

    http_method_names = ["put"]


class PendingEditRequestDeleteAPIView(generics.DestroyAPIView):
    queryset = PendingEditRequest.objects.all()
    serializer_class = EditSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Pending edit request deleted successfully."}, status=204
        )



@api_view(['GET'])
@permission_classes([
    CanAccessMetrics, CanCreateReports, CanAccessReports
    ])
def user_metrics_for_last_period(request):
    user = request.user


    user_goals = Goal.objects.filter(responsible_user=user)
    

    periods_ids = user_goals.values_list('periods__id', flat=True).distinct()


    last_period = Periods.objects.filter(id__in=periods_ids).order_by('-end_date').first()
    
    if last_period:

        period_goals = last_period.goals.filter(responsible_user=user)
        serializer = UserGoalSerializer(period_goals, many=True)
        return Response({
            "period_name": last_period.title,
            "start_date": last_period.start_date,
            "end_date": last_period.end_date,
            "id": last_period.pk,
            'metrics': serializer.data
        })
    else:
        # Если подходящий период не найден
        return Response({'error': 'Метрики для пользователя не найдены в доступных периодах'}, status=404)
