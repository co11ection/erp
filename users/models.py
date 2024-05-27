from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from .managers import UserManagers


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ("user", "Пользователь"),
        ("admin", "Администратор"),
        ("owner", "Владелец"),
    )
    email = models.EmailField(primary_key=True, verbose_name="Электронная почта")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    telegram_id = models.PositiveIntegerField(blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения"
    )
    telegram = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Telegram"
    )
    photo = models.ImageField(
        upload_to="upload/", verbose_name="Фотография", blank=True, null=True
    )
    phone_number = models.CharField(max_length=30, verbose_name="Номер телефона")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")
    activation_code = models.CharField(
        max_length=8, blank=True, verbose_name="Код активации"
    )
    role = models.CharField(
        default="user", choices=ROLE_CHOICES, max_length=12, verbose_name="Роль"
    )
    users_and_roles_permission = models.BooleanField(
        default=False, verbose_name="Доступ к пользователя и роли"
    )
    category_metrics_permission = models.BooleanField(
        default=False, verbose_name="Доступ к категори метрик"
    )
    metrics_permission = models.BooleanField(
        default=False, verbose_name="Доступ к метрикам"
    )
    period_permission = models.BooleanField(
        default=False, verbose_name="Доступ к периоду"
    )
    statistick_permission = models.BooleanField(
        default=False, verbose_name="Доступ к статистакам"
    )
    reports_permission = models.BooleanField(
        default=False, verbose_name="Доступ к отчетам"
    )
    create_reports_permission = models.BooleanField(
        default=False, verbose_name="Доступ к заполнению отчета"
    )

    objects = UserManagers()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "middle_name", "last_name", "phone_number"]

    def create_activation_code(self):
        code = get_random_string(length=8)
        self.activation_code = code
        self.save()

    def save(self, *args, **kwargs):
        if (
                self.role == "owner"
                and User.objects.filter(role="owner").exclude(email=self.email).exists()
        ):
            raise ValidationError("Уже существует пользователь с ролью 'Владелец'")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.email}"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
