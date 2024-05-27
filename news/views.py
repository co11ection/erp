from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from news.models import News, Like
from news.serializers import NewsSerializer
from news.services import LikeService
from users.permissions import (
    CanCreateEditDeleteNews,
    CanViewNews,
    CanSendNewsToEmployees,
    CanReactToNews,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanViewNews])
def get_published_news(request):
    """
    Получает опубликованные новости.

    Методы:
    - get() - получение всех новостей

    Получаемые поля:
    "id",
    "title",
    "text",
    "image",
    "pub_date",
    "status",
    "total_likes",
    "user_liked"
    """
    published_news = News.objects.filter(status="Опубликовано")
    serializer = NewsSerializer(published_news, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, CanReactToNews])
def toggle_like(request):
    """
        Переключает лайк для новости.

        Отправить в headers токен
        Пример Body {
        "news_id":1
    }"""

    user = request.user
    news_id = request.data.get("news_id")
    news = get_object_or_404(News, pk=news_id, status="Опубликовано")
    liked = LikeService.toggle_like(user, news)
    serializer = NewsSerializer(news)
    return Response({"liked": liked, "news": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated, CanCreateEditDeleteNews])
def create_news(request):
    """
    Создает новость. Доступно только для владельцев.

    Поля:
    "title",
    "text",
    "image",
    "pub_date",
    "status",
    "total_likes",
    """
    serializer = NewsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, CanCreateEditDeleteNews])
def update_news(request, news_id):
    """
    Обновляет новость. Доступно только для владельцев.

    Методы:
    -put(id) - обновление новости(полное)
    -patch(id) - обноыление новости(частичное)

    Поля:
    "id",
    "title",
    "text",
    "image",
    "pub_date",
    "status",
    "total_likes",
    "user_liked"
    """
    news = get_object_or_404(News, pk=news_id)
    serializer = NewsSerializer(news, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, CanCreateEditDeleteNews])
def delete_news(request, news_id):
    """
    Удаляет новость. Доступно только для владельцев.

    Методы:
    delete(id) - удаление новости

    """
    news = get_object_or_404(News, pk=news_id)
    news.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def get_single_news(request, news_id):
    try:
        news = News.objects.get(pk=news_id)
    except News.DoesNotExist:
        return Response({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the news data
    serializer = NewsSerializer(news)

    return Response(serializer.data)
