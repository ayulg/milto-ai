import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import AssessmentPage from './pages/AssessmentPage';
import DashboardPage from './pages/DashboardPage';
import CoachPage from './pages/CoachPage';
import CareerLabPage from './pages/CareerLabPage';
import CareerChangePage from './pages/CareerChangePage';
import DevelopmentPage from './pages/DevelopmentPage';
import LimitationPage from './pages/LimitationPage';
import BrutalCoachPage from './pages/BrutalCoachPage';
import ProfilePage from './pages/ProfilePage';
import ReflectionsPage from './pages/ReflectionsPage';

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
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/reflections" element={<ReflectionsPage />} />
            <Route path="/coach" element={<CoachPage />} />
            <Route path="/career-lab" element={<CareerLabPage />} />
            <Route path="/career-change" element={<CareerChangePage />} />
            <Route path="/development" element={<DevelopmentPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
            <Route path="/limitations" element={<LimitationPage />} />
            <Route path="/brutal-coach" element={<BrutalCoachPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
