import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import CharacterCreate from './pages/CharacterCreate.jsx';
import Adventure from './pages/Adventure.jsx';
import Layout from './components/Layout.jsx';

function RequireAuth({ children }) {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('username');
  if (!token || !user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/create" element={<CharacterCreate />} />
        <Route path="/adventure/:characterId" element={<Adventure />} />
      </Route>
    </Routes>
  );
}
