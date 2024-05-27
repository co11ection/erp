from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_published_news, name="published-news-list"),
    path("toggle-like/", views.toggle_like, name="toggle-like"),
    path("create-news/", views.create_news, name="create-news"),
    path("update-news/<int:news_id>/", views.update_news, name="update-news"),
    path("delete-news/<int:news_id>/", views.delete_news, name="delete-news"),
    path("<int:news_id>/", views.get_single_news, name="get_single_news"),
]
