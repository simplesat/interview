import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from answers.models import Answer, Response
from questions.models import Choice, Question
from questions.scales import DEFAULT_LABELS
from surveys.models import Survey, SurveyQuestion

RESPONSES_PER_SURVEY = 60
HISTORY_DAYS = 21

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

SUPPORT_TEXT = "How would you rate our support today?"
CONTACT_TEXT = "How did you contact us?"


def rating(text, counts, is_required=False, direction=Question.LOWEST_FIRST):
    return {
        "type": Question.RATING,
        "text": text,
        "is_required": is_required,
        "direction": direction,
        "counts": counts,
        "labels": DEFAULT_LABELS[len(counts)],
    }


def single_choice(text, options, is_required=False):
    return {
        "type": Question.SINGLE_CHOICE,
        "text": text,
        "is_required": is_required,
        "direction": Question.LOWEST_FIRST,
        "counts": [count for _, count in options],
        "labels": [label for label, _ in options],
    }


SURVEYS = [
    (
        "Support CSAT",
        [
            rating(SUPPORT_TEXT, [4, 7, 12, 20, 17], is_required=True),
            single_choice(
                CONTACT_TEXT,
                [("Phone", 9), ("Email", 22), ("Chat", 14), ("Social", 10)],
            ),
            rating("How easy was it to get help?", [3, 6, 10, 19, 14]),
            single_choice(
                "Which plan are you on?",
                [("Starter", 24), ("Team", 20), ("Business", 11)],
            ),
        ],
    ),
    (
        "Support CSAT (highest first)",
        [
            rating(
                SUPPORT_TEXT,
                [2, 6, 11, 19, 22],
                is_required=True,
                direction=Question.HIGHEST_FIRST,
            ),
            single_choice(
                CONTACT_TEXT,
                [("Phone", 8), ("Email", 21), ("Chat", 16), ("Social", 9)],
            ),
        ],
    ),
    (
        "Onboarding check-in",
        [
            rating("How was onboarding?", [9, 21, 26]),
            rating("Would you recommend us?", [14, 39]),
        ],
    ),
]


def submission_times(rng, total):
    now = timezone.now()
    minutes = sorted(rng.randint(0, HISTORY_DAYS * 24 * 60) for _ in range(total))
    return [now - timedelta(minutes=offset) for offset in reversed(minutes)]


def skipped_slots(rng, total, skips):
    order = rng.sample(range(total), total)
    slots = []
    start = 0
    for count in skips:
        slots.append(set(order[start:start + count]))
        start += count
    return slots


def picks_for(rng, counts, skipped, total):
    values = [index for index, count in enumerate(counts) for _ in range(count)]
    rng.shuffle(values)
    picks = [None] * total
    answering = [slot for slot in range(total) if slot not in skipped]
    for slot, value in zip(answering, values):
        picks[slot] = value
    return picks


def create_question(survey, order, spec):
    is_rating = spec["type"] == Question.RATING
    question = Question.objects.create(
        type=spec["type"],
        text=spec["text"],
        is_required=spec["is_required"],
        scale_size=len(spec["counts"]) if is_rating else None,
        direction=spec["direction"],
    )
    choices = Choice.objects.bulk_create(
        [
            Choice(
                question=question,
                label=label,
                order=position,
                value=position + 1 if is_rating else None,
            )
            for position, label in enumerate(spec["labels"])
        ]
    )
    SurveyQuestion.objects.create(survey=survey, question=question, order=order)
    return question, choices


class Command(BaseCommand):
    help = "Load the small demo data set"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all survey data before loading",
        )

    def handle(self, *args, **options):
        self.ensure_admin()
        if options["clear"]:
            self.clear()
        elif Survey.objects.exists():
            self.stdout.write("already seeded")
            return

        rng = random.Random(1337)
        with transaction.atomic():
            for name, specs in SURVEYS:
                self.create_survey(rng, name, specs)
        self.stdout.write(
            f"Seeded {Survey.objects.count()} surveys, "
            f"{Response.objects.count()} responses, "
            f"{Answer.objects.count()} answers"
        )

    def ensure_admin(self):
        User = get_user_model()
        if User.objects.filter(username=ADMIN_USERNAME).exists():
            return
        User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
        self.stdout.write(f"Created superuser {ADMIN_USERNAME}")

    def clear(self):
        tables = [
            model._meta.db_table
            for model in (
                Answer,
                Response,
                SurveyQuestion,
                Survey,
                Choice,
                Question,
            )
        ]
        names = ", ".join(connection.ops.quote_name(table) for table in tables)
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE {names} RESTART IDENTITY CASCADE")

    def create_survey(self, rng, name, specs):
        total = RESPONSES_PER_SURVEY
        survey = Survey.objects.create(name=name)
        built = [
            create_question(survey, order, spec) for order, spec in enumerate(specs)
        ]

        optional = [spec for spec in specs if not spec["is_required"]]
        skips = [total - sum(spec["counts"]) for spec in optional]
        slots = iter(skipped_slots(rng, total, skips))
        picks = []
        for spec in specs:
            skipped = set() if spec["is_required"] else next(slots)
            picks.append(picks_for(rng, spec["counts"], skipped, total))

        responses = Response.objects.bulk_create(
            [
                Response(survey=survey, submitted_at=stamp)
                for stamp in submission_times(rng, total)
            ]
        )
        answers = []
        for slot, response in enumerate(responses):
            for (question, choices), spec, column in zip(built, specs, picks):
                pick = column[slot]
                if pick is None:
                    continue
                if spec["type"] == Question.RATING:
                    answers.append(
                        Answer(response=response, question=question, rating=pick + 1)
                    )
                else:
                    answers.append(
                        Answer(response=response, question=question, choice=choices[pick])
                    )
        Answer.objects.bulk_create(answers)
        return survey
