from django.db import models


class Survey(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SurveyQuestion(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="survey_questions"
    )
    question = models.OneToOneField(
        "questions.Question", on_delete=models.CASCADE, related_name="survey_question"
    )
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
