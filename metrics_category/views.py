from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from .models import Category
from .serializers import CategorySerializers
from users.permissions import CanEditMetric


class MetricsCategoryView(ModelViewSet):
    """
    Представление для категории метрик

    Поля:
    title = (financial, process, client, team),

    методы:
    -get(request) - получение всех категорий
    -post(request) - создание категорий тока choise
    -get(slug, request) -  получение категории по slug
    -put(slug, request) - изменение категории (полное)
    -patch(slug, request) - изменение категории (частичное)
    -delete(slug, request) - удаление категории

    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializers

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [
                AllowAny,
            ]

        else:
            self.permission_classes = [
                CanEditMetric,
            ]
        return super().get_permissions()
