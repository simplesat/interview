import { Route, Routes } from 'react-router-dom';
import SurveyListPage from './pages/SurveyListPage';
import SurveyBuilderPage from './pages/SurveyBuilderPage';
import SurveyPage from './pages/SurveyPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<SurveyListPage />} />
      <Route path="/surveys/:id/builder" element={<SurveyBuilderPage />} />
      <Route path="/s/:id" element={<SurveyPage />} />
    </Routes>
  );
}
