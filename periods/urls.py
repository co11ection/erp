from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("periods", views.PeriodViews)

urlpatterns = [
    path("periods/result", views.get_copmare_result_period),
    path("", include(router.urls)),
]
