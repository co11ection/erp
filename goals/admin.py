from django.contrib import admin
from .models import Goal, PendingEditRequest

# Register your models here.

admin.site.register(Goal)


@admin.register(PendingEditRequest)
class DataForApp(admin.ModelAdmin):
    list_display = ["id", "goals", "user", "request_date", "data_to_update", "approved"]
