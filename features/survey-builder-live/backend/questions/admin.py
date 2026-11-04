from django.contrib import admin

from config.readonly_admin import ReadOnlyModelAdmin, ReadOnlyTabularInline
from questions.models import Choice, Question


class ChoiceInline(ReadOnlyTabularInline):
    model = Choice
    fields = ("label", "order", "value")


@admin.register(Question)
class QuestionAdmin(ReadOnlyModelAdmin):
    list_display = ("id", "text", "type", "scale_size", "direction", "is_required")
    list_filter = ("type",)
    search_fields = ("text",)
    inlines = [ChoiceInline]
