from django.urls import reverse
from rest_framework.test import APITestCase

from surveys.models import Survey


class SurveyListViewTests(APITestCase):
    def test_post_creates_an_empty_survey(self):
        response = self.client.post(reverse("survey_list"), {"name": "Onboarding"}, format="json")

        self.assertEqual(response.status_code, 201)
        survey = Survey.objects.get(pk=response.data["id"])
        self.assertEqual(response.data, {"id": survey.id, "name": "Onboarding"})
        self.assertEqual(survey.name, "Onboarding")
        self.assertEqual(survey.survey_questions.count(), 0)
