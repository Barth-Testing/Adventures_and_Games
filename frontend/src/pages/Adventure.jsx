import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adventure } from '../api.js';

export default function Adventure() {
  const { characterId } = useParams();
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(null);
  const [state, setState] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const logRef = useRef(null);
  const user = localStorage.getItem('username');

  useEffect(() => {
    setLoading(true);
    adventure.start(user, Number(characterId))
      .then((res) => {
        setSessionId(res.session_id);
        setState(res);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [user, characterId]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [state?.narrative]);

  const sendAction = useCallback(async (text) => {
    if (!sessionId || !text.trim()) return;
    setLoading(true);
    setError('');
    setInput('');
    try {
      const res = await adventure.action(sessionId, text.trim());
      setState((prev) => ({
        ...res,
        narrative_history: [...(prev?.narrative_history || []), prev?.narrative],
        options: res.options || []
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendAction(input);
  };

  const handleOption = (opt) => sendAction(opt);

  if (loading && !state) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gold text-xl animate-pulse">Das Abenteuer beginnt...</p>
      </div>
    );
  }

  if (error && !state) {
    return (
      <div className="text-center py-16">
        <p className="text-red-400 mb-4">{error}</p>
        <button onClick={() => navigate('/')} className="text-gold underline">
          Zurück zum Dashboard
        </button>
      </div>
    );
  }

  if (!state) return null;

  const isCombat = state.combat_active || state.combat_start;
  const isComplete = state.adventure_complete;

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold text-gold">Der Schatten-Schatz der vergessenen Zitadelle</h2>
        <button
          onClick={() => navigate('/')}
          className="text-xs px-3 py-1 rounded border border-slate-600 text-slate-400 hover:text-white transition"
        >
          ✕ Schließen
        </button>
      </div>

      {error && (
        <div className="mb-3 p-3 rounded-xl bg-red-900/30 border border-red-700 text-red-300 text-sm">
          {error}
        </div>
      )}

      <div
        ref={logRef}
        className="flex-1 overflow-y-auto bg-darkcard border border-slate-700 rounded-2xl p-5 mb-4 space-y-3"
      >
        {state.narrative_history?.map((n, i) => (
          <p key={i} className="text-slate-400 text-sm leading-relaxed">{n}</p>
        ))}
        <div className={`text-base leading-relaxed whitespace-pre-line ${isCombat ? 'text-red-300' : 'text-white'}`}>
          {state.narrative}
        </div>
        {state.roll && (
          <div className="inline-block px-3 py-1 rounded bg-slate-700 text-amber-400 text-sm font-mono">
            W20: {state.roll} {state.success ? '✓ Erfolg' : '✗ Fehlschlag'}
          </div>
        )}
        {state.puzzle_active && state.puzzle && (
          <div className="p-3 rounded-xl bg-amber-900/20 border border-amber-700/50 text-amber-300 text-sm">
            <span className="font-bold">🧩 Rätsel:</span> {state.puzzle.question || state.puzzle.description}
          </div>
        )}
      </div>

      {isComplete ? (
        <div className="text-center py-4">
          <p className="text-naturegreen text-xl font-bold mb-3">🎉 Abenteuer abgeschlossen!</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gold text-darkbg rounded-xl font-bold"
          >
            Zum Dashboard
          </button>
        </div>
      ) : isCombat && state.combat_state ? (
        <CombatUI state={state} input={input} setInput={setInput} handleSubmit={handleSubmit} handleOption={handleOption} loading={loading} />
      ) : (
        <ExplorationUI input={input} setInput={setInput} handleSubmit={handleSubmit} handleOption={handleOption} options={state.options} loading={loading} />
      )}
    </div>
  );
}

function ExplorationUI({ input, setInput, handleSubmit, handleOption, options, loading }) {
  return (
    <div className="space-y-3">
      {options && options.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => handleOption(opt)}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-darkcard border border-slate-600 text-slate-200 hover:border-gold hover:text-gold transition text-sm disabled:opacity-50"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 px-4 py-3 rounded-xl bg-darkcard border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-gold"
          placeholder="Was tust du? (Freitext)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 rounded-xl bg-gold text-darkbg font-bold hover:bg-amber-400 transition disabled:opacity-50"
        >
          {loading ? '...' : 'Senden'}
        </button>
      </form>
    </div>
  );
}

function CombatUI({ state, input, setInput, handleSubmit, handleOption, loading }) {
  const cs = state.combat_state;
  const player = cs?.combatants?.find((c) => c.is_player);
  const enemies = cs?.combatants?.filter((c) => !c.is_player) || cs?.all_combatants?.filter((c) => !c.is_player) || [];
  const currentTurn = cs?.current_turn;

  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        {player && (
          <div className="flex-1 p-3 rounded-xl bg-darkcard border border-naturegreen/50">
            <div className="text-xs text-slate-400">Spieler</div>
            <div className="font-bold text-naturegreen">{player.name}</div>
            <div className="text-sm">
              <span className="text-red-400">{player.hp}</span>
              <span className="text-slate-500">/{player.hp_max} HP</span>
              <span className="ml-2 text-slate-400">RK {player.ac}</span>
            </div>
          </div>
        )}
        {enemies.length > 0 && enemies.map((e) => (
          <div key={e.name} className={`flex-1 p-3 rounded-xl border ${e.hp <= 0 ? 'border-slate-700 opacity-50' : 'border-dragonred/50'}`}>
            <div className="text-xs text-slate-400">Gegner</div>
            <div className="font-bold text-dragonred">{e.name}</div>
            <div className="text-sm">
              <span className="text-red-400">{e.hp}</span>
              <span className="text-slate-500">/{e.hp_max} HP</span>
            </div>
          </div>
        ))}
      </div>

      {state.combat_result && (
        <div className="text-sm text-slate-300 p-2 rounded bg-darkcard border border-slate-700">
          {state.combat_result.message}
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {['Angreifen', 'Verteidigen', 'Warten', 'Fliehen'].map((opt) => (
          <button
            key={opt}
            onClick={() => handleOption(opt)}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-darkcard border border-slate-600 text-slate-200 hover:border-gold hover:text-gold transition text-sm disabled:opacity-50"
          >
            {opt}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 px-4 py-3 rounded-xl bg-darkcard border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-gold"
          placeholder="Ziel eingeben (z.B. 'Spinnenkrabbe 1')"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 rounded-xl bg-gold text-darkbg font-bold hover:bg-amber-400 transition disabled:opacity-50"
        >
          {loading ? '...' : 'Senden'}
        </button>
      </form>
    </div>
  );
}
