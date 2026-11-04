import { api } from './index';
import { AnswerInput } from '../types';

export async function submitResponse(
  surveyId: number,
  answers: AnswerInput[],
): Promise<{ id: number }> {
  const { data } = await api.post<{ id: number }>(`surveys/${surveyId}/responses/`, { answers });
  return data;
}
