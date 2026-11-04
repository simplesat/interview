import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Loader, Message } from 'semantic-ui-react';
import axios from 'axios';
import { getRenderSurvey } from '../../api/surveys';
import { submitResponse } from '../../api/responses';
import SurveyPreview from '../../components/SurveyPreview';
import { AnswerInput, Survey } from '../../types';

export default function SurveyPage() {
  const { id } = useParams();
  const surveyId = Number(id);
  const [survey, setSurvey] = useState<Survey | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    setSurvey(null);
    setLoadError(null);
    getRenderSurvey(surveyId)
      .then(setSurvey)
      .catch(() => setLoadError('This survey could not be loaded.'));
  }, [surveyId]);

  const handleSubmit = async (answers: AnswerInput[]) => {
    setSubmitError(null);
    try {
      await submitResponse(surveyId, answers);
      setIsDone(true);
    } catch (error) {
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : undefined;
      setSubmitError(typeof detail === 'string' ? detail : 'Your response could not be submitted.');
    }
  };

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <Message negative>{loadError}</Message>
      </div>
    );
  }

  if (!survey) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <Loader active inline="centered" />
      </div>
    );
  }

  if (isDone) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <Message positive>
          <Message.Header>Thank you!</Message.Header>
          <p>Your response has been recorded.</p>
        </Message>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      {submitError && <Message negative>{submitError}</Message>}
      <SurveyPreview survey={survey} mode="live" onSubmit={handleSubmit} />
    </div>
  );
}
