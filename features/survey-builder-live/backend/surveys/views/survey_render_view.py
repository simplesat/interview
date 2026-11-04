from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from surveys.config import build_survey_config
from surveys.models import Survey


class SurveyRenderView(APIView):
    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, pk=survey_id)
        return Response(build_survey_config(survey, with_counts=False))
