import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import {
  Button,
  Checkbox,
  Dropdown,
  Form,
  Icon,
  Label,
  Loader,
  Message,
  Segment,
} from 'semantic-ui-react';
import { getBuilderSurvey, saveSurvey } from '../../api/surveys';
import SurveyPreview from '../../components/SurveyPreview';
import { Choice, DEFAULT_LABELS, Direction, Question, QuestionType, Survey } from '../../types';

const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
  rating: 'Rating',
  single_choice: 'Single choice',
};

const NEW_QUESTION_TEXT: Record<QuestionType, string> = {
  rating: 'How would you rate us?',
  single_choice: 'Pick one option',
};

const ADD_QUESTION_BUTTONS: { type: QuestionType; text: string }[] = [
  { type: 'rating', text: 'Add rating question' },
  { type: 'single_choice', text: 'Add single-choice question' },
];

const SCALE_SIZE_OPTIONS = [2, 3, 4, 5].map((size) => ({
  key: size,
  value: size,
  text: `${size} points`,
}));

const DIRECTION_OPTIONS: { value: Direction; text: string }[] = [
  { value: 'lowest_first', text: 'Lowest first' },
  { value: 'highest_first', text: 'Highest first' },
];

function getErrorMessage(error: unknown): string {
  const detail = axios.isAxiosError(error) ? error.response?.data?.detail : undefined;
  return typeof detail === 'string' ? detail : 'Something went wrong. Please try again.';
}

function renumber<T extends { order: number }>(items: T[]): T[] {
  return items.map((item, index) => ({ ...item, order: index }));
}

function moveItem<T>(items: T[], from: number, to: number): T[] {
  const next = [...items];
  [next[from], next[to]] = [next[to], next[from]];
  return next;
}

function ratingChoices(size: number, previous: Choice[] = []): Choice[] {
  return DEFAULT_LABELS[size].map((label, index) => ({
    id: previous[index]?.id,
    order: index,
    value: index + 1,
    label,
    answerCount: previous[index]?.answerCount,
  }));
}

function newQuestion(type: QuestionType, order: number): Question {
  if (type === 'rating') {
    return {
      order,
      type,
      text: NEW_QUESTION_TEXT[type],
      isRequired: false,
      scaleSize: 5,
      direction: 'lowest_first',
      choices: ratingChoices(5),
    };
  }
  return {
    order,
    type,
    text: NEW_QUESTION_TEXT[type],
    isRequired: false,
    scaleSize: null,
    direction: null,
    choices: [
      { order: 0, value: null, label: 'Option 1' },
      { order: 1, value: null, label: 'Option 2' },
    ],
  };
}

function totalAnswers(question: Question): number {
  return question.choices.reduce((sum, choice) => sum + (choice.answerCount ?? 0), 0);
}

function findProblem(name: string, questions: Question[]): string | null {
  if (name.trim() === '') {
    return 'The survey needs a name.';
  }
  if (questions.length === 0) {
    return 'Add at least one question before saving.';
  }
  for (let i = 0; i < questions.length; i += 1) {
    const question = questions[i];
    if (question.text.trim() === '') {
      return `Question ${i + 1} needs some text.`;
    }
    if (question.choices.some((choice) => choice.label.trim() === '')) {
      const what = question.type === 'rating' ? 'point' : 'option';
      return `Every ${what} of question ${i + 1} needs a label.`;
    }
  }
  return null;
}

function buildSaveBody(surveyId: number, name: string, questions: Question[]): Survey {
  return {
    id: surveyId,
    name: name.trim(),
    questions: questions.map((question, questionIndex) => ({
      id: question.id,
      order: questionIndex,
      type: question.type,
      text: question.text.trim(),
      isRequired: question.isRequired,
      scaleSize: question.scaleSize,
      direction: question.direction,
      choices: question.choices.map((choice, choiceIndex) => ({
        id: choice.id,
        order: choiceIndex,
        value: choice.value,
        label: choice.label.trim(),
      })),
    })),
  };
}

