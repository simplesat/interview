import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Form, Loader, Message, Segment, Table } from 'semantic-ui-react';
import { createSurvey, listSurveys } from '../../api/surveys';
import { SurveyListItem } from '../../types';

export default function SurveyListPage() {
  const navigate = useNavigate();
  const [surveys, setSurveys] = useState<SurveyListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    listSurveys()
      .then(setSurveys)
      .catch(() => setError('Could not load surveys.'));
  }, []);

  const handleCreate = async () => {
    if (newName.trim() === '') {
      setCreateError('Give the survey a name.');
      return;
    }
    setIsSaving(true);
    setCreateError(null);
    try {
      const survey = await createSurvey(newName.trim());
      navigate(`/surveys/${survey.id}/builder`);
    } catch {
      setCreateError('Could not create the survey.');
      setIsSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="m-0 text-2xl font-semibold">Surveys</h1>
        {!isCreating && (
          <Button primary icon="plus" content="New survey" onClick={() => setIsCreating(true)} />
        )}
      </div>

      {isCreating && (
        <Segment>
          <Form onSubmit={handleCreate}>
            <Form.Input
              autoFocus
              label="Survey name"
              placeholder="Customer satisfaction"
              maxLength={200}
              value={newName}
              error={createError ? { content: createError, pointing: 'above' } : false}
              onChange={(_, data) => {
                setNewName(data.value);
                setCreateError(null);
              }}
            />
            <Button primary type="submit" loading={isSaving} disabled={isSaving}>
              Create survey
            </Button>
            <Button
              type="button"
              disabled={isSaving}
              onClick={() => {
                setIsCreating(false);
                setNewName('');
                setCreateError(null);
              }}
            >
              Cancel
            </Button>
          </Form>
        </Segment>
      )}

      {error && <Message negative>{error}</Message>}
      {!surveys && !error && <Loader active inline="centered" />}
      {surveys && (
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell collapsing textAlign="right">
                Questions
              </Table.HeaderCell>
              <Table.HeaderCell collapsing textAlign="right">
                Responses
              </Table.HeaderCell>
              <Table.HeaderCell collapsing />
              <Table.HeaderCell collapsing />
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {surveys.map((survey) => (
              <Table.Row key={survey.id}>
                <Table.Cell>{survey.name}</Table.Cell>
                <Table.Cell textAlign="right">{survey.questionCount}</Table.Cell>
                <Table.Cell textAlign="right">{survey.responseCount}</Table.Cell>
                <Table.Cell>
                  <Link to={`/surveys/${survey.id}/builder`}>Builder</Link>
                </Table.Cell>
                <Table.Cell>
                  <Link to={`/s/${survey.id}`}>Respondent page</Link>
                </Table.Cell>
              </Table.Row>
            ))}
            {surveys.length === 0 && (
              <Table.Row>
                <Table.Cell colSpan={5}>No surveys yet.</Table.Cell>
              </Table.Row>
            )}
          </Table.Body>
        </Table>
      )}
    </div>
  );
}
