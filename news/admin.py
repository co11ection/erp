from django.contrib import admin
from .models import News, Like


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "pub_date",
        "status",
        "get_likes_count",
    )  # Используем метод get_likes_count
    list_filter = ("status", "pub_date")
    search_fields = ("title", "text")

    def get_likes_count(self, obj):
        return obj.total_likes.count()  # Возвращаем количество лайков

    get_likes_count.short_description = (
        "Количество лайков"  # Определяем название для колонки в админке
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "news", "date_created")
    list_filter = ("date_created",)
    search_fields = ("user__username", "news__title")
