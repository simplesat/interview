from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APITestCase


class SurveyBuilderViewTests(APITestCase):
    def test_returns_questions_choices_and_answer_counts(self):
        survey = baker.make("surveys.Survey", name="Support CSAT")
        rating = baker.make(
            "questions.Question",
            type="rating",
            text="How would you rate our support?",
            is_required=True,
            scale_size=5,
        )
        contact = baker.make(
            "questions.Question", type="single_choice", text="How did you contact us?"
        )
        baker.make("surveys.SurveyQuestion", survey=survey, question=rating, order=0)
        baker.make("surveys.SurveyQuestion", survey=survey, question=contact, order=1)
        points = [
            baker.make(
                "questions.Choice", question=rating, label=label, order=order, value=order + 1
            )
            for order, label in enumerate(["Terrible", "Bad", "Okay", "Good", "Great"])
        ]
        phone, email = [
            baker.make("questions.Choice", question=contact, label=label, order=order)
            for order, label in enumerate(["Phone", "Email"])
        ]
        for rating_value, choice in [(5, phone), (4, email), (5, email)]:
            response = baker.make("answers.Response", survey=survey)
            baker.make("answers.Answer", response=response, question=rating, rating=rating_value)
            baker.make("answers.Answer", response=response, question=contact, choice=choice)

        response = self.client.get(reverse("survey_builder", kwargs={"survey_id": survey.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Support CSAT")
        rating_payload, contact_payload = response.data["questions"]
        self.assertEqual(rating_payload["id"], rating.id)
        self.assertEqual(rating_payload["type"], "rating")
        self.assertEqual(rating_payload["scale_size"], 5)
        self.assertEqual(
            [(c["id"], c["label"], c["value"]) for c in rating_payload["choices"]],
            [(point.id, point.label, point.value) for point in points],
        )
        self.assertEqual(
            [choice["answer_count"] for choice in rating_payload["choices"]], [0, 0, 0, 1, 2]
        )
        self.assertEqual(contact_payload["type"], "single_choice")
        self.assertEqual(
            [(choice["label"], choice["answer_count"]) for choice in contact_payload["choices"]],
            [("Phone", 1), ("Email", 2)],
        )
