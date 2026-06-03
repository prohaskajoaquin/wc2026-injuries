import { useState, useEffect, useCallback, useRef } from 'react'
import { BASE_DATA } from './data.js'
import './App.css'

const STATUS_CFG = {
  out:   { label: 'BAJA CONFIRMADA', color: '#ff3b3b', bg: 'rgba(255,59,59,0.12)'  },
  doubt: { label: 'EN DUDA',         color: '#ff9500', bg: 'rgba(255,149,0,0.12)'  },
  fit:   { label: 'RECUPERADO',      color: '#30d158', bg: 'rgba(48,209,88,0.12)'  },
}

function PlayerCard({ p, index }) {
  const cfg = STATUS_CFG[p.status] || STATUS_CFG.doubt
  return (
    <div className="card" style={{ animationDelay: `${index * 45}ms` }}>
      <div className="card-accent" style={{ background: cfg.color }} />

      <div className="card-head">
        <span className="card-flag">{p.flag}</span>
        <div className="card-team-pos">
          <span className="card-team">{p.team}</span>
          {p.pos && <span className="card-pos"> · {p.pos}</span>}
        </div>
        <div className="status-badge" style={{ background: cfg.bg, color: cfg.color }}>
          <span className="status-dot" style={{ background: cfg.color }} />
          {cfg.label}
        </div>
      </div>

      <div className="card-name">{p.player}</div>
      {p.club && <div className="card-club">🏟 {p.club}</div>}

      {p.injury && (
        <div className="card-injury">
          <span className="inj-icon">🩹</span>
          <span>{p.injury}</span>
        </div>
      )}

      {p.timeline && (
        <div className="card-meta">
          <span>⏱</span>
          <span>{p.timeline}</span>
        </div>
      )}

      {p.replacement && (
        <div className="card-repl">
          <span className="repl-icon">↪</span>
          <span>Reemplazado por: <strong>{p.replacement}</strong></span>
        </div>
      )}

      {p.confirmed_date && (
        <div className="card-date">📅 Confirmado: {p.confirmed_date}</div>
      )}

      {p.link && (
        <a
          className="card-link"
          href={p.link}
          target="_blank"
          rel="noopener noreferrer"
        >
          <span>🔗</span>
          <span>{p.link_label || 'Ver fuente'}</span>
          <span className="link-arrow">↗</span>
        </a>
      )}
    </div>
  )
}

function StatCard({ num, label, colorClass }) {
  return (
    <div className="stat">
      <div className={`stat-num ${colorClass}`}>{num}</div>
      <div className="stat-lbl">{label}</div>
    </div>
  )
}

