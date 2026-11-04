from django.db.models import Count
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from answers.models import Response as SurveyResponse
from surveys.models import Survey


class SurveyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)


class SurveyListView(APIView):
    def get(self, request):
        surveys = Survey.objects.annotate(question_count=Count("survey_questions")).order_by("id")
        response_counts = dict(
            SurveyResponse.objects.values_list("survey_id").annotate(total=Count("id"))
        )
        return Response(
            [
                {
                    "id": survey.id,
                    "name": survey.name,
                    "question_count": survey.question_count,
                    "response_count": response_counts.get(survey.id, 0),
                }
                for survey in surveys
            ]
        )

    def post(self, request):
        serializer = SurveyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        survey = Survey.objects.create(name=serializer.validated_data["name"])
        return Response({"id": survey.id, "name": survey.name}, status=201)
