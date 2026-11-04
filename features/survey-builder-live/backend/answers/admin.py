from django.contrib import admin

from answers.models import Answer, Response
from config.readonly_admin import ReadOnlyModelAdmin, ReadOnlyTabularInline
from questions.models import Question


class AnswerColumns:
    @admin.display(description="question")
    def question_text(self, obj):
        return obj.question.text

    @admin.display(description="picked")
    def picked(self, obj):
        if obj.question.type == Question.SINGLE_CHOICE:
            return obj.choice.label if obj.choice else "—"
        for choice in obj.question.choices.all():
            if choice.value == obj.rating:
                return choice.label
        return "—"

    @admin.display(description="scale size")
    def scale_size(self, obj):
        return obj.question.scale_size


class AnswerInline(AnswerColumns, ReadOnlyTabularInline):
    model = Answer
    fields = ("question_text", "picked", "rating", "scale_size")
    readonly_fields = fields

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("question", "choice")
            .prefetch_related("question__choices")
        )


@admin.register(Answer)
class AnswerAdmin(AnswerColumns, ReadOnlyModelAdmin):
    list_display = (
        "response",
        "survey_name",
        "question_text",
        "picked",
        "rating",
        "scale_size",
    )
    list_filter = ("response__survey",)
    list_select_related = ("response__survey", "question", "choice")
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("question__choices")

    @admin.display(description="survey", ordering="response__survey__name")
    def survey_name(self, obj):
        return obj.response.survey.name


@admin.register(Response)
class ResponseAdmin(ReadOnlyModelAdmin):
    list_display = ("id", "survey", "submitted_at")
    list_filter = ("survey",)
    list_select_related = ("survey",)
    inlines = [AnswerInline]
