from django.urls import re_path

from surveys.views import SurveyBuilderView, SurveyListView, SurveyRenderView, SurveySaveView

urlpatterns = [
    re_path(r"^surveys/$", SurveyListView.as_view(), name="survey_list"),
    re_path(r"^surveys/(?P<survey_id>\d+)/$", SurveySaveView.as_view(), name="survey_detail"),
    re_path(
        r"^surveys/(?P<survey_id>\d+)/builder/$",
        SurveyBuilderView.as_view(),
        name="survey_builder",
    ),
    re_path(
        r"^surveys/(?P<survey_id>\d+)/render/$",
        SurveyRenderView.as_view(),
        name="survey_render",
    ),
]
