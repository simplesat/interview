from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from answers.models import Answer
from answers.models import Response as SurveyResponse
from questions.models import Question
from surveys.models import Survey


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    rating = serializers.IntegerField(required=False)
    choice_id = serializers.IntegerField(required=False)


class SurveyResponseSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True)


class SurveyResponseView(APIView):
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, pk=survey_id)
        serializer = SurveyResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        questions = {
            question.id: question
            for question in Question.objects.filter(survey_question__survey=survey)
        }

        rows = []
        answered = set()
        for item in serializer.validated_data["answers"]:
            question = questions.get(item["question_id"])
            if question is None:
                raise ValidationError(f"Question {item['question_id']} is not in this survey.")
            if question.id in answered:
                raise ValidationError(f"Question {question.id} was answered more than once.")
            answered.add(question.id)

            if question.type == Question.RATING:
                rating = item.get("rating")
                if rating is None or not 1 <= rating <= question.scale_size:
                    raise ValidationError(f"Answer to question {question.id} is not a rating.")
                rows.append(Answer(question=question, rating=rating))
            else:
                choice_id = item.get("choice_id")
                if choice_id is None or not question.choices.filter(pk=choice_id).exists():
                    raise ValidationError(f"Answer to question {question.id} is not a choice.")
                rows.append(Answer(question=question, choice_id=choice_id))

        with transaction.atomic():
            response = SurveyResponse.objects.create(survey=survey)
            for row in rows:
                row.response = response
            Answer.objects.bulk_create(rows)

        return Response({"id": response.id}, status=201)
