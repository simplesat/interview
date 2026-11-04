from django.db import models
from django.utils import timezone


class Response(models.Model):
    survey = models.ForeignKey(
        "surveys.Survey", on_delete=models.CASCADE, related_name="responses"
    )
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Response {self.pk}"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(
        "questions.Question", on_delete=models.CASCADE, related_name="answers"
    )
    choice = models.ForeignKey(
        "questions.Choice",
        on_delete=models.CASCADE,
        related_name="answers",
        null=True,
        blank=True,
    )
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
