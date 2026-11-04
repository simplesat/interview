export type QuestionType = 'rating' | 'single_choice';

export type Direction = 'lowest_first' | 'highest_first';

export interface Choice {
  id?: number;
  order: number;
  value: number | null;
  label: string;
  answerCount?: number;
}

export interface Question {
  id?: number;
  order: number;
  type: QuestionType;
  text: string;
  isRequired: boolean;
  scaleSize: number | null;
  direction: Direction | null;
  choices: Choice[];
}

export interface Survey {
  id: number;
  name: string;
  questions: Question[];
}

export interface SurveyListItem {
  id: number;
  name: string;
  questionCount: number;
  responseCount: number;
}

export interface RatingAnswer {
  questionId: number;
  rating?: number;
}

export interface ChoiceAnswer {
  questionId: number;
  choiceId?: number;
}

export type AnswerInput = RatingAnswer | ChoiceAnswer;

export const DEFAULT_LABELS: Record<number, string[]> = {
  2: ['Bad', 'Good'],
  3: ['Bad', 'Okay', 'Good'],
  4: ['Bad', 'Poor', 'Good', 'Great'],
  5: ['Terrible', 'Bad', 'Okay', 'Good', 'Great'],
};
