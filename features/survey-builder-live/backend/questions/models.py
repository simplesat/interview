from django.db import models


class Question(models.Model):
    RATING = "rating"
    SINGLE_CHOICE = "single_choice"
    TYPE_CHOICES = [
        (RATING, "Rating"),
        (SINGLE_CHOICE, "Single choice"),
    ]

    LOWEST_FIRST = "lowest_first"
    HIGHEST_FIRST = "highest_first"
    DIRECTION_CHOICES = [
        (LOWEST_FIRST, "Lowest first"),
        (HIGHEST_FIRST, "Highest first"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.CharField(max_length=300)
    is_required = models.BooleanField(default=False)
    scale_size = models.PositiveSmallIntegerField(null=True, blank=True)
    direction = models.CharField(
        max_length=20, choices=DIRECTION_CHOICES, default=LOWEST_FIRST
    )

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    value = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label
