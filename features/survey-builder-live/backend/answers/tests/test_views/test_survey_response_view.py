from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APITestCase

from answers.models import Answer


class SurveyResponseViewTests(APITestCase):
    def test_post_saves_a_rating_answer_and_a_single_choice_answer(self):
        survey = baker.make("surveys.Survey")
        rating = baker.make(
            "questions.Question", type="rating", text="How was it?", scale_size=5
        )
        contact = baker.make(
            "questions.Question", type="single_choice", text="How did you contact us?"
        )
        baker.make("surveys.SurveyQuestion", survey=survey, question=rating, order=0)
        baker.make("surveys.SurveyQuestion", survey=survey, question=contact, order=1)
        for order, label in enumerate(["Terrible", "Bad", "Okay", "Good", "Great"]):
            baker.make(
                "questions.Choice", question=rating, label=label, order=order, value=order + 1
            )
        phone, email = [
            baker.make("questions.Choice", question=contact, label=label, order=order)
            for order, label in enumerate(["Phone", "Email"])
        ]

        response = self.client.post(
            reverse("survey_responses", kwargs={"survey_id": survey.id}),
            {
                "answers": [
                    {"question_id": rating.id, "rating": 4},
                    {"question_id": contact.id, "choice_id": email.id},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        answers = Answer.objects.filter(response_id=response.data["id"])
        self.assertEqual(answers.count(), 2)
        self.assertEqual(answers.get(question=rating).rating, 4)
        self.assertEqual(answers.get(question=contact).choice, email)
