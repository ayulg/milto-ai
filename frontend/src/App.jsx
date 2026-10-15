import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import AssessmentPage from './pages/AssessmentPage';
import DashboardPage from './pages/DashboardPage';
import CoachPage from './pages/CoachPage';
import CareerLabPage from './pages/CareerLabPage';
import CareerChangePage from './pages/CareerChangePage';
import LoginPage from './pages/LoginPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-[#0b1117] text-[#f3eee8]">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/assessment" element={<AssessmentPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/coach" element={<CoachPage />} />
            <Route path="/career-lab" element={<CareerLabPage />} />
            <Route path="/career-change" element={<CareerChangePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
