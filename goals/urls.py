from django.urls import path, include
from rest_framework.routers import DefaultRouter


from . import views
from metrics_category.views import MetricsCategoryView

router = DefaultRouter()
router.register("category", MetricsCategoryView)
router.register("goal", views.GoalViewset)


urlpatterns = [
    path("goal/list_edit/", views.get_list_edit_request),
    path(
        "goal/<int:goal_id>/create_edit_request/",
        views.EditRequestCreateView.as_view(),
        name="create_edit_request",
    ),
    path(
        "goal/edit_request/",
        views.edit_request_list,
        name="edit_request",
    ),
    path(
        "goal/edit_request/<int:pk>/approve/",
        views.EditRequestApprovalView.as_view(),
        name="approve_edit_request",
    ),
    path("goal/count_pending_reques/", views.count_pending_edit_request),
    path(
        "goal/pending-edit-request/<int:pk>/delete/",
        views.PendingEditRequestDeleteAPIView.as_view(),
        name="delete_pending_edit_request_api",
    ),
    path('goal/user/', views.user_metrics_for_last_period, name='api-user-metrics'),
    path("", include(router.urls)),
]
