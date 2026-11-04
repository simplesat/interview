import { useState } from 'react';
import { Button, Form, Message, Radio } from 'semantic-ui-react';
import { AnswerInput, Survey } from '../../types';

interface SurveyPreviewProps {
  survey: Survey;
  mode: 'preview' | 'live';
  onSubmit?: (answers: AnswerInput[]) => void | Promise<void>;
}

export default function SurveyPreview({ survey, mode, onSubmit }: SurveyPreviewProps) {
  const [picked, setPicked] = useState<Record<number, number>>({});
  const [touched, setTouched] = useState<Set<number>>(new Set());
  const [errors, setErrors] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const pick = (questionKey: number, index: number) => {
    setPicked((current) => {
      if (current[questionKey] === index) {
        const { [questionKey]: removed, ...rest } = current;
        return rest;
      }
      return { ...current, [questionKey]: index };
    });
    setTouched((current) => new Set(current).add(questionKey));
    setErrors((current) => {
      const { [questionKey]: removed, ...rest } = current;
      return rest;
    });
  };

  const handleSubmit = async () => {
    if (mode !== 'live' || !onSubmit) {
      return;
    }

    const nextErrors: Record<number, string> = {};
    survey.questions.forEach((question, questionIndex) => {
      const questionKey = question.id ?? -(questionIndex + 1);
      if (question.isRequired && touched.has(questionKey) && picked[questionKey] === undefined) {
        nextErrors[questionKey] = 'This question is required';
      }
    });
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    const answers: AnswerInput[] = [];
    survey.questions.forEach((question, questionIndex) => {
      const questionKey = question.id ?? -(questionIndex + 1);
      const index = picked[questionKey];
      if (index === undefined) {
        return;
      }
      if (question.type === 'rating') {
        answers.push({ questionId: questionKey, rating: index + 1 });
      } else {
        answers.push({ questionId: questionKey, choiceId: question.choices[index].id });
      }
    });

    setIsSubmitting(true);
    try {
      await onSubmit(answers);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <h2 className="mb-4 text-xl font-semibold">{survey.name}</h2>
      {survey.questions.map((question, questionIndex) => {
        const questionKey = question.id ?? -(questionIndex + 1);
        const displayed =
          question.direction === 'highest_first'
            ? [...question.choices].reverse()
            : question.choices;
        const pickedIndex = picked[questionKey];

        return (
          <div key={questionIndex} className="mb-6 rounded border border-slate-200 bg-white p-4">
            <div className="mb-3 font-medium">
              {question.text}
              {question.isRequired && <span className="ml-1 text-red-600">*</span>}
            </div>

            {question.type === 'rating' && (
              <div className="flex flex-wrap gap-2">
                {displayed.map((choice, i) => (
                  <Button
                    key={i}
                    type="button"
                    basic={pickedIndex !== i}
                    onClick={() => pick(questionKey, i)}
                  >
                    {choice.label}
                  </Button>
                ))}
              </div>
            )}

            {question.type === 'single_choice' && (
              <div className="flex flex-col gap-2">
                {displayed.map((choice, i) => (
                  <Radio
                    key={i}
                    label={choice.label}
                    name={`question-${questionKey}`}
                    checked={pickedIndex === i}
                    onClick={() => pick(questionKey, i)}
                  />
                ))}
              </div>
            )}

            {errors[questionKey] && (
              <div className="mt-2 text-sm text-red-600">{errors[questionKey]}</div>
            )}
          </div>
        );
      })}

      {Object.keys(errors).length > 0 && (
        <Message negative>Please answer the required questions.</Message>
      )}

      {mode === 'live' && (
        <Button primary type="submit" loading={isSubmitting} disabled={isSubmitting}>
          Submit
        </Button>
      )}
    </Form>
  );
}
