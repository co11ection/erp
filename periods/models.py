from django.db import models
from goals.models import Goal


# Create your models here.
class Periods(models.Model):
    title = models.CharField(max_length=80)
    start_date = models.DateField()
    end_date = models.DateField()
    goals = models.ManyToManyField(
        Goal,
        blank=True,
        verbose_name="Цели",
        related_name="periods",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Периоды"
        verbose_name_plural = "Период"

    def __str__(self) -> str:
        return f"{self.title} {self.id}"
