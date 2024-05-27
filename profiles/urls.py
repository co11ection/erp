from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_profile, name="view-profile"),
    path("edit-profile/", views.edit_profile, name="edit-profile"),
    path(
        "change_profile_photo/", views.change_profile_photo, name="change-profile-photo"
    ),
    path("change_password/", views.change_password, name="change-password"),
    path("get_all_person/", views.get_all_person, name="get-all-person"),
    path("edit_role/", views.change_role, name="edit-role"),
    path("add_medal/", views.add_medal, name="api_add_medal"),
    path("get_user_profile/", views.get_user_profile, name="get_user_profile"),
    path(
        "schedules/bulk-create/",
        views.ScheduleBulkCreateView.as_view(),
        name="schedule-bulk-create",
    ),
    path(
        "schedules/bulk-delete/",
        views.ScheduleBulkDeleteView.as_view(),
        name="schedule-bulk-delete",
    ),
    path("get_user_result/", views.get_user_result, name="get_user_result"),
    path("change_birth/", views.change_birthday, name="change_birth")
]
