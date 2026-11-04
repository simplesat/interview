from django.contrib import admin

from config.readonly_admin import ReadOnlyModelAdmin
from surveys.models import Survey


@admin.register(Survey)
class SurveyAdmin(ReadOnlyModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
