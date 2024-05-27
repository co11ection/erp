from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from metrics_category.models import Category

User = get_user_model()

DIGITAL_RANGE_CHOICES = (
    ("integer", "Целое"),
    ("fractional", "Дробное"),
    ("percentage", "Процентное"),
    ("Yes/No", "Да/Нет")
)

CALCULATION_TYPE_CHOICES = (
    ("sum", "Сумма"),
    ("average", "Среднее"),
    ("last_day", "Показатель за последний день"),
)


class Goal(models.Model):
    name = models.CharField(max_length=50)
    user_created = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals_creator",
        verbose_name="Автор",
    )
    metrics_name = models.CharField(max_length=50)
    is_persistent = models.BooleanField(default=False)
    digit_range = models.CharField(max_length=10, choices=DIGITAL_RANGE_CHOICES)
    calculation_type = models.CharField(
        max_length=30, choices=CALCULATION_TYPE_CHOICES, blank=True, null=True
    )
    reverse_calculation = models.BooleanField(default=False)
    version_history = models.JSONField(default=list, blank=True)
    is_change = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    number_range_initial = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    number_range_finally = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    responsible_user = models.ManyToManyField(
        User, related_name="responsible_for_goals", verbose_name="user", blank=True
    )
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=1),
        ],
    )
    weight_of_perspective = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=1),
        ],
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="goals_category",
        verbose_name="category",
    )

    def __str__(self) -> str:
        return f"{self.name} {self.pk}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not is_new:
            old_obj = self.__class__.objects.get(id=self.id)
            responsible_users = list(old_obj.responsible_user.all())
            responsible_user_ids = [
                f"{user.first_name} {user.last_name}" for user in responsible_users
            ]
            version_data = {
                "id": old_obj.pk,
                "name": old_obj.name,
                "metrics_name": old_obj.metrics_name,
                "category": old_obj.category.slug,
                "digit_range": old_obj.digit_range,
                "number_range_initial": str(old_obj.number_range_initial),
                "number_range_finally": str(old_obj.number_range_finally),
                "calculation_type": old_obj.calculation_type,
                "reverse_calculation": old_obj.reverse_calculation,
                "weight": str(old_obj.weight),
                "is_active": old_obj.is_active,
                "is_persistent": old_obj.is_persistent,
                "weight_of_perspective": str(old_obj.weight_of_perspective),
                "responsible_user": responsible_user_ids,
            }
            self.version_history = version_data
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Метрика и цель"
        verbose_name_plural = "Метрики и цели"


class PendingEditRequest(models.Model):
    goals = models.ForeignKey(Goal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    data_to_update = models.JSONField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Pending edit request for {self.goals.name} by {self.user}"
