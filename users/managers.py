from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class UserManagers(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email должен быть заполнен")

        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_employer", False)
        return self._create(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        return self._create(email=email, password=password, **extra_fields)
