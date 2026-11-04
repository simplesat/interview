from answers.models import Answer
from questions.models import Question


def build_question_config(question, order, with_counts=True):
    is_rating = question.type == Question.RATING
    choices = []
    for choice in question.choices.all():
        item = {
            "id": choice.id,
            "order": choice.order,
            "value": choice.value,
            "label": choice.label,
        }
        if with_counts:
            if is_rating:
                item["answer_count"] = Answer.objects.filter(
                    question=question, rating=choice.value
                ).count()
            else:
                item["answer_count"] = Answer.objects.filter(
                    question=question, choice=choice
                ).count()
        choices.append(item)

    return {
        "id": question.id,
        "order": order,
        "type": question.type,
        "text": question.text,
        "is_required": question.is_required,
        "scale_size": question.scale_size,
        "direction": question.direction if is_rating else None,
        "choices": choices,
    }


def build_survey_config(survey, with_counts=True):
    questions = []
    for survey_question in survey.survey_questions.all():
        question = survey_question.question
        questions.append(build_question_config(question, survey_question.order, with_counts))
    return {"id": survey.id, "name": survey.name, "questions": questions}