export default function SurveyBuilderPage() {
  const { id } = useParams();
  const surveyId = Number(id);

  const [name, setName] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [newQuestionType, setNewQuestionType] = useState<QuestionType>('rating');
  const [confirmDeleteIndex, setConfirmDeleteIndex] = useState<number | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);

  const applySurvey = (survey: Survey) => {
    setName(survey.name);
    setQuestions(survey.questions);
    setIsDirty(false);
    setSaveError(null);
    setConfirmDeleteIndex(null);
    setSelectedIndex((current) => {
      if (survey.questions.length === 0) {
        return null;
      }
      if (current === null || current >= survey.questions.length) {
        return 0;
      }
      return current;
    });
  };

  useEffect(() => {
    setIsLoading(true);
    setLoadError(null);
    getBuilderSurvey(surveyId)
      .then((survey) => {
        applySurvey(survey);
        setIsLoading(false);
      })
      .catch(() => {
        setLoadError('Could not load the survey.');
        setIsLoading(false);
      });
  }, [surveyId]);

  useEffect(() => {
    if (!isDirty) {
      return undefined;
    }
    const warnBeforeLeaving = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnBeforeLeaving);
    return () => window.removeEventListener('beforeunload', warnBeforeLeaving);
  }, [isDirty]);

  const markDirty = () => {
    setIsDirty(true);
    setSaveError(null);
  };

  const updateQuestionAt = (index: number, patch: Partial<Question>) => {
    setQuestions((current) =>
      current.map((question, i) => (i === index ? { ...question, ...patch } : question)),
    );
    markDirty();
  };

  const updateChoice = (questionIndex: number, choiceIndex: number, patch: Partial<Choice>) => {
    const question = questions[questionIndex];
    updateQuestionAt(questionIndex, {
      choices: question.choices.map((choice, i) =>
        i === choiceIndex ? { ...choice, ...patch } : choice,
      ),
    });
  };

  const addChoice = (questionIndex: number) => {
    const question = questions[questionIndex];
    const position = question.choices.length;
    updateQuestionAt(questionIndex, {
      choices: [
        ...question.choices,
        { order: position, value: null, label: `Option ${position + 1}` },
      ],
    });
  };

  const removeChoice = (questionIndex: number, choiceIndex: number) => {
    const question = questions[questionIndex];
    updateQuestionAt(questionIndex, {
      choices: renumber(question.choices.filter((_, i) => i !== choiceIndex)),
    });
  };

  const moveChoice = (questionIndex: number, choiceIndex: number, delta: number) => {
    const question = questions[questionIndex];
    const target = choiceIndex + delta;
    if (target < 0 || target >= question.choices.length) {
      return;
    }
    updateQuestionAt(questionIndex, {
      choices: renumber(moveItem(question.choices, choiceIndex, target)),
    });
  };

  const changeScaleSize = (questionIndex: number, size: number) => {
    const question = questions[questionIndex];
    if (question.scaleSize === size) {
      return;
    }
    updateQuestionAt(questionIndex, {
      scaleSize: size,
      choices: ratingChoices(size, question.choices),
    });
  };

  const selectQuestion = (index: number) => {
    setSelectedIndex(index);
    setConfirmDeleteIndex(null);
  };

  const addQuestion = (type: QuestionType) => {
    setNewQuestionType(type);
    setQuestions((current) => [...current, newQuestion(type, current.length)]);
    setSelectedIndex(questions.length);
    setConfirmDeleteIndex(null);
    markDirty();
  };

  const moveQuestion = (index: number, delta: number) => {
    const target = index + delta;
    if (target < 0 || target >= questions.length) {
      return;
    }
    setQuestions(renumber(moveItem(questions, index, target)));
    if (selectedIndex === index) {
      setSelectedIndex(target);
    } else if (selectedIndex === target) {
      setSelectedIndex(index);
    }
    setConfirmDeleteIndex(null);
    markDirty();
  };

  const removeQuestion = (index: number) => {
    const remaining = renumber(questions.filter((_, i) => i !== index));
    setQuestions(remaining);
    setSelectedIndex((current) => {
      if (remaining.length === 0) {
        return null;
      }
      if (current === null) {
        return 0;
      }
      if (current > index) {
        return current - 1;
      }
      return Math.min(current, remaining.length - 1);
    });
    setConfirmDeleteIndex(null);
    markDirty();
  };

  const discardChanges = async () => {
    if (!window.confirm('Discard all unsaved changes?')) {
      return;
    }
    setIsSaving(true);
    try {
      applySurvey(await getBuilderSurvey(surveyId));
    } catch (error) {
      setSaveError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleSave = async () => {
    const problem = findProblem(name, questions);
    if (problem) {
      setSaveError(problem);
      return;
    }
    setIsSaving(true);
    setSaveError(null);
    try {
      const saved = await saveSurvey(surveyId, buildSaveBody(surveyId, name, questions));
      applySurvey(saved);
      setLastSavedAt(new Date());
    } catch (error) {
      setSaveError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const renderRatingEditor = (question: Question, questionIndex: number) => (
    <div className="mb-6">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h4 className="m-0 font-semibold">Rating scale</h4>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Points</span>
          <Dropdown
            selection
            compact
            options={SCALE_SIZE_OPTIONS}
            value={question.scaleSize ?? 5}
            onChange={(_, data) => changeScaleSize(questionIndex, Number(data.value))}
          />
        </div>
      </div>
      <div className="mb-3 flex items-center gap-3">
        <span className="text-sm text-slate-500">Show</span>
        <Button.Group size="small">
          {DIRECTION_OPTIONS.map((option) => (
            <Button
              key={option.value}
              type="button"
              active={question.direction === option.value}
              onClick={() => updateQuestionAt(questionIndex, { direction: option.value })}
            >
              {option.text}
            </Button>
          ))}
        </Button.Group>
      </div>
      <p className="mb-3 text-sm text-slate-500">
        Points are listed from the lowest to the highest rating. Changing the number of points
        resets the labels.
      </p>
      <div className="flex flex-col gap-2">
        {question.choices.map((choice, choiceIndex) => (
          <div key={choiceIndex} className="flex items-center gap-2">
            <span className="w-6 text-right text-slate-500">{choiceIndex + 1}</span>
            <Form.Input
              fluid
              className="flex-1 !mb-0"
              value={choice.label}
              maxLength={100}
              error={choice.label.trim() === ''}
              placeholder="Label"
              onChange={(_, data) =>
                updateChoice(questionIndex, choiceIndex, { label: data.value })
              }
            />
            <Label circular title="Answers so far">
              {choice.answerCount ?? 0}
            </Label>
          </div>
        ))}
      </div>
    </div>
  );

  const renderOptionEditor = (question: Question, questionIndex: number) => (
    <div className="mb-6">
      <h4 className="mb-2 font-semibold">Options</h4>
      <div className="flex flex-col gap-2">
        {question.choices.map((choice, choiceIndex) => (
          <div key={choiceIndex} className="flex items-center gap-2">
            <span className="w-6 text-right text-slate-500">{choiceIndex + 1}</span>
            <Form.Input
              fluid
              className="flex-1 !mb-0"
              value={choice.label}
              maxLength={100}
              error={choice.label.trim() === ''}
              placeholder="Label"
              onChange={(_, data) =>
                updateChoice(questionIndex, choiceIndex, { label: data.value })
              }
            />
            <Label circular title="Answers so far">
              {choice.answerCount ?? 0}
            </Label>
            <div className="flex items-center gap-1">
              <Button
                type="button"
                icon="arrow up"
                size="mini"
                basic
                title="Move option up"
                disabled={choiceIndex === 0}
                onClick={() => moveChoice(questionIndex, choiceIndex, -1)}
              />
              <Button
                type="button"
                icon="arrow down"
                size="mini"
                basic
                title="Move option down"
                disabled={choiceIndex === question.choices.length - 1}
                onClick={() => moveChoice(questionIndex, choiceIndex, 1)}
              />
              <Button
                type="button"
                icon="trash"
                size="mini"
                basic
                negative
                title="Delete option"
                disabled={question.choices.length <= 1}
                onClick={() => removeChoice(questionIndex, choiceIndex)}
              />
            </div>
          </div>
        ))}
      </div>
      <Button
        type="button"
        basic
        size="small"
        className="mt-3"
        icon="plus"
        content="Add option"
        onClick={() => addChoice(questionIndex)}
      />
    </div>
  );

  const renderQuestionEditor = (question: Question, questionIndex: number) => (
    <div className="mt-4 border-t border-slate-200 pt-4">
      <div className="mb-4 text-sm text-slate-500">
        {QUESTION_TYPE_LABELS[question.type]} question
        {question.type === 'single_choice' && ' where respondents pick one option'}
        {question.type === 'rating' && ' where respondents pick a point on the scale'}
      </div>
      <Form>
        <Form.Input
          label="Question text"
          value={question.text}
          maxLength={300}
          error={
            question.text.trim() === ''
              ? { content: 'The question needs some text', pointing: 'above' }
              : false
          }
          onChange={(_, data) => updateQuestionAt(questionIndex, { text: data.value })}
        />
        <Form.Field>
          <Checkbox
            label="Required"
            checked={question.isRequired}
            onChange={(_, data) =>
              updateQuestionAt(questionIndex, { isRequired: data.checked === true })
            }
          />
        </Form.Field>

        <div className="mt-6">
          {question.type === 'rating' && renderRatingEditor(question, questionIndex)}
          {question.type === 'single_choice' && renderOptionEditor(question, questionIndex)}
        </div>
      </Form>
    </div>
  );

  const renderQuestionCard = (question: Question, index: number) => {
    const isSelected = selectedIndex === index;
    return (
      <Segment key={index} color={isSelected ? 'blue' : undefined} className="!mb-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="flex flex-1 items-center gap-3 border-0 bg-transparent p-0 text-left"
            onClick={() => selectQuestion(index)}
          >
            <span className="w-6 text-slate-500">{index + 1}.</span>
            <Label size="small">{QUESTION_TYPE_LABELS[question.type]}</Label>
            <span className="flex-1 font-medium">
              {question.text}
              {question.isRequired && (
                <span className="ml-1 text-red-600" title="Required">
                  *
                </span>
              )}
            </span>
            <span className="text-sm text-slate-500">
              {question.choices.length} {question.type === 'rating' ? 'points' : 'options'}
              {' · '}
              {totalAnswers(question)} answers
            </span>
          </button>
          <div className="flex items-center gap-1">
            <Button
              type="button"
              icon="arrow up"
              size="mini"
              basic
              title="Move question up"
              disabled={index === 0}
              onClick={() => moveQuestion(index, -1)}
            />
            <Button
              type="button"
              icon="arrow down"
              size="mini"
              basic
              title="Move question down"
              disabled={index === questions.length - 1}
              onClick={() => moveQuestion(index, 1)}
            />
            <Button
              type="button"
              icon="trash"
              size="mini"
              basic
              negative
              title="Delete question"
              onClick={() => setConfirmDeleteIndex(index)}
            />
          </div>
        </div>
        {!isSelected && (
          <div className="mt-2 pl-9 text-sm text-slate-500">
            {question.choices.map((choice) => choice.label).join(' · ')}
            {question.direction === 'highest_first' && ' (highest first)'}
          </div>
        )}
        {confirmDeleteIndex === index && (
          <Message warning className="!mb-0 !mt-3">
            <div className="flex items-center justify-between gap-3">
              <span>Delete question {index + 1} from this survey?</span>
              <div className="flex items-center gap-2">
                <Button type="button" size="small" negative onClick={() => removeQuestion(index)}>
                  Delete
                </Button>
                <Button type="button" size="small" onClick={() => setConfirmDeleteIndex(null)}>
                  Cancel
                </Button>
              </div>
            </div>
          </Message>
        )}
        {isSelected && renderQuestionEditor(question, index)}
      </Segment>
    );
  };

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <Message negative>{loadError}</Message>
        <Link to="/">Back to surveys</Link>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <Loader active inline="centered" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-slate-500">
            <Icon name="arrow left" />
            Surveys
          </Link>
          <h1 className="m-0 text-xl font-semibold">
            {name.trim() === '' ? 'Untitled survey' : name}
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-500">
            {questions.length} {questions.length === 1 ? 'question' : 'questions'}
          </span>
          {isSaving && <span className="text-sm text-slate-500">Working...</span>}
          {isDirty && <span className="text-sm text-amber-700">Unsaved changes</span>}
          {isDirty && (
            <Button type="button" basic size="small" disabled={isSaving} onClick={discardChanges}>
              Discard changes
            </Button>
          )}
          {!isDirty && lastSavedAt && (
            <span className="text-sm text-slate-500">
              Saved at {lastSavedAt.toLocaleTimeString()}
            </span>
          )}
          <Link to={`/s/${surveyId}`}>Respondent page</Link>
          <Button
            primary
            type="button"
            loading={isSaving}
            disabled={isSaving || questions.length === 0}
            onClick={handleSave}
          >
            Save survey
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-6 p-6">
        <section>
          <h2 className="mb-4 text-lg font-semibold">Builder</h2>
          {saveError && <Message negative>{saveError}</Message>}
          <Form className="mb-6">
            <Form.Input
              label="Survey name"
              value={name}
              maxLength={200}
              error={name.trim() === ''}
              onChange={(_, data) => {
                setName(data.value);
                markDirty();
              }}
            />
          </Form>
          {questions.map((question, index) => renderQuestionCard(question, index))}
          {questions.length === 0 && (
            <p className="mb-4 text-slate-500">
              This survey has no questions yet. Add one to be able to save it.
            </p>
          )}
          <Segment secondary>
            <div className="mb-3 font-semibold">Add a question</div>
            <div className="flex flex-wrap gap-2">
              {ADD_QUESTION_BUTTONS.map((button) => (
                <Button
                  key={button.type}
                  type="button"
                  basic={newQuestionType !== button.type}
                  size="small"
                  icon="plus"
                  content={button.text}
                  onClick={() => addQuestion(button.type)}
                />
              ))}
            </div>
          </Segment>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">Preview</h2>
          <p className="mb-4 text-sm text-slate-500">
            This is how respondents see the survey. Answers given here are not saved.
          </p>
          <div className="rounded border border-slate-200 bg-slate-50 p-4">
            {questions.length === 0 && (
              <p className="text-slate-500">Add a question to see it in the preview.</p>
            )}
            <SurveyPreview
              key={surveyId}
              survey={{ id: surveyId, name, questions }}
              mode="preview"
            />
          </div>
        </section>
      </div>
    </div>
  );
}
