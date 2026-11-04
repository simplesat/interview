from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APITestCase

from questions.models import Question


class SurveySaveViewTests(APITestCase):
    def setUp(self):
        self.survey = baker.make("surveys.Survey", name="Support CSAT")
        self.rating = baker.make(
            "questions.Question",
            type="rating",
            text="How would you rate our support?",
            is_required=True,
            scale_size=3,
        )
        self.contact = baker.make(
            "questions.Question", type="single_choice", text="How did you contact us?"
        )
        baker.make("surveys.SurveyQuestion", survey=self.survey, question=self.rating, order=0)
        baker.make("surveys.SurveyQuestion", survey=self.survey, question=self.contact, order=1)
        for order, label in enumerate(["Bad", "Okay", "Good"]):
            baker.make(
                "questions.Choice", question=self.rating, label=label, order=order, value=order + 1
            )
        for order, label in enumerate(["Phone", "Email"]):
            baker.make("questions.Choice", question=self.contact, label=label, order=order)

    def test_put_changes_a_question_text_and_the_survey_name(self):
        builder_url = reverse("survey_builder", kwargs={"survey_id": self.survey.id})
        payload = self.client.get(builder_url).data
        for question in payload["questions"]:
            for choice in question["choices"]:
                del choice["answer_count"]
        payload["name"] = "Support satisfaction"
        payload["questions"][1]["text"] = "How did you get in touch with us?"

        response = self.client.put(
            reverse("survey_detail", kwargs={"survey_id": self.survey.id}),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Support satisfaction")
        saved = self.client.get(builder_url).data
        self.assertEqual(saved["name"], "Support satisfaction")
        self.assertEqual(
            [question["text"] for question in saved["questions"]],
            ["How would you rate our support?", "How did you get in touch with us?"],
        )
        self.assertEqual(
            [question["id"] for question in saved["questions"]],
            [self.rating.id, self.contact.id],
        )
        self.assertEqual(
            [[c["label"] for c in question["choices"]] for question in saved["questions"]],
            [["Bad", "Okay", "Good"], ["Phone", "Email"]],
        )
        self.assertEqual(Question.objects.count(), 2)
