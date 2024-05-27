from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Reports
from datetime import date, datetime
from profiles.models import UserProfile


@receiver(pre_save, sender=Reports)
def update_days_without_skip(sender, instance, **kwargs):
    today = date.today()
    user = UserProfile.objects.get(user=instance.user)

    if not sender.objects.filter(user=instance.user, created_date=today):
        user.days_without_skip += 1
        user.save()

    user.save()
