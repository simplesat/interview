import random
import time
from bisect import bisect_right
from datetime import timedelta
from itertools import accumulate

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from answers.models import Answer, Response
from questions.models import Choice, Question
from questions.scales import DEFAULT_LABELS
from surveys.models import Survey, SurveyQuestion

SURVEY_NAME = "Big survey"

RESPONSES = 200_000
CHUNK_SIZE = 10_000
ANSWERS_PER_RESPONSE = (11, 15)
HISTORY_DAYS = 90
SCALE_SIZE = 5

LAYOUT = ["rating", "rating", "choice"] * 20
REQUIRED_RATINGS = {0, 14, 28}
REQUIRED_CHOICES = {0, 10}

RATING_PROFILES = [
    [4, 8, 16, 32, 40],
    [40, 30, 15, 10, 5],
    [10, 15, 40, 25, 10],
    [30, 10, 5, 15, 40],
    [5, 10, 20, 35, 30],
    [20, 25, 30, 15, 10],
]

RATING_TEXTS = [
    "How would you rate our support today?",
    "How would you rate the speed of our first reply?",
    "How would you rate how clearly we explained the solution?",
    "How would you rate the friendliness of our team?",
    "How would you rate our product knowledge?",
    "How would you rate how easy it was to reach us?",
    "How would you rate the time it took to fix your issue?",
    "How would you rate our help center articles?",
    "How would you rate the onboarding session?",
    "How would you rate the setup instructions?",
    "How would you rate the billing process?",
    "How would you rate how we handled your refund?",
    "How would you rate the mobile app?",
    "How would you rate the web dashboard?",
    "How would you rate the reporting features?",
    "How would you rate the import tools?",
    "How would you rate our API documentation?",
    "How would you rate the integration setup?",
    "How would you rate notifications and alerts?",
    "How would you rate the reliability of the product?",
    "How would you rate performance on large accounts?",
    "How would you rate the search experience?",
    "How would you rate the permissions and roles settings?",
    "How would you rate the quality of our release notes?",
    "How would you rate our status page updates?",
    "How would you rate the training webinar?",
    "How would you rate the community forum?",
    "How would you rate your account manager?",
    "How would you rate the renewal experience?",
    "How would you rate us overall?",
    "How would you rate the clarity of our pricing?",
    "How would you rate the speed of the dashboard?",
    "How would you rate our survey templates?",
    "How would you rate the export options?",
    "How would you rate the quality of our emails?",
    "How would you rate how well we protect your data?",
    "How would you rate how easy it is to invite teammates?",
    "How would you rate the automation features?",
    "How would you rate the accuracy of the reports?",
    "How would you rate our customer success calls?",
]

