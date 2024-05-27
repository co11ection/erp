from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("reports", views.ReportsViewSet)

urlpatterns = [
    path(
        "reports/<int:report_id>/comments/",
        views.report_comments,
        name="report_comments",
    ),
    path("", include(router.urls)),
    path(
        "reports/report_count/",
        views.ReportsViewSet.as_view({"get": "report_count"}),
        name="report-count",
    ),
    path(
        "reports/get_user_reports/",
        views.ReportsViewSet.as_view({"get": "get_user_reports"}),
    ),
    path(
        "reports/get_user_all_reports/",
        views.ReportsViewSet.as_view({"get": "get_user_all_reports"}),
    ),
    path("comments/", views.CommentListCreateView.as_view()),
    path("comments/<int:pk>/", views.CommentDetailView.as_view()),
    path("report/get_reports_result/", views.get_reports_result),
]
