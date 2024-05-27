from django.db import models
from slugify import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    CATEGORY_CHOICES = (
        ("financial", "Финансовая"),
        ("process", "Процессная"),
        ("client", "Клиентская"),
        ("team", "Командная"),
    )

    slug = models.SlugField(max_length=50, primary_key=True, blank=True, unique=True)
    title = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = "Категория метрик"
        verbose_name_plural = "Категории метрик"


@receiver(pre_save, sender=Category)
def category_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        base_slug = slugify(instance.title)
        instance.slug = base_slug
