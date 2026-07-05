import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { characters, adventure } from '../api.js';

const CLASS_ICONS = { krieger: '⚔️', magier: '🔮', schurke: '🗡️', kleriker: '✨' };
const CLASS_COLORS = { krieger: 'text-dragonred', magier: 'text-magicblue', schurke: 'text-roguepurple', kleriker: 'text-naturegreen' };

export default function Dashboard() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = localStorage.getItem('username');
  const navigate = useNavigate();

  useEffect(() => {
    characters.list(user)
      .then(setList)
      .catch(() => setList([]))
      .finally(() => setLoading(false));
  }, [user]);

  const startAdventure = async (char) => {
    try {
      const res = await adventure.start(user, char.id);
      navigate(`/adventure/${res.session_id}`, { state: { initial: res } });
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Meine Helden</h2>
        <div className="flex gap-2">
          <Link to="/multiplayer" className="px-4 py-2 bg-roguepurple/80 text-white rounded-xl font-bold hover:bg-roguepurple transition text-sm">
            👥 Gemeinsames Abenteuer
          </Link>
          <Link to="/create" className="px-4 py-2 bg-gold text-darkbg rounded-xl font-bold hover:bg-amber-400 transition text-sm">
            + Neuer Held
          </Link>
        </div>
      </div>

      {loading && <p className="text-slate-400">Lade Helden...</p>}

      {!loading && list.length === 0 && (
        <div className="text-center py-16">
          <p className="text-slate-400 text-lg mb-4">Noch keine Helden erstellt.</p>
          <Link to="/create" className="px-6 py-3 bg-gold text-darkbg rounded-xl font-bold">
            Erstelle deinen ersten Helden
          </Link>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {list.map((c) => (
          <div key={c.id} className="bg-darkcard border border-slate-700 rounded-2xl p-5 hover:border-gold/50 transition">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className={`text-xl font-bold ${CLASS_COLORS[c.char_class] || 'text-white'}`}>
                  {CLASS_ICONS[c.char_class] || '⚔'} {c.name}
                </h3>
                <p className="text-sm text-slate-400 capitalize">
                  {c.char_class} · Stufe {c.level} · {c.race}
                </p>
              </div>
              <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                {c.hp_current}/{c.hp_max} HP
              </span>
            </div>
            <div className="flex gap-2 text-xs text-slate-400 mb-4">
              <span>RK {c.ac}</span>
              <span>ANG +{c.attack_bonus}</span>
              <span>SCHD +{c.damage_bonus}</span>
            </div>
            <button
              onClick={() => startAdventure(c)}
              className="w-full py-2 rounded-xl bg-gold/20 text-gold border border-gold/30 font-bold hover:bg-gold/30 transition"
            >
              Allein spielen
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
