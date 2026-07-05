import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { characters as api, adventure } from '../api.js';

const CLASS_ICONS = { krieger: '⚔️', magier: '🔮', schurke: '🗡️', kleriker: '✨' };
const CLASS_COLORS = { krieger: 'text-dragonred', magier: 'text-magicblue', schurke: 'text-roguepurple', kleriker: 'text-naturegreen' };

export default function MultiplayerLobby() {
  const [allChars, setAllChars] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.all()
      .then(setAllChars)
      .catch(() => setAllChars([]))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const start = async () => {
    if (selected.length === 0) return;
    setStarting(true);
    try {
      const res = await adventure.startMulti(selected);
      navigate(`/adventure/${res.session_id}`);
    } catch (e) {
      alert(e.message);
      setStarting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2">👥 Gemeinsames Abenteuer</h2>
      <p className="text-slate-400 mb-6">
        Wählt aus, welche Helden gemeinsam aufbrechen. Jeder spielt seinen eigenen Helden am selben Bildschirm.
      </p>

      {loading && <p className="text-slate-400">Lade Helden...</p>}

      {!loading && allChars.length === 0 && (
        <div className="text-center py-16">
          <p className="text-slate-400">Es gibt noch keine Helden. Erstellt zuerst welche!</p>
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 mb-6">
        {allChars.map((c) => {
          const isSelected = selected.includes(c.id);
          return (
            <button
              key={c.id}
              onClick={() => toggle(c.id)}
              className={`p-4 rounded-2xl border text-left transition ${
                isSelected
                  ? 'border-roguepurple bg-roguepurple/10 ring-2 ring-roguepurple/50'
                  : 'border-slate-700 bg-darkcard hover:border-slate-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className={`text-xl ${CLASS_COLORS[c.char_class]}`}>
                    {CLASS_ICONS[c.char_class]} {c.name}
                  </span>
                  <p className="text-xs text-slate-400 mt-1 capitalize">
                    {c.char_class} · Stufe {c.level}
                  </p>
                </div>
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  isSelected ? 'border-roguepurple bg-roguepurple' : 'border-slate-500'
                }`}>
                  {isSelected && <span className="text-white text-xs">✓</span>}
                </div>
              </div>
              <div className="flex gap-3 mt-2 text-xs text-slate-400">
                <span>RK {c.ac}</span>
                <span>HP {c.hp_current}/{c.hp_max}</span>
                <span>ANG +{c.attack_bonus}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex gap-3 items-center">
        <button
          onClick={start}
          disabled={selected.length === 0 || starting}
          className="px-6 py-3 rounded-xl bg-roguepurple text-white font-bold hover:bg-roguepurple/80 transition text-lg disabled:opacity-50"
        >
          {starting ? 'Starte...' : `Abenteuer starten (${selected.length} Helden)`}
        </button>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-3 rounded-xl border border-slate-600 text-slate-300 hover:border-slate-400 transition"
        >
          Zurück
        </button>
      </div>
    </div>
  );
}
