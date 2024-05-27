from django.contrib import admin
from .models import UserProfile, UserMedal, Schedule


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "telegram_username",
        "notification_time",
        "notification_frequency",
        "days_without_skip",
        "display_medals",
    ]
    list_filter = []

    def display_medals(self, obj):
        return ", ".join([str(medal) for medal in obj.medals.all()])

    display_medals.short_description = "Medals"
    
    def telegram_username(self, obj):
        return obj.user.telegram_username


admin.site.register(UserMedal)
admin.site.register(Schedule)
