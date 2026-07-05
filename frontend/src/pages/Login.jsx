import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../api.js';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await auth.register(username, password);
        setIsRegister(false);
        return;
      }
      const res = await auth.login(username, password);
      localStorage.setItem('token', res.token);
      localStorage.setItem('username', res.username);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-darkcard border border-slate-700 rounded-2xl p-8 w-full max-w-md">
        <h1 className="text-gold text-3xl font-bold text-center mb-2">Abenteuer &amp; Games</h1>
        <p className="text-slate-400 text-center mb-8">D&D Abenteuer mit Computer-Spielführer</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            className="w-full px-4 py-3 rounded-xl bg-darkbg border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-gold"
            placeholder="Benutzername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            className="w-full px-4 py-3 rounded-xl bg-darkbg border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-gold"
            placeholder="Passwort"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-gold text-darkbg font-bold hover:bg-amber-400 transition"
          >
            {isRegister ? 'Registrieren' : 'Einloggen'}
          </button>
        </form>

        <p className="text-center mt-6 text-sm text-slate-400">
          <button
            onClick={() => { setIsRegister(!isRegister); setError(''); }}
            className="hover:text-gold transition"
          >
            {isRegister ? 'Bereits registriert? Einloggen' : 'Neuen Account erstellen'}
          </button>
        </p>
      </div>
    </div>
  );
}
