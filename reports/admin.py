from django.contrib import admin
from .models import Reports, ReportComments


@admin.register(Reports)
class ReportsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "created_date",
        "user",
        "period",
        "goal",
    ]


admin.site.register(ReportComments)