export default function App() {
  const [data, setData] = useState(BASE_DATA)
  const [filter, setFilter] = useState('all')
  const [lastUpdated, setLastUpdated] = useState(null)
  const [nextUpdateMs, setNextUpdateMs] = useState(null)
  const [countdown, setCountdown] = useState('')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [updateCycle, setUpdateCycle] = useState(0)
  const autoTimerRef = useRef(null)
  const countdownRef = useRef(null)

  // Countdown ticker
  useEffect(() => {
    if (!nextUpdateMs) return
    if (countdownRef.current) clearInterval(countdownRef.current)
    countdownRef.current = setInterval(() => {
      const diff = nextUpdateMs - Date.now()
      if (diff <= 0) { setCountdown('00:00'); return }
      const m = Math.floor(diff / 60000)
      const s = Math.floor((diff % 60000) / 1000)
      setCountdown(`${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`)
    }, 1000)
    return () => clearInterval(countdownRef.current)
  }, [nextUpdateMs])

  const fetchUpdates = useCallback(async () => {
    setIsRefreshing(true)
    const today = new Date().toLocaleDateString('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    })
    try {
      const playerList = BASE_DATA.map(p => `${p.player} (${p.team})`).join(', ')
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1800,
          system: `You are a football journalist. Today is ${today}.
Update injury status for each FIFA World Cup 2026 officially called-up player listed.
Return ONLY a valid JSON array (no markdown fences). Each object:
{
  "player": string,
  "team": string,
  "flag": string,
  "pos": string,
  "club": string,
  "status": "out" | "doubt" | "fit",
  "injury": string (max 35 words),
  "replacement": string or null,
  "timeline": string or null (max 25 words),
  "link": string (best news URL),
  "link_label": string (max 5 words),
  "confirmed_date": string
}`,
          messages: [{
            role: 'user',
            content: `Update injury status as of today (${today}) for: ${playerList}. Return only the JSON array.`,
          }],
        }),
      })
      const json = await res.json()
      const textBlock = (json.content || []).find(b => b.type === 'text')
      if (!textBlock) throw new Error('No text block')
      const raw = textBlock.text.replace(/```json|```/g, '').trim()
      const match = raw.match(/\[[\s\S]*\]/)
      if (!match) throw new Error('No JSON array')
      const parsed = JSON.parse(match[0])
      // Merge: keep base links as fallback
      setData(parsed.map((p, i) => ({
        ...BASE_DATA[i],
        ...p,
        link: (p.link && p.link.startsWith('http')) ? p.link : BASE_DATA[i]?.link,
        link_label: p.link_label || BASE_DATA[i]?.link_label,
      })))
      setUpdateCycle(c => c + 1)
    } catch {
      // Silent fail — keep current data
      setData(BASE_DATA)
    } finally {
      const now = Date.now()
      setLastUpdated(new Date(now))
      setNextUpdateMs(now + 60 * 60 * 1000)
      setIsRefreshing(false)
    }
  }, [])

  const scheduleNext = useCallback(() => {
    if (autoTimerRef.current) clearTimeout(autoTimerRef.current)
    autoTimerRef.current = setTimeout(async () => {
      await fetchUpdates()
      scheduleNext()
    }, 60 * 60 * 1000)
  }, [fetchUpdates])

  useEffect(() => {
    // Show base data immediately
    const now = Date.now()
    setLastUpdated(new Date(now))
    setNextUpdateMs(now + 60 * 60 * 1000)
    // Try live update in background
    fetchUpdates().then(scheduleNext)
    return () => {
      if (autoTimerRef.current) clearTimeout(autoTimerRef.current)
      if (countdownRef.current) clearInterval(countdownRef.current)
    }
  }, [])

  const handleManualRefresh = async () => {
    if (autoTimerRef.current) clearTimeout(autoTimerRef.current)
    await fetchUpdates()
    scheduleNext()
  }

  const counts = {
    all: data.length,
    out: data.filter(p => p.status === 'out').length,
    doubt: data.filter(p => p.status === 'doubt').length,
    fit: data.filter(p => p.status === 'fit').length,
  }

  const filtered = filter === 'all' ? data : data.filter(p => p.status === filter)

  const TABS = [
    { key: 'all',   label: 'Todos' },
    { key: 'out',   label: 'Bajas',      dot: '#ff3b3b' },
    { key: 'doubt', label: 'En duda',    dot: '#ff9500' },
    { key: 'fit',   label: 'Recuperados',dot: '#30d158' },
  ]

  return (
    <>
      <div className="bg-grid" />
      <div className="glow glow1" />
      <div className="glow glow2" />

      <div className="wrap">
        {/* Header */}
        <header>
          <div className="header-top">
            <div className="live-pill">
              <span className="live-dot" />
              EN VIVO
            </div>
            <div className="wc-badge">⚽ FIFA WORLD CUP 2026</div>
            {updateCycle > 0 && (
              <div className="cycle-badge">Ciclo #{updateCycle + 1}</div>
            )}
          </div>
          <h1 className="title-main">LESIONES</h1>
          <h1 className="title-outline">CONVOCATORIAS</h1>
          <p className="subtitle">
            Tracker en tiempo real · solo jugadores de la convocatoria oficial FIFA · actualización automática cada hora
          </p>
        </header>

        {/* Stats */}
        <div className="stats-bar">
          <StatCard num={counts.out}   label="Bajas confirmadas" colorClass="red"   />
          <div className="stat-div" />
          <StatCard num={counts.doubt} label="En duda"           colorClass="amber" />
          <div className="stat-div" />
          <StatCard num={counts.fit}   label="Recuperados"       colorClass="green" />
          <div className="stat-div" />
          <StatCard num={counts.all}   label="Monitoreados"      colorClass="white" />
        </div>

        {/* Update bar */}
        <div className="update-bar">
          <div className="update-left">
            {isRefreshing ? (
              <span className="refreshing-text">
                <span className="spinner" /> Buscando actualizaciones con IA...
              </span>
            ) : lastUpdated ? (
              <span className="updated-text">
                Actualizado: {lastUpdated.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
              </span>
            ) : null}
          </div>
          <div className="update-right">
            {countdown && !isRefreshing && (
              <span className="countdown">Próx. actualiz: {countdown}</span>
            )}
            <button
              className={`refresh-btn ${isRefreshing ? 'disabled' : ''}`}
              onClick={handleManualRefresh}
              disabled={isRefreshing}
            >
              {isRefreshing ? <span className="spin-inline">↺</span> : '↺'} Actualizar
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs">
          {TABS.map(({ key, label, dot }) => (
            <button
              key={key}
              className={`tab ${filter === key ? 'active' : ''}`}
              onClick={() => setFilter(key)}
            >
              {dot && <span className="tab-dot" style={{ background: dot }} />}
              {label} <span className="tab-count">({counts[key]})</span>
            </button>
          ))}
        </div>

        {/* Cards grid */}
        {filtered.length === 0 ? (
          <div className="empty">Sin jugadores en esta categoría.</div>
        ) : (
          <div className="grid">
            {filtered.map((p, i) => (
              <PlayerCard key={p.player} p={p} index={i} />
            ))}
          </div>
        )}

        <footer>
          <p>⚽ FIFA World Cup 2026 · Solo jugadores de la convocatoria oficial del 1–2 junio 2026</p>
          <p>Fuentes: ESPN · Al Jazeera · BBC Sport · Olympics.com · beIN Sports · FIFA</p>
          <p>La IA busca noticias frescas y actualiza el estado cada 60 minutos automáticamente</p>
        </footer>
      </div>
    </>
  )
}