CHOICE_QUESTIONS = [
    (
        "How did you contact us?",
        [
            "Email",
            "Phone",
            "Chat",
            "Social media",
            "Help center form",
            "In-app message",
            "Community forum",
        ],
    ),
    ("Which plan are you on?", ["Free", "Starter", "Growth", "Business", "Enterprise", "Not sure"]),
    (
        "How big is your team?",
        ["Just me", "2-5", "6-10", "11-25", "26-50", "51-200", "More than 200"],
    ),
    (
        "What is your role?",
        [
            "Owner or founder",
            "Support agent",
            "Support manager",
            "Product manager",
            "Engineer",
            "Operations",
            "Marketing",
            "Other",
        ],
    ),
    (
        "How long have you been a customer?",
        [
            "Under a month",
            "1-3 months",
            "3-6 months",
            "6-12 months",
            "1-2 years",
            "2-3 years",
            "Over 3 years",
        ],
    ),
    (
        "Which device did you use?",
        [
            "Windows laptop",
            "Mac laptop",
            "Linux desktop",
            "iPhone",
            "Android phone",
            "iPad",
            "Android tablet",
        ],
    ),
    (
        "Which browser did you use?",
        ["Chrome", "Safari", "Firefox", "Edge", "Arc", "Brave", "Other"],
    ),
    (
        "Which area did you need help with?",
        [
            "Billing",
            "Account access",
            "Integrations",
            "Reports",
            "Notifications",
            "Imports",
            "Permissions",
            "Something else",
        ],
    ),
    (
        "How did you hear about us?",
        [
            "Search engine",
            "Colleague",
            "Social media",
            "Review site",
            "Conference",
            "Newsletter",
            "Podcast",
            "Other",
        ],
    ),
    (
        "How often do you use the product?",
        [
            "Several times a day",
            "Daily",
            "A few times a week",
            "Weekly",
            "Monthly",
            "Rarely",
        ],
    ),
    (
        "Which industry are you in?",
        [
            "Software",
            "Retail",
            "Healthcare",
            "Finance",
            "Education",
            "Hospitality",
            "Manufacturing",
            "Other",
        ],
    ),
    (
        "Which region are you in?",
        [
            "North America",
            "South America",
            "Western Europe",
            "Eastern Europe",
            "Middle East and Africa",
            "South Asia",
            "East Asia",
            "Oceania",
        ],
    ),
    (
        "Which feature do you use most?",
        ["Surveys", "Dashboards", "Alerts", "Exports", "Integrations", "Automations"],
    ),
    (
        "How did you get started?",
        [
            "Self-serve signup",
            "Sales demo",
            "Partner referral",
            "Free trial",
            "Migration from another tool",
            "Invited by a colleague",
        ],
    ),
    (
        "Which integration do you use?",
        ["Zendesk", "Intercom", "Freshdesk", "Salesforce", "HubSpot", "Slack", "Email only"],
    ),
    (
        "What was the main reason you contacted us?",
        [
            "Question about a feature",
            "Something is broken",
            "Billing question",
            "Request for a feature",
            "Account change",
            "Cancellation",
            "Other",
        ],
    ),
    (
        "How urgent was your request?",
        [
            "Blocking my work",
            "Needs a fix today",
            "Needs a fix this week",
            "Can wait",
            "Just curious",
            "Not sure",
        ],
    ),
    (
        "Who resolved your issue?",
        ["First agent", "Second agent", "A specialist", "A manager", "A bot", "Nobody yet"],
    ),
    (
        "How many tickets did you open this month?",
        ["None", "1", "2", "3-5", "6-10", "11-20", "More than 20"],
    ),
    (
        "Which language do you prefer for support?",
        ["English", "Spanish", "French", "German", "Portuguese", "Japanese", "Other"],
    ),
]


