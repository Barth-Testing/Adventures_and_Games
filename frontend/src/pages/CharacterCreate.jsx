import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { characters } from '../api.js';

const CLASSES = [
  { id: 'krieger', label: 'Krieger', desc: 'Starker Nahkämpfer, hohe Verteidigung', color: 'text-dragonred', icon: '⚔️' },
  { id: 'magier', label: 'Magier', desc: 'Mächtige Zauber, aber schwache Verteidigung', color: 'text-magicblue', icon: '🔮' },
  { id: 'schurke', label: 'Schurke', desc: 'Schnell und wendig, präzise Angriffe', color: 'text-roguepurple', icon: '🗡️' },
  { id: 'kleriker', label: 'Kleriker', desc: 'Heilung und Unterstützung', color: 'text-naturegreen', icon: '✨' },
];

export default function CharacterCreate() {
  const [name, setName] = useState('');
  const [charClass, setCharClass] = useState('krieger');
  const [race, setRace] = useState('Mensch');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const user = localStorage.getItem('username');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Bitte Namen eingeben'); return; }
    try {
      await characters.create(user, name.trim(), charClass, race);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Neuen Helden erschaffen</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm text-slate-400 mb-2">Name</label>
          <input
            className="w-full px-4 py-3 rounded-xl bg-darkcard border border-slate-600 text-white focus:outline-none focus:border-gold"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name deines Helden"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-2">Volk</label>
          <select
            className="w-full px-4 py-3 rounded-xl bg-darkcard border border-slate-600 text-white focus:outline-none focus:border-gold"
            value={race}
            onChange={(e) => setRace(e.target.value)}
          >
            <option>Mensch</option>
            <option>Elf</option>
            <option>Zwerg</option>
            <option>Halbling</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-3">Klasse</label>
          <div className="grid grid-cols-2 gap-3">
            {CLASSES.map((c) => (
              <button
                type="button"
                key={c.id}
                onClick={() => setCharClass(c.id)}
                className={`p-4 rounded-2xl border text-left transition ${
                  charClass === c.id
                    ? 'border-gold bg-gold/10'
                    : 'border-slate-700 bg-darkcard hover:border-slate-500'
                }`}
              >
                <div className={`text-2xl mb-1 ${c.color}`}>{c.icon}</div>
                <div className={`font-bold ${c.color}`}>{c.label}</div>
                <div className="text-xs text-slate-400 mt-1">{c.desc}</div>
              </button>
            ))}
          </div>
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <div className="flex gap-3">
          <button
            type="submit"
            className="flex-1 py-3 rounded-xl bg-gold text-darkbg font-bold hover:bg-amber-400 transition"
          >
            Helden erschaffen
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-3 rounded-xl border border-slate-600 text-slate-300 hover:border-slate-400 transition"
          >
            Abbrechen
          </button>
        </div>
      </form>
    </div>
  );
}
