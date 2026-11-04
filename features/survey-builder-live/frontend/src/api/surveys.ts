import { api } from './index';
import { Survey, SurveyListItem } from '../types';

export async function listSurveys(): Promise<SurveyListItem[]> {
  const { data } = await api.get<SurveyListItem[]>('surveys/');
  return data;
}

export async function createSurvey(name: string): Promise<{ id: number; name: string }> {
  const { data } = await api.post<{ id: number; name: string }>('surveys/', { name });
  return data;
}

export async function getBuilderSurvey(surveyId: number): Promise<Survey> {
  const { data } = await api.get<Survey>(`surveys/${surveyId}/builder/`);
  return data;
}

export async function saveSurvey(surveyId: number, survey: Survey): Promise<Survey> {
  const { data } = await api.put<Survey>(`surveys/${surveyId}/`, survey);
  return data;
}

export async function getRenderSurvey(surveyId: number): Promise<Survey> {
  const { data } = await api.get<Survey>(`surveys/${surveyId}/render/`);
  return data;
}
