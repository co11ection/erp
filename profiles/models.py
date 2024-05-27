from django.db import models
from users.models import User


class UserMedal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="medal_icons/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Медали"
        verbose_name_plural = "Медаль"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_sync_date = models.DateTimeField(blank=True, null=True)
    notification_time = models.TimeField(blank=True, null=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Ежедневно"),
            ("weekly", "Еженедельно"),
            ("monthly", "Ежемесячно"),
        ],
        blank=True,
        null=True,
    )
    days_without_skip = models.PositiveIntegerField(default=0)
    medals = models.ManyToManyField(UserMedal, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "Профили"
        verbose_name_plural = "Профиль"


class Schedule(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="user_schedule"
    )
    date = models.DateField()
    is_working = models.BooleanField(default=False)

    class Meta:
        verbose_name = "График работы"
        verbose_name_plural = "График работы"
