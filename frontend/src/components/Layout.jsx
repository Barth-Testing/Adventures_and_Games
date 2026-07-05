import { Outlet, Link, useNavigate } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();
  const user = localStorage.getItem('username');

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-darkcard border-b border-slate-700 px-6 py-3 flex items-center justify-between">
        <Link to="/" className="text-gold text-xl font-bold tracking-wider">
          ⚔ Abenteuer &amp; Games
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-400">{user}</span>
          <button onClick={logout} className="text-slate-400 hover:text-red-400 transition">
            Abmelden
          </button>
        </div>
      </header>
      <main className="flex-1 p-4 md:p-6 max-w-5xl mx-auto w-full">
        <Outlet />
      </main>
    </div>
  );
}