class Command(BaseCommand):
    help = "Load one large survey with about 200k responses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete the large survey and its responses before loading",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.clear()
        elif Survey.objects.filter(name=SURVEY_NAME).exists():
            self.stdout.write("already seeded")
            return

        rng = random.Random(1337)
        started = time.monotonic()
        with transaction.atomic():
            survey, specs = self.create_survey(rng)
            answer_total = self.load_responses(rng, survey, specs)
        self.analyze()
        elapsed = time.monotonic() - started
        self.stdout.write(
            f"Loaded {len(specs)} questions, {RESPONSES} responses and "
            f"{answer_total} answers into survey {survey.id} in {elapsed:.0f}s"
        )

    def clear(self):
        survey_ids = list(
            Survey.objects.filter(name=SURVEY_NAME).values_list("id", flat=True)
        )
        if not survey_ids:
            return
        question_ids = list(
            SurveyQuestion.objects.filter(survey_id__in=survey_ids).values_list(
                "question_id", flat=True
            )
        )
        answers = Answer._meta.db_table
        responses = Response._meta.db_table
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM {answers} WHERE question_id = ANY(%s)", [question_ids]
                )
                cursor.execute(
                    f"DELETE FROM {responses} WHERE survey_id = ANY(%s)", [survey_ids]
                )
            Question.objects.filter(id__in=question_ids).delete()
            Survey.objects.filter(id__in=survey_ids).delete()
        self.vacuum("VACUUM FULL", (Answer, Response))

    def create_survey(self, rng):
        survey = Survey.objects.create(name=SURVEY_NAME)
        specs = []
        ratings = iter(range(len(RATING_TEXTS)))
        choices = iter(range(len(CHOICE_QUESTIONS)))
        for order, kind in enumerate(LAYOUT):
            if kind == "rating":
                specs.append(self.create_rating(rng, survey, order, next(ratings)))
            else:
                specs.append(self.create_choice_question(rng, survey, order, next(choices)))
        return survey, specs

    def create_rating(self, rng, survey, order, index):
        question = Question.objects.create(
            type=Question.RATING,
            text=RATING_TEXTS[index],
            is_required=index in REQUIRED_RATINGS,
            scale_size=SCALE_SIZE,
            direction=Question.LOWEST_FIRST,
        )
        Choice.objects.bulk_create(
            [
                Choice(question=question, label=label, order=position, value=position + 1)
                for position, label in enumerate(DEFAULT_LABELS[SCALE_SIZE])
            ]
        )
        SurveyQuestion.objects.create(survey=survey, question=question, order=order)
        profile = RATING_PROFILES[index % len(RATING_PROFILES)]
        weights = [max(1, round(weight * rng.uniform(0.7, 1.3))) for weight in profile]
        return {
            "id": question.id,
            "is_required": question.is_required,
            "choice_ids": None,
            "cutoffs": list(accumulate(weights)),
        }

    def create_choice_question(self, rng, survey, order, index):
        text, labels = CHOICE_QUESTIONS[index]
        question = Question.objects.create(
            type=Question.SINGLE_CHOICE,
            text=text,
            is_required=index in REQUIRED_CHOICES,
        )
        choices = Choice.objects.bulk_create(
            [
                Choice(question=question, label=label, order=position)
                for position, label in enumerate(labels)
            ]
        )
        SurveyQuestion.objects.create(survey=survey, question=question, order=order)
        weights = [rng.randint(3, 40) for _ in labels]
        return {
            "id": question.id,
            "is_required": question.is_required,
            "choice_ids": [choice.id for choice in choices],
            "cutoffs": list(accumulate(weights)),
        }

    def load_responses(self, rng, survey, specs):
        responses_table = Response._meta.db_table
        answers_table = Answer._meta.db_table
        required = [spec for spec in specs if spec["is_required"]]
        optional = [spec for spec in specs if not spec["is_required"]]
        low, high = ANSWERS_PER_RESPONSE

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {responses_table}")
            next_id = cursor.fetchone()[0] + 1

        start = timezone.now() - timedelta(days=HISTORY_DAYS)
        step = timedelta(days=HISTORY_DAYS) / RESPONSES
        answer_total = 0

        with connection.cursor() as cursor:
            raw = cursor.cursor
            for chunk_start in range(0, RESPONSES, CHUNK_SIZE):
                size = min(CHUNK_SIZE, RESPONSES - chunk_start)
                response_rows = []
                answer_rows = []
                for offset in range(size):
                    response_id = next_id + chunk_start + offset
                    response_rows.append(
                        (response_id, survey.id, start + step * (chunk_start + offset))
                    )
                    extra = rng.randint(low, high) - len(required)
                    for spec in required + rng.sample(optional, extra):
                        cutoffs = spec["cutoffs"]
                        position = bisect_right(cutoffs, rng.random() * cutoffs[-1])
                        if spec["choice_ids"] is None:
                            answer_rows.append((response_id, spec["id"], None, position + 1))
                        else:
                            answer_rows.append(
                                (response_id, spec["id"], spec["choice_ids"][position], None)
                            )
                self.copy_rows(
                    raw, responses_table, ("id", "survey_id", "submitted_at"), response_rows
                )
                self.copy_rows(
                    raw,
                    answers_table,
                    ("response_id", "question_id", "choice_id", "rating"),
                    answer_rows,
                )
                answer_total += len(answer_rows)
                done = chunk_start + size
                if done % (CHUNK_SIZE * 5) == 0:
                    self.stdout.write(f"  {done} of {RESPONSES} responses")

            cursor.execute(
                f"SELECT setval(pg_get_serial_sequence('{responses_table}', 'id'), "
                f"(SELECT MAX(id) FROM {responses_table}))"
            )
        return answer_total

    def copy_rows(self, raw, table, columns, rows):
        statement = f"COPY {table} ({', '.join(columns)}) FROM STDIN"
        with raw.copy(statement) as copy:
            for row in rows:
                copy.write_row(row)

    def analyze(self):
        self.vacuum("VACUUM ANALYZE", (Response, Answer, Choice, Question))

    def vacuum(self, command, models):
        tables = ", ".join(model._meta.db_table for model in models)
        with connection.cursor() as cursor:
            cursor.execute(f"{command} {tables}")
