import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { adventure } from '../api.js';

const CLASS_COLORS = { krieger: 'text-dragonred', magier: 'text-magicblue', schurke: 'text-roguepurple', kleriker: 'text-naturegreen' };

function useAudio(audioUrl, ttsEnabled) {
  const prevRef = useRef(null);
  useEffect(() => {
    if (prevRef.current === audioUrl) return;
    prevRef.current = audioUrl;
    if (!audioUrl || !ttsEnabled) return;
    const audio = new Audio(audioUrl);
    audio.play().catch(() => {});
    return () => audio.pause();
  }, [audioUrl, ttsEnabled]);
}

export default function Adventure() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [state, setState] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const logRef = useRef(null);

  useAudio(state?.audio_url, ttsEnabled);

  useEffect(() => {
    if (location.state?.initial) {
      const initial = location.state.initial;
      setState(initial);
      window.history.replaceState({}, document.title);
    } else {
      setLoading(true);
      adventure.state(sessionId)
        .then((res) => setState(res))
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }
  }, [sessionId]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [state?.narrative]);

  const sendAction = useCallback(async (text, characterName) => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setInput('');
    try {
      const res = await adventure.action(sessionId, text.trim(), characterName);
      setState((prev) => ({
        ...res,
        narrative_history: [...(prev?.narrative_history || []), prev?.narrative],
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const detectCharacter = useCallback((text) => {
    const lower = text.toLowerCase();
    for (const c of state?.characters || []) {
      if (lower.includes(c.name.toLowerCase())) return c.name;
    }
    return state?.characters?.[0]?.name;
  }, [state?.characters]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!state?.characters?.length) return;
    const charName = detectCharacter(input);
    sendAction(input, charName);
  };

  const handleOption = (opt) => {
    if (!state?.characters?.length) return;
    sendAction(opt, state.characters[0].name);
  };

  const handleCharacterAction = (charName, action) => {
    sendAction(action, charName);
  };

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
  const characters = state.characters || [];
  const cs = state.combat_state;

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold text-gold">Der Schatten-Schatz der vergessenen Zitadelle</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setTtsEnabled(!ttsEnabled)}
            className={`text-xs px-2 py-1 rounded border transition ${ttsEnabled ? 'border-naturegreen/50 text-naturegreen' : 'border-slate-600 text-slate-500'}`}
            title={ttsEnabled ? 'Sprache aus' : 'Sprache an'}
          >
            {ttsEnabled ? '🔊' : '🔇'}
          </button>
          {state?.audio_url && (
            <button
              onClick={() => { const a = new Audio(state.audio_url); a.play().catch(() => {}); }}
              className="text-xs px-2 py-1 rounded border border-slate-600 text-slate-400 hover:text-white transition"
              title="Erzählung wiederholen"
            >
              🔄
            </button>
          )}
          <button
            onClick={() => navigate('/')}
            className="text-xs px-3 py-1 rounded border border-slate-600 text-slate-400 hover:text-white transition"
          >
            ✕ Schließen
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-3 p-3 rounded-xl bg-red-900/30 border border-red-700 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Character bar */}
      {characters.length > 0 && (
        <div className="flex gap-2 mb-3 overflow-x-auto">
          {characters.map((c) => {
            const combatChar = cs?.combatants?.find((cc) => cc.is_player && cc.name === c.name);
            const hp = combatChar ? combatChar.hp : c.hp_current;
            const hpMax = combatChar ? combatChar.hp_max : c.hp_max;
            const pct = Math.max(0, (hp / hpMax) * 100);
            return (
              <div key={c.name} className="flex-shrink-0 min-w-[140px] p-3 rounded-xl bg-darkcard border border-slate-700">
                <div className={`text-sm font-bold ${CLASS_COLORS[c.char_class] || 'text-white'}`}>
                  {c.name}
                </div>
                <div className="text-xs text-slate-400 capitalize">{c.char_class}</div>
                <div className="mt-1 h-1.5 rounded-full bg-slate-700 overflow-hidden">
                  <div className="h-full rounded-full bg-naturegreen transition-all" style={{ width: `${pct}%` }} />
                </div>
                <div className="text-xs text-slate-400 mt-0.5">{hp}/{hpMax} HP</div>
                <div className="flex gap-1 mt-1">
                  <button
                    onClick={() => handleCharacterAction(c.name, 'angreifen')}
                    disabled={loading || !isCombat}
                    className="flex-1 text-[10px] px-1 py-0.5 rounded bg-dragonred/20 text-dragonred border border-dragonred/30 disabled:opacity-30"
                  >
                    ⚔️
                  </button>
                  <button
                    onClick={() => handleCharacterAction(c.name, 'verteidigen')}
                    disabled={loading || !isCombat}
                    className="flex-1 text-[10px] px-1 py-0.5 rounded bg-magicblue/20 text-magicblue border border-magicblue/30 disabled:opacity-30"
                  >
                    🛡️
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Narrative log */}
      <div ref={logRef} className="flex-1 overflow-y-auto bg-darkcard border border-slate-700 rounded-2xl p-5 mb-4 space-y-3">
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
        <div className="text-xs text-slate-500 italic">
          {state.current_character && `${state.current_character}`}
        </div>
      </div>

      {isComplete ? (
        <div className="text-center py-4">
          <p className="text-naturegreen text-xl font-bold mb-3">🎉 Abenteuer abgeschlossen!</p>
          <button onClick={() => navigate('/')} className="px-6 py-3 bg-gold text-darkbg rounded-xl font-bold">
            Zum Dashboard
          </button>
        </div>
      ) : isCombat ? (
        <CombatUI state={state} input={input} setInput={setInput} handleSubmit={handleSubmit} handleCharacterAction={handleCharacterAction} loading={loading} characters={characters} />
      ) : (
        <ExplorationUI input={input} setInput={setInput} handleSubmit={handleSubmit} handleOption={handleOption} options={state.options} loading={loading} characters={characters} />
      )}
    </div>
  );
}

function ExplorationUI({ input, setInput, handleSubmit, handleOption, options, loading, characters }) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1">
        {characters.map((c) => (
          <span key={c.name} className={`text-xs px-2 py-0.5 rounded-full border border-slate-600 ${CLASS_COLORS[c.char_class] || 'text-white'}`}>
            {c.name}
          </span>
        ))}
      </div>
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
          placeholder='Name sagt: "Aktion" (z.B. "Finn greift an")'
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

function CombatUI({ state, input, setInput, handleSubmit, handleCharacterAction, loading, characters }) {
  const cs = state.combat_state;
  const enemies = cs?.combatants?.filter((c) => !c.is_player) || cs?.all_combatants?.filter((c) => !c.is_player) || [];
  const currentTurn = cs?.current_turn;

  return (
    <div className="space-y-3">
      <div className="flex gap-2 overflow-x-auto">
        {enemies.length > 0 && enemies.map((e) => (
          <div key={e.name} className={`flex-shrink-0 min-w-[100px] p-2 rounded-xl border ${e.hp <= 0 ? 'border-slate-700 opacity-50' : 'border-dragonred/50'}`}>
            <div className="text-xs text-slate-400">Gegner</div>
            <div className="font-bold text-dragonred text-sm">{e.name}</div>
            <div className="text-xs">
              <span className="text-red-400">{e.hp}</span>
              <span className="text-slate-500">/{e.hp_max} HP</span>
            </div>
          </div>
        ))}
      </div>

      {currentTurn && (
        <div className="text-sm text-slate-300">
          ⏳ <span className="font-bold text-gold">{currentTurn}</span> ist am Zug
        </div>
      )}

      {state.combat_result && (
        <div className="text-sm text-slate-300 p-2 rounded bg-darkcard border border-slate-700">
          {state.combat_result.message}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {characters.map((c) => (
          <div key={c.name} className="p-2 rounded-xl bg-darkcard border border-slate-700">
            <div className={`text-xs font-bold mb-1 ${CLASS_COLORS[c.char_class] || 'text-white'}`}>
              {c.name}
            </div>
            <div className="flex gap-1">
              <button
                onClick={() => handleCharacterAction(c.name, 'angreifen')}
                disabled={loading}
                className="flex-1 text-xs px-2 py-1 rounded bg-dragonred/20 text-dragonred border border-dragonred/30 hover:bg-dragonred/40 disabled:opacity-50"
              >
                ⚔️
              </button>
              <button
                onClick={() => handleCharacterAction(c.name, 'verteidigen')}
                disabled={loading}
                className="flex-1 text-xs px-2 py-1 rounded bg-magicblue/20 text-magicblue border border-magicblue/30 hover:bg-magicblue/40 disabled:opacity-50"
              >
                🛡️
              </button>
              <button
                onClick={() => handleCharacterAction(c.name, 'warten')}
                disabled={loading}
                className="flex-1 text-xs px-2 py-1 rounded bg-slate-600/20 text-slate-300 border border-slate-600/30 hover:bg-slate-600/40 disabled:opacity-50"
              >
                ⏳
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2 flex-wrap">
        {['Fliehen'].map((opt) => (
          <button
            key={opt}
            onClick={() => handleCharacterAction(characters[0]?.name, opt.toLowerCase())}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl bg-darkcard border border-slate-600 text-slate-200 hover:border-gold text-sm disabled:opacity-50"
          >
            {opt}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 px-4 py-3 rounded-xl bg-darkcard border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-gold"
          placeholder='Freitext (z.B. "Finn schießt auf Goblin 1")'
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
