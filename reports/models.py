from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from periods.models import Periods
from goals.models import Goal

User = get_user_model()

HIRE_MAID_CHOISE = (("yes", "Да"), ("no", "Нет"))


class Reports(models.Model):
    hire_maid = models.CharField(max_length=10, choices=HIRE_MAID_CHOISE, null=True, blank=True)
    hire_maid_comment = models.TextField(blank=True, null=True)
    created_date = models.DateField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    revenue_comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports", verbose_name="user"
    )
    period = models.ForeignKey(
        Periods, on_delete=models.CASCADE, related_name="reports", verbose_name="period"
    )
    goal = models.ForeignKey(
        Goal, on_delete=models.CASCADE, related_name="reports", verbose_name="goal"
    )

    def __str__(self) -> str:
        return f"{self.user} {self.pk}"

    class Meta:
        ordering = ["pk"]
        verbose_name = "Отчеты"
        verbose_name_plural = "Отчет"


class ReportComments(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    report = models.ForeignKey(
        Reports, related_name="comments", on_delete=models.CASCADE
    )
    body = models.TextField()
    created_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user} -> {self.report} -> {self.created_at}"

    class Meta:
        verbose_name = "Комментарии отчетов"
        verbose_name_plural = "Комментарии отчетов"
