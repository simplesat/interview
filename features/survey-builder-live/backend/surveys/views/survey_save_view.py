from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from questions.models import Choice, Question
from surveys.config import build_survey_config
from surveys.models import Survey, SurveyQuestion


class ChoiceInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False)
    value = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(max_length=100)


class QuestionInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=Question.TYPE_CHOICES)
    text = serializers.CharField(max_length=300)
    is_required = serializers.BooleanField(required=False, default=False)
    scale_size = serializers.IntegerField(required=False, allow_null=True)
    direction = serializers.ChoiceField(
        choices=Question.DIRECTION_CHOICES, required=False, allow_null=True
    )
    choices = ChoiceInputSerializer(many=True)

    def validate(self, attrs):
        choices = attrs["choices"]
        if attrs["type"] == Question.RATING:
            scale_size = attrs.get("scale_size")
            if scale_size is None or not 2 <= scale_size <= 5:
                raise serializers.ValidationError(
                    {"scale_size": "A rating question needs a scale size from 2 to 5."}
                )
            if len(choices) != scale_size:
                raise serializers.ValidationError(
                    {"choices": "A rating question needs one point for each step of the scale."}
                )
            if [choice.get("value") for choice in choices] != list(range(1, scale_size + 1)):
                raise serializers.ValidationError(
                    {"choices": "Rating points need the values 1 to the scale size, in order."}
                )
        else:
            if attrs.get("scale_size") is not None:
                raise serializers.ValidationError(
                    {"scale_size": "A single choice question has no scale size."}
                )
            if not choices:
                raise serializers.ValidationError(
                    {"choices": "A single choice question needs at least one option."}
                )
            if any(choice.get("value") is not None for choice in choices):
                raise serializers.ValidationError(
                    {"choices": "Single choice options have no value."}
                )
        return attrs


class SurveySaveSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    questions = QuestionInputSerializer(many=True)


class SurveySaveView(APIView):
    def put(self, request, survey_id):
        survey = get_object_or_404(Survey, pk=survey_id)
        serializer = SurveySaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        received = serializer.validated_data["questions"]

        with transaction.atomic():
            survey.name = serializer.validated_data["name"]
            survey.save()

            existing = list(survey.survey_questions.select_related("question").order_by("order"))
            for index, data in enumerate(received):
                if index < len(existing):
                    survey_question = existing[index]
                    question = self.save_question(survey_question.question, data)
                    survey_question.order = index
                    survey_question.save()
                else:
                    question = self.save_question(Question(), data)
                    SurveyQuestion.objects.create(survey=survey, question=question, order=index)
                self.save_choices(question, data["choices"])

            for survey_question in existing[len(received):]:
                survey_question.question.delete()

        return Response(build_survey_config(survey, with_counts=True))

    def save_question(self, question, data):
        question.type = data["type"]
        question.text = data["text"]
        question.is_required = data["is_required"]
        if data["type"] == Question.RATING:
            question.scale_size = data["scale_size"]
            question.direction = data.get("direction") or Question.LOWEST_FIRST
        else:
            question.scale_size = None
            question.direction = Question.LOWEST_FIRST
        question.save()
        return question

    def save_choices(self, question, received):
        existing = list(question.choices.order_by("order"))
        for index, data in enumerate(received):
            choice = existing[index] if index < len(existing) else Choice(question=question)
            choice.label = data["label"]
            choice.value = data.get("value")
            choice.order = index
            choice.save()
        for choice in existing[len(received):]:
            choice.delete()
