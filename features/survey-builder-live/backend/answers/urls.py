from django.urls import re_path

from answers.views import SurveyResponseView

urlpatterns = [
    re_path(
        r"^surveys/(?P<survey_id>\d+)/responses/$",
        SurveyResponseView.as_view(),
        name="survey_responses",
    ),
]
