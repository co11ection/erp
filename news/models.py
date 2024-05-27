from django.db import models
from users.models import User


class News(models.Model):
    STATUS_PUBLISHED = "Опубликовано"
    STATUS_ARCHIVED = "Архив"
    STATUS_PENDING = "В ожидании"

    STATUS_CHOICES = (
        (STATUS_ARCHIVED, "Архив"),
        (STATUS_PUBLISHED, "Опубликовано"),
        (STATUS_PENDING, "В ожидании"),
    )

    title = models.CharField(max_length=250, verbose_name="Заголовок", unique=True)
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField(verbose_name="Изображение", blank=True, null=True)
    documents = models.FileField(upload_to="uploads/%Y/%m/%d/", blank=True, null=True)
    pub_date = models.DateTimeField(verbose_name="Дата и время публикации новости.")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="В ожидании",
        verbose_name="Статус новости",
    )

    total_likes = models.ManyToManyField(
        User, related_name="liked_news", through="Like", verbose_name="Лайки"
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return f"Создана новость {self.title}. Статус {self.status}"


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name="Новость")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        ordering = ("date_created",)
        unique_together = ("user", "news")  # Уникальность по полю user и news

    def __str__(self):
        return f"Лайк от {self.user} на Новость {self.news}"
