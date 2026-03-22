import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom'
import Markdown from 'react-markdown'
import { Activity, AlertCircle, AlertTriangle, Archive, BarChart3, BookOpen, Brain, BrainCircuit, Building2, Calculator, Check, CheckCircle2, ChevronDown, ChevronRight, Circle, Clipboard, Clock, Cpu, Database, ExternalLink, FileText, Filter, FlaskConical, Gauge, GitBranch, Globe, GraduationCap, Heart, HeartPulse, Home, Hourglass, Hospital, Info, Layers, LayoutDashboard, Lightbulb, Mic, MicOff, MonitorSmartphone, Network, Pill, Plug, Presentation, Radar, RefreshCw, Rocket, Search, Send, Server, Shield, ShieldAlert, Sparkles, Star, Stethoscope, StickyNote, Tags, Target, TrendingDown, TrendingUp, Truck, Users, Volume2, VolumeX, Wallet, Wifi, WifiOff, Wrench, X, XCircle, Zap } from 'lucide-react'
import './style.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/* ═══ Hook fetch ═══ */
function useFetch(url) {
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  React.useEffect(() => {
    setLoading(true)
    fetch(API + url)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [url])
  return { data, loading }
}

/* ═══ Nav ═══ */
function Nav() {
  return (
    <nav className="sf-nav">
      <div className="sf-nav-brand">
        <div className="sf-nav-icon">S</div>
        <span className="sf-nav-title">SIGFAR Hub</span>
        <span className="sf-nav-badge">CHGUV</span>
      </div>
      <div className="sf-nav-links">
        <Link to="/radar"><span className="nav-icon"><Radar size={16}/></span>Radar IA</Link>
        <Link to="/apis"><span className="nav-icon"><Plug size={16}/></span>APIs</Link>
        <Link to="/ml"><span className="nav-icon"><BrainCircuit size={16}/></span>Algoritmos ML</Link>
        <Link to="/propuestas"><span className="nav-icon"><Lightbulb size={16}/></span>Propuestas</Link>
        <Link to="/integraciones"><span className="nav-icon"><Network size={16}/></span>Integraciones</Link>
        <Link to="/jefatura"><span className="nav-icon"><Building2 size={16}/></span>Dirección Servicio Farmacia</Link>
        <Link to="/"><span className="nav-icon"><LayoutDashboard size={16}/></span>Dashboard</Link>
        <Link to="/pacientes"><span className="nav-icon"><Users size={16}/></span>Pacientes</Link>
        <Link to="/emprm"><span className="nav-icon"><ShieldAlert size={16}/></span>EM/PRM</Link>
      </div>
    </nav>
  )
}

/* ═══ Animated Counter ═══ */
function AnimCounter({ target, duration = 1200 }) {
  const [count, setCount] = React.useState(0)
  React.useEffect(() => {
    if (!target && target !== 0) return
    const n = Number(target)
    if (isNaN(n)) return
    let start = null
    const animate = (ts) => {
      if (!start) start = ts
      const progress = Math.min((ts - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * n))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [target, duration])
  return count
}

/* ═══ Dashboard ═══ */
function Dashboard() {
  const [hub, setHub] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [now, setNow] = React.useState(new Date())

  React.useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  React.useEffect(() => {
    fetch(API + '/api/hub/dashboard')
      .then(r => r.json())
      .then(d => { setHub(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="sf-loading">Conectando con APEX SIGFAR...</div>

  const sigfar = hub?.sigfar
  const gestionax = hub?.gestionax
  const sigfarOk = sigfar && !sigfar.error

  const fechaStr = now.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  const horaStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <div>
      {/* Cabecera */}
      <div className="sf-hub-header">
        <div>
          <h1>SIGFAR Hub</h1>
          <p>Centro de integración del Servicio de Farmacia · CHGUV</p>
        </div>
        <div className="sf-hub-clock">
          <div className="sf-hub-clock-time">{horaStr}</div>
          <div className="sf-hub-clock-date">{fechaStr}</div>
        </div>
      </div>

      {/* Plataforma SIGFAR */}
      <div className="sf-hub-section">
        <div className="sf-hub-section-hdr">
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Building2 size={20} className="shrink-0" style={{ color: '#0f766e' }}/> Plataforma SIGFAR</span>
          <span className="sf-hub-source">Datos en tiempo real desde Oracle Cloud</span>
        </div>
        {sigfarOk ? (
          <>
            <div className="sf-hub-stats-row">
              {[
                { label: 'Pacientes activos', value: sigfar.pacientes_activos, color: '#0f766e' },
                { label: 'POF este mes', value: sigfar.pof_mes, color: '#06b6d4' },
                { label: 'EM/PRM pendientes', value: sigfar.emprm_pendientes, color: '#dc2626' },
                { label: 'EM/PRM críticos', value: sigfar.emprm_criticos, color: '#991b1b' },
                { label: 'Validaciones mes', value: sigfar.validaciones_mes, color: '#059669' },
              ].map((c, i) => (
                <div key={i} className="sf-hub-stat">
                  <div className="sf-hub-stat-top">
                    <span className="sf-hub-stat-label">{c.label}</span>
                  </div>
                  <div className="sf-hub-stat-val" style={{ color: c.color }}>
                    <AnimCounter target={c.value} />
                  </div>
                </div>
              ))}
            </div>
            <div className="sf-hub-connected"><CheckCircle2 size={12} className="inline"/> Conectado · Oracle Cloud Madrid · ORDS</div>
          </>
        ) : (
          <div className="sf-hub-error">
            <AlertTriangle size={16} className="inline"/> APEX SIGFAR no disponible — {sigfar?.error || 'Sin conexión configurada'}
          </div>
        )}
      </div>

      {/* GestionAX */}
      <div className="sf-hub-section" style={{ borderLeft: '4px solid #1e40af' }}>
        <div className="sf-hub-section-hdr">
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Wallet size={20} className="shrink-0" style={{ color: '#1e40af' }}/> GestionAX</span>
          <span className="sf-hub-source">Gestión económica y catálogos · Oracle Cloud</span>
        </div>
        {gestionax && !gestionax.error ? (
          <>
            <div className="sf-hub-stats-row" style={{ gridTemplateColumns: 'repeat(3,1fr)' }}>
              {[
                { label: 'Total consumos', value: gestionax.total_consumos, color: '#1e40af' },
                { label: 'Medicamentos GFT', value: gestionax.medicamentos_gft, color: '#0f766e' },
                { label: 'Consumos agrupados', value: gestionax.consumos_agrupados, color: '#c2410c' },
              ].map((c, i) => (
                <div key={i} className="sf-hub-stat">
                  <div className="sf-hub-stat-top">
                    <span className="sf-hub-stat-label">{c.label}</span>
                  </div>
                  <div className="sf-hub-stat-val" style={{ color: c.color }}>
                    <AnimCounter target={c.value} duration={1800} />
                  </div>
                </div>
              ))}
            </div>
            <div className="sf-hub-connected"><CheckCircle2 size={12} className="inline"/> Conectado · Oracle Cloud Madrid · ORDS</div>
          </>
        ) : (
          <div className="sf-hub-pending">
            <Wallet size={24} style={{ color: '#94a3b8', marginBottom: 8 }}/>
            <p><strong>Pendiente de conexión ORDS</strong></p>
            <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Se conectará con APEX GestionAX via Oracle REST Data Services</p>
            <button className="sf-hub-btn-config">Configurar</button>
          </div>
        )}
      </div>

      {/* Inteligencia Artificial */}
      <div className="sf-hub-section">
        <div className="sf-hub-section-hdr">
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Brain size={20} className="shrink-0" style={{ color: '#7c3aed' }}/> Inteligencia Artificial</span>
        </div>
        <div className="sf-hub-ai-grid">
          <div className="sf-hub-ai-card">
            <div className="sf-hub-ai-top">
              <strong style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Server size={16} className="shrink-0" style={{ color: '#475569' }}/> Groq Cloud</strong>
              <span className="sf-hub-ai-badge active"><Activity size={12} className="inline"/>Activo</span>
            </div>
            <p>Llama 3.3 70B</p>
            <span className="sf-hub-ai-tag">Gratuito</span>
          </div>
          <div className="sf-hub-ai-card">
            <div className="sf-hub-ai-top">
              <strong style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Brain size={16} className="shrink-0" style={{ color: '#475569' }}/> Cerebro IA Local</strong>
              <span className="sf-hub-ai-badge pending"><Clock size={12} className="inline"/>Pendiente</span>
            </div>
            <p>Substrate AI · Qwen 72B</p>
            <span className="sf-hub-ai-tag">Servidor local</span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ═══ PlanViewer (POF Dashboard) ═══ */
function PlanViewer({ plan, paciente }) {
  const [collapsed, setCollapsed] = React.useState(false)
  const now = new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

  const edad = React.useMemo(() => {
    if (!paciente?.fecha_nac) return null
    const nac = new Date(paciente.fecha_nac)
    const hoy = new Date()
    let age = hoy.getFullYear() - nac.getFullYear()
    if (hoy.getMonth() < nac.getMonth() || (hoy.getMonth() === nac.getMonth() && hoy.getDate() < nac.getDate())) age--
    return age
  }, [paciente])

  const SECTION_MAP = [
    { key: 'evaluacion', patterns: ['evaluaci', 'valoraci', 'resumen del paciente', 'contexto', 'situaci', 'datos cl'], icon: <Clipboard size={18} className="shrink-0" style={{ color: '#0f766e' }}/>, label: 'Evaluación del paciente', chip: 'Clínica', chipColor: 'teal' },
    { key: 'objetivos', patterns: ['objetivo', 'meta', 'finalidad'], icon: <CheckCircle2 size={18} className="shrink-0" style={{ color: '#1e40af' }}/>, label: 'Objetivos del POF', chip: 'Objetivos', chipColor: 'blue' },
    { key: 'acciones', patterns: ['acci', 'recomendaci', 'ajust', 'intervencion', 'intervención', 'optimizaci', 'propuesta', 'plan de acci'], icon: <Zap size={18} className="shrink-0" style={{ color: '#c2410c' }}/>, label: 'Acciones a realizar', chip: 'Acciones', chipColor: 'orange' },
    { key: 'tratamientos', patterns: ['tratamiento', 'medicamento', 'fármaco', 'farmaco', 'medicaci', 'prescri', 'terapia actual'], icon: <Pill size={18} className="shrink-0" style={{ color: '#0f766e' }}/>, label: 'Tratamientos', chip: 'Fármacos', chipColor: 'teal' },
    { key: 'monitoreo', patterns: ['monitor', 'control', 'vigilancia', 'frecuencia', 'seguimiento'], icon: <BarChart3 size={18} className="shrink-0" style={{ color: '#7c3aed' }}/>, label: 'Frecuencia de evaluación', chip: 'Monitoreo', chipColor: 'purple' },
    { key: 'notificaciones', patterns: ['notificaci', 'alerta', 'aviso', 'señal'], icon: <AlertTriangle size={18} className="shrink-0" style={{ color: '#dc2626' }}/>, label: 'Notificaciones', chip: 'Alertas', chipColor: 'red' },
    { key: 'emprm', patterns: ['em/prm', 'error de medicaci', 'problema relacionado', 'prm detectad'], icon: <ShieldAlert size={18} className="shrink-0" style={{ color: '#dc2626' }}/>, label: 'EM/PRM', chip: 'Alertas', chipColor: 'red' },
    { key: 'conclusion', patterns: ['conclusi', 'resumen final', 'síntesis'], icon: <CheckCircle2 size={18} className="shrink-0" style={{ color: '#059669' }}/>, label: 'Conclusión', chip: 'Resumen', chipColor: 'green' },
  ]

  function classifySection(title) {
    const t = title.toLowerCase()
    for (const s of SECTION_MAP) {
      if (s.patterns.some(p => t.includes(p))) return s
    }
    return { key: 'general', icon: <Clipboard size={18} className="shrink-0" style={{ color: '#475569' }}/>, label: title, chip: 'Info', chipColor: 'teal' }
  }

  const sections = React.useMemo(() => {
    const lines = plan.split('\n')
    const result = []
    let current = { title: '', lines: [] }
    for (const line of lines) {
      const hMatch = line.match(/^#{1,3}\s+(.+)/)
      if (hMatch) {
        if (current.title || current.lines.length) result.push({ ...current })
        current = { title: hMatch[1].replace(/\*+/g, '').trim(), lines: [] }
      } else {
        current.lines.push(line)
      }
    }
    if (current.title || current.lines.length) result.push({ ...current })
    return result.map(s => ({ ...s, meta: classifySection(s.title || 'Resumen') }))
  }, [plan])

  function annotateText(text) {
    return text
      .replace(/(elevad[oa]s?|alto|ALTO|↑|hiperglucemia|hiperpotasemia)/g, '<span class="pof-val-badge pof-val-alto">$1</span>')
      .replace(/(normal(es)?|OK|adecuad[oa]s?|dentro de rango)/gi, '<span class="pof-val-badge pof-val-ok">$1</span>')
      .replace(/(baj[oa]s?|BAJO|↓|disminuid[oa]s?|hipoalbuminemia|hipopotasemia|hipoglucemia)/g, '<span class="pof-val-badge pof-val-bajo">$1</span>')
  }

  function parseTable(lines) {
    const tableLines = lines.filter(l => l.includes('|'))
    const sepIdx = tableLines.findIndex(l => l.match(/^\|?\s*[-:| ]+$/))
    if (sepIdx < 1) return null
    const parse = l => l.split('|').map(c => c.trim()).filter(Boolean)
    const headers = parse(tableLines[sepIdx - 1])
    const rows = tableLines.slice(sepIdx + 1).filter(l => !l.match(/^\|?\s*[-:| ]+$/)).map(parse)
    if (!rows.length) return null
    return { headers, rows }
  }

  function extractAnalytics() {
    const keys = ['creatinina', 'pcr', 'albúmina', 'albumina', 'glucosa', 'hemoglobina', 'potasio', 'sodio', 'urea']
    const found = []
    const seen = new Set()
    for (const line of plan.split('\n')) {
      const lower = line.toLowerCase()
      for (const k of keys) {
        if (lower.includes(k) && !seen.has(k) && found.length < 6) {
          const m = line.match(new RegExp(k + '[:\\s]+([\\d.,]+\\s*[a-zA-Z/%]*)', 'i'))
          if (m) {
            const status = (lower.includes('alto') || lower.includes('elevad')) ? 'alto' : (lower.includes('bajo') || lower.includes('disminuid')) ? 'bajo' : 'ok'
            found.push({ param: k.charAt(0).toUpperCase() + k.slice(1), value: m[1].trim(), status })
            seen.add(k)
          }
        }
      }
    }
    return found
  }

  function renderSectionContent(sec) {
    const text = sec.lines.join('\n').trim()
    if (!text) return null

    // Try table first
    const table = parseTable(sec.lines)
    if (table) {
      return (
        <table className="pof-med-table">
          <thead><tr>{table.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
          <tbody>{table.rows.map((r, ri) => (
            <tr key={ri}>{r.map((c, ci) => <td key={ci}>{ci === 0 ? <strong>{c}</strong> : c}</td>)}</tr>
          ))}</tbody>
        </table>
      )
    }

    // Line-by-line rendering
    const elements = []
    let i = 0
    const lines = sec.lines
    while (i < lines.length) {
      const line = lines[i].trim()
      if (!line) { i++; continue }

      // Numbered item
      const numMatch = line.match(/^\s*(\d+)[\.\)]\s*(.+)/)
      if (numMatch) {
        let itemText = numMatch[2]
        i++
        while (i < lines.length && lines[i].trim() && !lines[i].trim().match(/^\s*\d+[\.\)]/) && !lines[i].trim().match(/^[\-\*]\s/)) {
          itemText += ' ' + lines[i].trim()
          i++
        }
        elements.push(
          <div key={elements.length} className="pof-action-item"
            dangerouslySetInnerHTML={{ __html: annotateText(itemText.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')) }} />
        )
        continue
      }

      // Bullet item
      const bulletMatch = line.match(/^[\-\*]\s+(.+)/)
      if (bulletMatch) {
        elements.push(
          <div key={elements.length} className="pof-bullet-item">
            <span className="pof-bullet-dot" />
            <span dangerouslySetInnerHTML={{ __html: annotateText(bulletMatch[1].replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')) }} />
          </div>
        )
        i++
        continue
      }

      // Paragraph text
      elements.push(
        <p key={elements.length} className="pof-card-body"
          dangerouslySetInnerHTML={{ __html: annotateText(line.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')) }} />
      )
      i++
    }
    return elements.length ? <>{elements}</> : null
  }

  const analytics = React.useMemo(() => extractAnalytics(), [plan])

  return (
    <div className="pof-dashboard">
      <div className="pof-header" onClick={() => setCollapsed(!collapsed)} style={{ cursor: 'pointer' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', width: '100%' }}>
          <div>
            <h3><Clipboard size={18} className="inline"/> Plan de Optimización Farmacoterapéutica</h3>
            {paciente && <p>{paciente.nombre} · {paciente.ubicacion}</p>}
            <p style={{ fontSize: 11, opacity: 0.7 }}>{now}</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="pof-badge-model">Groq · Llama 3.3 70B</span>
            <span style={{ fontSize: 14 }}>{collapsed ? <ChevronRight size={14}/> : <ChevronDown size={14}/>}</span>
          </div>
        </div>
      </div>

      {!collapsed && (
        <>
          {/* Summary grid */}
          <div className="pof-summary-grid" style={{ margin: '12px' }}>
            {paciente && (
              <div className="pof-summary-card">
                <h4><Clipboard size={14} className="inline"/> Datos del paciente</h4>
                {[
                  ['Nombre', paciente.nombre],
                  ['Edad', edad ? `${edad} años` : '—'],
                  ['Peso', `${paciente.peso} kg`],
                  ['Talla', `${paciente.talla} cm`],
                  ['Diagnóstico', paciente.diagnostico],
                  ['Ubicación', paciente.ubicacion],
                ].map(([k, v], i) => (
                  <div key={i} className="pof-summary-row">
                    <span className="pof-summary-label">{k}</span>
                    <span className="pof-summary-value">{v}</span>
                  </div>
                ))}
              </div>
            )}
            <div className="pof-summary-card">
              <h4><FlaskConical size={14} className="inline"/> Analítica destacada</h4>
              {analytics.length ? analytics.map((a, i) => (
                <div key={i} className="pof-summary-row">
                  <span className="pof-summary-label">{a.param}</span>
                  <span className="pof-summary-value">
                    {a.value} <span className={`pof-val-badge pof-val-${a.status}`}>{a.status === 'alto' ? '↑' : a.status === 'bajo' ? '↓' : '✓'}</span>
                  </span>
                </div>
              )) : (
                <div className="pof-summary-row"><span className="pof-summary-label">Sin datos extraídos</span></div>
              )}
            </div>
          </div>

          {/* Section cards */}
          <div className="pof-cards-container" style={{ margin: '0 12px 12px' }}>
            {sections.map((sec, i) => {
              const content = renderSectionContent(sec)
              if (!content && !sec.title) return null
              return (
                <div key={i} className="pof-card">
                  <div className="pof-card-hdr">
                    <span className="pof-card-title">
                      <span className="pof-card-icon">{sec.meta.icon}</span>
                      {sec.meta.label}
                    </span>
                    <span className={`pof-chip pof-chip-${sec.meta.chipColor}`}>{sec.meta.chip}</span>
                  </div>
                  {content}
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}

/* ═══ Lista pacientes ═══ */
function Pacientes() {
  const { data: pacientes, loading } = useFetch('/api/pacientes')

  if (loading) return <div className="sf-loading">Cargando...</div>

  return (
    <div>
      <h2 className="sf-page-title">Pacientes activos</h2>
      <div className="sf-table-wrap">
        <table className="sf-table">
          <thead>
            <tr>
              <th>NHC</th><th>Nombre</th><th>Ubicación</th><th>Diagnóstico</th><th>Ingreso</th><th></th>
            </tr>
          </thead>
          <tbody>
            {(pacientes || []).map(p => (
              <tr key={p.id_episodio}>
                <td><strong>{p.nhc}</strong></td>
                <td>{p.nombre}</td>
                <td><span className="sf-badge">{p.ubicacion}</span></td>
                <td className="sf-td-diag">{p.diagnostico}</td>
                <td>{p.fecha_ingreso}</td>
                <td><Link to={`/paciente/${p.id_episodio}`} className="sf-btn-sm">Ver →</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/* ═══ Ficha paciente ═══ */
function FichaPaciente() {
  const { id } = useParams()
  const { data: pac, loading: lPac } = useFetch(`/api/pacientes/${id}`)
  const { data: trats, loading: lTrat } = useFetch(`/api/pacientes/${id}/tratamientos`)
  const { data: anals, loading: lAnal } = useFetch(`/api/pacientes/${id}/analiticas`)
  const { data: emprm, loading: lEm } = useFetch(`/api/pacientes/${id}/emprm`)
  const [sending, setSending] = React.useState(false)
  const [plan, setPlan] = React.useState(null)

  if (lPac) return <div className="sf-loading">Cargando...</div>
  if (!pac) return <div>Paciente no encontrado</div>

  async function handleSend2GPT() {
    setSending(true)
    try {
      const r = await fetch(API + `/api/send2gpt/${id}`, { method: 'POST' })
      const d = await r.json()
      if (d.status === 'OK') { setPlan(d.plan) }
      else { alert(d.detail || 'Error') }
    } catch (e) { alert('Error: ' + e.message) }
    setSending(false)
  }

  function gravIcon(grav) {
    const g = (grav || '').toLowerCase()
    if (g === 'grave') return <AlertTriangle size={16} className="shrink-0" style={{ color: '#dc2626' }}/>
    if (g === 'moderada') return <ShieldAlert size={16} className="shrink-0" style={{ color: '#f59e0b' }}/>
    return <Shield size={16} className="shrink-0" style={{ color: '#3b82f6' }}/>
  }

  return (
    <div>
      <div className="sf-pac-header">
        <div>
          <h2>{pac.nombre}</h2>
          <p>NHC: {pac.nhc} · {pac.sexo} · {pac.peso}kg · {pac.talla}cm · {pac.ubicacion}</p>
          <p className="sf-diag">{pac.diagnostico}</p>
        </div>
        <button className="sf-btn-gpt" onClick={handleSend2GPT} disabled={sending}>
          {sending ? <><Clock size={16} className="inline"/> Enviando a Groq (Llama 3.3 70B)...</> : <><Zap size={16} className="inline"/> Enviar a IA</>}
        </button>
      </div>

      {plan && <PlanViewer plan={plan} paciente={pac} />}

      <div className="sf-grid-2">
        <div className="sf-card">
          <h3><Pill size={16} className="inline"/> Tratamientos ({trats?.length || 0})</h3>
          {(trats || []).map(t => (
            <div key={t.trat_id} className="sf-trat-row">
              <strong>{t.principio_activo}</strong> — {t.pauta}
            </div>
          ))}
        </div>
        <div className="sf-card">
          <h3><FlaskConical size={16} className="inline"/> Analíticas ({anals?.length || 0})</h3>
          {(anals || []).map((a, i) => (
            <div key={i} className={`sf-anal-row sf-anal-${(a.estado || '').toLowerCase()}`}>
              <span>{a.parametro}</span>
              <strong>{a.valor} {a.unidad}</strong>
              <span className={`sf-badge-${(a.estado || '').toLowerCase()}`}>{a.estado}</span>
            </div>
          ))}
        </div>
      </div>

      {emprm && emprm.length > 0 && (
        <div className="sf-card sf-emprm-section">
          <h3><ShieldAlert size={16} className="inline"/> EM/PRM ({emprm.length})</h3>
          {emprm.map(e => (
            <div key={e.codigo} className={`sf-emprm-row sf-grav-${(e.gravedad || '').toLowerCase()}`}>
              <div className="sf-emprm-head">
                {gravIcon(e.gravedad)}
                <strong>{e.farmaco}</strong>
                <span className="sf-badge-grav">{e.gravedad}</span>
                <span className="sf-badge-dec">{e.decision === 'P' ? 'Pendiente' : 'Aceptado'}</span>
              </div>
              <p>{e.descripcion}</p>
              <p className="sf-emprm-accion">→ {e.accion}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ═══ EM/PRM pendientes ═══ */
function EmprmPendientes() {
  const { data, loading } = useFetch('/api/emprm/pendientes')

  if (loading) return <div className="sf-loading">Cargando...</div>

  function gravIcon(grav) {
    const g = (grav || '').toLowerCase()
    if (g === 'grave') return <AlertTriangle size={16} className="shrink-0" style={{ color: '#dc2626' }}/>
    if (g === 'moderada') return <ShieldAlert size={16} className="shrink-0" style={{ color: '#f59e0b' }}/>
    return <Shield size={16} className="shrink-0" style={{ color: '#3b82f6' }}/>
  }

  return (
    <div>
      <h2 className="sf-page-title">EM/PRM Pendientes</h2>
      {(data || []).map(e => (
        <div key={e.codigo} className={`sf-emprm-card sf-grav-${(e.gravedad || '').toLowerCase()}`}>
          <div className="sf-emprm-head">
            {gravIcon(e.gravedad)}
            <strong>{e.farmaco}</strong>
            <span className="sf-badge-grav">{e.gravedad}</span>
            <Link to={`/paciente/${e.id_episodio}`} className="sf-btn-sm">
              {e.nhc} — {e.ubicacion}
            </Link>
          </div>
          <p>{e.descripcion}</p>
          <p className="sf-emprm-accion">→ {e.accion}</p>
        </div>
      ))}
    </div>
  )
}

/* ═══ Integraciones ═══ */
function Integraciones() {
  const systems = [
    { icon: <Stethoscope size={20}/>, name: 'Plataforma SIGFAR (APEX)', desc: 'Seguimiento clínico, POF, EM/PRM', type: 'REST API', status: 'connected' },
    { icon: <Wallet size={20}/>, name: 'GestionAX (APEX)', desc: 'Gestión económica, consumos, catálogos', type: 'REST API', status: 'connected' },
    { icon: <Server size={20}/>, name: 'Groq Cloud', desc: 'IA generativa Llama 3.3 70B', type: 'REST API', status: 'connected' },
    { icon: <Brain size={20}/>, name: 'Cerebro IA Local', desc: 'Substrate AI · Qwen 72B (servidor local)', type: 'REST API', status: 'pending' },
    { icon: <Pill size={20}/>, name: 'CIMA AEMPS', desc: 'Fichas técnicas medicamentos España', type: 'REST API', status: 'connected' },
    { icon: <FlaskConical size={20}/>, name: 'ClinicalTrials.gov', desc: 'Ensayos clínicos evidencia', type: 'REST API', status: 'connected' },
    { icon: <Activity size={20}/>, name: 'ICCA (UCI)', desc: 'Datos clínicos tiempo real UCI', type: 'HL7/API', status: 'pending' },
    { icon: <FileText size={20}/>, name: 'OMA (Planta)', desc: 'Prescripción electrónica planta', type: 'HL7/API', status: 'pending' },
    { icon: <Building2 size={20}/>, name: 'Hosix (HCE)', desc: 'Historia clínica electrónica', type: 'FHIR R4', status: 'pending' },
    { icon: <FlaskConical size={20}/>, name: 'Microbiología', desc: 'Cultivos y antibiogramas', type: 'HL7', status: 'pending' },
    { icon: <FlaskConical size={20}/>, name: 'Laboratorio', desc: 'Analíticas tiempo real', type: 'HL7', status: 'pending' },
    { icon: <Clipboard size={20}/>, name: 'Versia', desc: 'Prescripción nutrición parenteral', type: 'REST API', status: 'pending' },
    { icon: <MonitorSmartphone size={20}/>, name: 'ExactaMix Pro', desc: 'Robot elaboración NP', type: 'API', status: 'pending' },
    { icon: <MonitorSmartphone size={20}/>, name: 'ChemoMaker', desc: 'Robot elaboración quimioterapia', type: 'API/PDF', status: 'pending' },
    { icon: <Database size={20}/>, name: 'Kardex', desc: 'Preparación carros unidosis', type: 'API', status: 'pending' },
    { icon: <Shield size={20}/>, name: 'Armarios estupefacientes', desc: 'Gestión estupefacientes', type: 'API', status: 'pending' },
    { icon: <Heart size={20}/>, name: 'Abucasis/SIA', desc: 'Receta electrónica CV', type: 'FHIR', status: 'pending' },
    { icon: <FileText size={20}/>, name: 'PubMed/NCBI', desc: 'Evidencia científica', type: 'REST API', status: 'connected' },
  ]

  const connected = systems.filter(s => s.status === 'connected').length

  return (
    <div>
      {/* Cabecera */}
      <div className="sf-integ-header">
        <h1>SIGFAR Hub — Centro de Integraciones</h1>
        <p>Conectando todos los sistemas del Servicio de Farmacia · CHGUV</p>
        <span className="sf-integ-badge">Substrate AI · Subgen AI</span>
      </div>

      {/* Grid de conexiones */}
      <div className="sf-integ-grid">
        {systems.map((s, i) => (
          <div key={i} className="sf-integ-card">
            <div className="sf-integ-card-hdr">
              <span className="sf-integ-card-icon" style={{ color: '#475569' }}>{s.icon}</span>
              <span className="sf-integ-card-name">{s.name}</span>
            </div>
            <span className="sf-integ-card-desc">{s.desc}</span>
            <div className="sf-integ-card-footer">
              <span className="sf-integ-card-type">{s.type}</span>
              <span className={`sf-integ-status ${s.status}`}>
                {s.status === 'connected' ? <><CheckCircle2 size={10} className="inline"/>Conectado</> : <><Clock size={10} className="inline"/>Pendiente</>}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Flujo de datos */}
      <div className="sf-integ-flow">
        <h3>Flujo de datos</h3>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
          {/* Sistemas clínicos */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['ICCA', 'OMA', 'Hosix', 'Lab', 'Micro'].map(s => (
              <div key={s} style={{ background: '#f8fafc', border: '1px solid #e8edf2', borderRadius: 8, padding: '6px 14px', fontSize: 12, fontWeight: 600, color: '#334155' }}>{s}</div>
            ))}
          </div>
          <div style={{ fontSize: 20, color: '#94a3b8', letterSpacing: 8 }}>↓ ↓ ↓ ↓ ↓</div>

          {/* Hub central */}
          <div style={{ background: 'linear-gradient(135deg, #0f766e, #14b8a6)', color: '#fff', borderRadius: 14, padding: '20px 48px', fontWeight: 800, fontSize: 16, boxShadow: '0 4px 20px rgba(15,118,110,.3)', textAlign: 'center', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Brain size={22}/> SIGFAR Hub + IA
          </div>

          {/* Flechas abajo */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, textAlign: 'center' }}>
            <div style={{ fontSize: 20, color: '#94a3b8' }}>↕</div>
            <div style={{ fontSize: 20, color: '#94a3b8' }}>↕</div>
          </div>

          {/* Elaboración + Interfaces */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, width: '100%' }}>
            <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: 12, padding: 16, textAlign: 'center' }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#92400e', marginBottom: 8 }}>Elaboración</div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                {['Versia', 'ExactaMix', 'ChemoMaker', 'Kardex'].map(s => (
                  <div key={s} style={{ background: '#fff', border: '1px solid #e8edf2', borderRadius: 6, padding: '4px 10px', fontSize: 11, fontWeight: 600, color: '#334155' }}>{s}</div>
                ))}
              </div>
            </div>
            <div style={{ background: '#eff6ff', border: '1px solid #dbeafe', borderRadius: 12, padding: 16, textAlign: 'center' }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#1e40af', marginBottom: 8 }}>Interfaces</div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                {['React Web', 'APEX SIGFAR', 'APEX GestionAX'].map(s => (
                  <div key={s} style={{ background: '#fff', border: '1px solid #e8edf2', borderRadius: 6, padding: '4px 10px', fontSize: 11, fontWeight: 600, color: '#334155' }}>{s}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="sf-integ-kpis">
        {[
          { value: `${connected}/18`, label: 'Sistemas conectados', icon: <Network size={16}/> },
          { value: '4', label: 'APIs activas', icon: <Server size={16}/> },
          { value: '1', label: 'Modelos IA (Groq Llama 3.3)', icon: <Brain size={16}/> },
          { value: '5', label: 'Pacientes unificados', icon: <Users size={16}/> },
        ].map((k, i) => (
          <div key={i} className="sf-integ-kpi">
            <div style={{ color: '#94a3b8', marginBottom: 4 }}>{k.icon}</div>
            <div className="sf-integ-kpi-val">{k.value}</div>
            <div className="sf-integ-kpi-label">{k.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ═══ Jefatura — Cuadro de Mandos ═══ */
function Jefatura() {
  const [now, setNow] = React.useState(new Date())
  const [resumen, setResumen] = React.useState(null)
  const [gastoServicio, setGastoServicio] = React.useState(null)
  const [topMeds, setTopMeds] = React.useState(null)
  const [evolucion, setEvolucion] = React.useState(null)
  const [showAllMeds, setShowAllMeds] = React.useState(false)
  const [pregunta, setPregunta] = React.useState('')
  const [messages, setMessages] = React.useState([])
  const [thinking, setThinking] = React.useState(false)
  const [recording, setRecording] = React.useState(false)
  const [muted, setMuted] = React.useState(false)
  const [micError, setMicError] = React.useState('')
  const recognitionRef = React.useRef(null)
  const messagesEndRef = React.useRef(null)
  const sendTimeoutRef = React.useRef(null)
  const finalTextRef = React.useRef('')

  React.useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  React.useEffect(() => {
    const safe = (url, setter) => fetch(API + url).then(r => r.json()).then(setter).catch(() => {})
    safe('/api/jefatura/resumen', setResumen)
    safe('/api/jefatura/gasto-servicio', d => setGastoServicio(d?.items || null))
    safe('/api/jefatura/top-medicamentos', d => setTopMeds(d?.items || null))
    safe('/api/jefatura/evolucion-mensual', d => setEvolucion(d?.items || null))
  }, [])

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const fmt = (v) => v != null ? Number(v).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €' : '—'
  const fmtN = (v) => v != null ? Number(v).toLocaleString('es-ES') : '—'

  const fechaStr = now.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  const horaStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  const sig = resumen?.sigfar
  const gax = resumen?.gestionax

  async function handleAsk() {
    if (!pregunta.trim()) return
    const ts = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    setMessages(prev => [...prev, { role: 'user', text: pregunta, timestamp: ts }])
    const q = pregunta
    setPregunta('')
    setThinking(true)
    try {
      const r = await fetch(API + '/api/jefatura/sigfarita', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: q })
      })
      const d = await r.json()
      const resp = d.respuesta || d.detail || 'Sin respuesta'
      const tsR = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      setMessages(prev => [...prev, { role: 'assistant', text: resp, timestamp: tsR }])
      if (!muted && d.respuesta) speakText(d.respuesta)
    } catch (e) {
      const tsR = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error al conectar con Sigfarita: ' + e.message, timestamp: tsR }])
    }
    setThinking(false)
  }

  function speakText(text) {
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    const voices = window.speechSynthesis.getVoices()
    const esVoice = voices.find(v => v.lang.startsWith('es'))
    if (esVoice) utt.voice = esVoice
    utt.lang = 'es-ES'
    utt.rate = 1
    window.speechSynthesis.speak(utt)
  }

  function toggleMic() {
    if (recording) {
      if (recognitionRef.current) recognitionRef.current.stop()
      setRecording(false)
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) { alert('Tu navegador no soporta reconocimiento de voz'); return }
    setMicError('')
    finalTextRef.current = ''
    const recog = new SpeechRecognition()
    recog.lang = 'es-ES'
    recog.continuous = false
    recog.interimResults = true
    recog.onresult = (e) => {
      let interim = ''
      let final = ''
      for (let i = 0; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          final += e.results[i][0].transcript
        } else {
          interim += e.results[i][0].transcript
        }
      }
      if (final) {
        finalTextRef.current = final
        setPregunta(final)
      } else if (interim) {
        setPregunta(interim)
      }
    }
    recog.onend = () => {
      setRecording(false)
      const text = finalTextRef.current.trim()
      if (text) {
        if (sendTimeoutRef.current) clearTimeout(sendTimeoutRef.current)
        sendTimeoutRef.current = setTimeout(() => {
          // Auto-send: build and send the message directly
          const ts = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
          setMessages(prev => [...prev, { role: 'user', text, timestamp: ts }])
          setPregunta('')
          setThinking(true)
          fetch(API + '/api/jefatura/sigfarita', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: text })
          })
            .then(r => r.json())
            .then(d => {
              const resp = d.respuesta || d.detail || 'Sin respuesta'
              const tsR = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
              setMessages(prev => [...prev, { role: 'assistant', text: resp, timestamp: tsR }])
              if (!muted && d.respuesta) speakText(d.respuesta)
              setThinking(false)
            })
            .catch(err => {
              const tsR = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
              setMessages(prev => [...prev, { role: 'assistant', text: 'Error al conectar con Sigfarita: ' + err.message, timestamp: tsR }])
              setThinking(false)
            })
        }, 500)
      }
    }
    recog.onerror = (e) => {
      setRecording(false)
      if (e.error === 'no-speech' || e.error === 'audio-capture' || e.error === 'not-allowed') {
        setMicError('No te he entendido, repite por favor')
        setTimeout(() => setMicError(''), 3000)
      }
    }
    recognitionRef.current = recog
    recog.start()
    setRecording(true)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleAsk()
  }

  // Gasto total for % calculation
  const gastoTotal = React.useMemo(() => {
    if (!gastoServicio) return 0
    return gastoServicio.reduce((sum, r) => sum + (Number(r.gasto) || 0), 0)
  }, [gastoServicio])

  return (
    <div className="jef-layout">
      {/* COLUMNA IZQUIERDA — Dashboard */}
      <div className="jef-main">
        {/* 1. CABECERA */}
        <div className="jef-header">
          <div>
            <h1>Cuadro de Mandos</h1>
            <p className="jef-sub">Dra. Pilar Blasco Segura · Jefa de Servicio de Farmacia · CHGUV</p>
            <span className="jef-badge">Sigfarita · Asistente IA activa</span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="jef-clock" style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}><Clock size={16}/> {horaStr}</div>
            <div className="jef-date" style={{ textTransform: 'capitalize' }}>{fechaStr}</div>
          </div>
        </div>

        {/* 2. KPIs EJECUTIVOS */}
        <div className="jef-kpis">
          {[
            { label: 'Pacientes activos', value: sig?.pacientes_activos, color: '#0f766e' },
            { label: 'Gasto mes actual', value: gax?.gasto_mes_actual, color: '#1e40af', isMoney: true },
            { label: 'EM/PRM pendientes', value: sig?.emprm_pendientes, color: '#dc2626' },
            { label: 'EM/PRM críticos', value: sig?.emprm_criticos, color: '#991b1b' },
            { label: 'Validaciones mes', value: sig?.validaciones_mes, color: '#059669' },
            { label: 'Medicamentos GFT', value: gax?.medicamentos_gft, color: '#7c3aed' },
          ].map((k, i) => (
            <div key={i} className="jef-kpi">
              <div className="jef-kpi-val" style={{ color: k.color }}>
                {k.isMoney ? fmt(k.value) : <AnimCounter target={k.value} />}
              </div>
              <div className="jef-kpi-label">{k.label}</div>
            </div>
          ))}
        </div>

        {/* 3. GASTO POR SERVICIO */}
        <div className="jef-card">
          <div className="jef-card-hdr"><Wallet size={18} className="shrink-0" style={{ color: '#475569' }}/> Gasto por servicio clínico</div>
          <div className="jef-card-body">
            {gastoServicio ? (
              <table className="jef-table">
                <thead><tr><th>Servicio</th><th>Actividad</th><th className="num">Artículos</th><th className="num">Unidades</th><th className="num">Gasto (€)</th><th className="num">% Total</th></tr></thead>
                <tbody>
                  {gastoServicio.sort((a, b) => (Number(b.gasto) || 0) - (Number(a.gasto) || 0)).map((r, i) => (
                    <tr key={i}>
                      <td><strong>{r.servicio || r.centro_actividad || r.descripcion_centro || '—'}</strong></td>
                      <td>{r.actividad || r.centro_actividad || '—'}</td>
                      <td className="num">{fmtN(r.articulos || r.articulos_distintos)}</td>
                      <td className="num">{fmtN(r.unidades || r.total_unidades)}</td>
                      <td className="num">{fmt(r.gasto || r.total_gasto)}</td>
                      <td className="num">{gastoTotal ? ((Number(r.gasto || r.total_gasto) / gastoTotal) * 100).toFixed(1) + '%' : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="jef-warn"><AlertTriangle size={14} className="inline"/> Datos no disponibles</div>}
          </div>
        </div>

        {/* 4. TOP MEDICAMENTOS */}
        <div className="jef-card">
          <div className="jef-card-hdr"><Pill size={18} className="shrink-0" style={{ color: '#475569' }}/> Top medicamentos por gasto</div>
          <div className="jef-card-body">
            {topMeds ? (
              <>
                <table className="jef-table">
                  <thead><tr><th>#</th><th>Medicamento</th><th>ATC</th><th className="num">Unidades</th><th className="num">Gasto (€)</th><th className="num">€/unidad</th><th>GFT</th></tr></thead>
                  <tbody>
                    {(showAllMeds ? topMeds : topMeds.slice(0, 15)).map((m, i) => {
                      const gft = m.gft || m.estado_gft || null
                      const gftLower = (gft || '').toLowerCase()
                      const gftClass = gft == null ? 'jef-gft-fuera' : gftLower.includes('activ') ? 'jef-gft-activo' : gftLower.includes('restringid') ? 'jef-gft-restringido' : gftLower.includes('inactiv') ? 'jef-gft-inactivo' : 'jef-gft-fuera'
                      const gftLabel = gft == null ? 'Fuera GFT' : gft
                      const unidades = Number(m.unidades || m.total_unidades) || 0
                      const gasto = Number(m.gasto || m.total_gasto) || 0
                      const precioUd = unidades ? (gasto / unidades) : 0
                      return (
                        <tr key={i}>
                          <td>{i + 1}</td>
                          <td><strong>{m.medicamento || m.descripcion || m.principio_activo || '—'}</strong></td>
                          <td>{m.atc || m.atc_codigo || '—'}</td>
                          <td className="num">{fmtN(unidades)}</td>
                          <td className="num">{fmt(gasto)}</td>
                          <td className="num">{fmt(precioUd)}</td>
                          <td><span className={`jef-gft-badge ${gftClass}`}>{gftLabel}</span></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                {topMeds.length > 15 && (
                  <div style={{ textAlign: 'center', marginTop: 10 }}>
                    <button onClick={() => setShowAllMeds(!showAllMeds)} style={{ background: 'none', border: '1px solid #d1d5db', borderRadius: 8, padding: '6px 20px', fontSize: 12, fontWeight: 600, cursor: 'pointer', color: '#334155' }}>
                      {showAllMeds ? 'Mostrar menos' : `Ver todos (${topMeds.length})`}
                    </button>
                  </div>
                )}
              </>
            ) : <div className="jef-warn"><AlertTriangle size={14} className="inline"/> Datos no disponibles</div>}
          </div>
        </div>

        {/* 5. EVOLUCIÓN MENSUAL */}
        <div className="jef-card">
          <div className="jef-card-hdr"><TrendingUp size={18} className="shrink-0" style={{ color: '#475569' }}/> Evolución mensual del gasto</div>
          <div className="jef-card-body">
            {evolucion ? (
              <table className="jef-table">
                <thead><tr><th>Año</th><th>Mes</th><th className="num">Transacciones</th><th className="num">Artículos</th><th className="num">Unidades</th><th className="num">Gasto (€)</th></tr></thead>
                <tbody>
                  {evolucion.map((r, i) => (
                    <tr key={i}>
                      <td>{r.anyo || r.año || r.year || '—'}</td>
                      <td>{r.mes || r.month || '—'}</td>
                      <td className="num">{fmtN(r.transacciones || r.total_transacciones)}</td>
                      <td className="num">{fmtN(r.articulos || r.articulos_distintos)}</td>
                      <td className="num">{fmtN(r.unidades || r.total_unidades)}</td>
                      <td className="num">{fmt(r.gasto || r.total_gasto)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="jef-warn"><AlertTriangle size={14} className="inline"/> Datos no disponibles</div>}
          </div>
        </div>
      </div>

      {/* COLUMNA DERECHA — Sigfarita sidebar */}
      <div className="jef-sidebar">
        <div className="jef-sidebar-hdr">
          <h3><Brain size={18} className="shrink-0"/> Sigfarita</h3>
          <p>Asistente IA · Dra. Blasco</p>
        </div>

        <div className="sigfarita-messages">
          {messages.length === 0 && !thinking && (
            <div className="sigfarita-welcome">
              <span className="sig-emoji"><Brain size={36} style={{ color: 'rgba(255,255,255,.4)' }}/></span>
              Hola Dra. Blasco, soy Sigfarita.<br/>Pregúntame lo que necesites sobre el servicio.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`sig-msg ${m.role}`}>
              {m.role === 'assistant' ? <Markdown>{m.text}</Markdown> : m.text}
              <span className="sig-time">{m.timestamp}</span>
            </div>
          ))}
          {thinking && <div className="sig-thinking">Pensando</div>}
          <div ref={messagesEndRef} />
        </div>

        <div className="sigfarita-input-area">
          <div className="sigfarita-sound-row">
            <button className="sigfarita-btn-sound" onClick={() => { if (messages.length) speakText(messages.filter(m => m.role === 'assistant').pop()?.text || '') }} title="Leer última respuesta"><Volume2 size={14}/></button>
            <button className="sigfarita-btn-sound" onClick={() => { window.speechSynthesis.cancel(); setMuted(!muted) }} title={muted ? 'Activar voz' : 'Silenciar'}>
              {muted ? <VolumeX size={14}/> : <Volume2 size={14}/>}
            </button>
          </div>
          <div className="sigfarita-input-row">
            <input
              className="sigfarita-input"
              type="text"
              placeholder="Pregunta a Sigfarita..."
              value={pregunta}
              onChange={e => setPregunta(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={thinking}
            />
            <button className="sigfarita-btn sigfarita-btn-send" onClick={handleAsk} disabled={thinking}><Send size={16}/></button>
            <button className={`sigfarita-btn sigfarita-btn-mic${recording ? ' recording' : ''}`} onClick={toggleMic}>{recording ? <MicOff size={16}/> : <Mic size={16}/>}</button>
          </div>
          {recording && <div style={{ fontSize: 10, color: 'rgba(255,255,255,.6)', fontStyle: 'italic', textAlign: 'center' }}>Escuchando...</div>}
          {micError && <div style={{ fontSize: 10, color: '#fca5a5', textAlign: 'center' }}>{micError}</div>}
        </div>
      </div>
    </div>
  )
}

/* ═══ Radar IA ═══ */

const RADAR_CATS = ['VALIDACION','FARMACOCINETICA','NUTRICION','PROA','ELABORACION','STOCK_LOGISTICA','ROBOTICA','FARMACOECONOMIA','CUADRO_MANDOS','REGULACION']
const RADAR_CAT_LABELS = {
  VALIDACION:'Validación', FARMACOCINETICA:'Farmacocinética', NUTRICION:'Nutrición', PROA:'PROA',
  ELABORACION:'Elaboración', STOCK_LOGISTICA:'Stock/Logística', ROBOTICA:'Robótica',
  FARMACOECONOMIA:'Farmacoeconomía', CUADRO_MANDOS:'Cuadro Mandos', REGULACION:'Regulación'
}
const RADAR_CAT_ICONS = {
  VALIDACION: ShieldAlert, FARMACOCINETICA: FlaskConical, NUTRICION: Heart, PROA: Shield,
  ELABORACION: Pill, STOCK_LOGISTICA: Database, ROBOTICA: Zap,
  FARMACOECONOMIA: Wallet, CUADRO_MANDOS: BarChart3, REGULACION: FileText
}
const RADAR_ESTADOS = ['IMPLEMENTADO','PARCIAL','PLANIFICADO','NUEVO']
const RADAR_FUENTES = ['PUBMED','GOOGLE_NEWS','CLINICALTRIALS','SEMANTIC']
const RADAR_FUENTE_LABELS = {PUBMED:'PubMed', GOOGLE_NEWS:'Google News', CLINICALTRIALS:'ClinicalTrials', SEMANTIC:'Semantic Scholar'}
const RADAR_ESTADO_ICONS = { IMPLEMENTADO: CheckCircle2, PARCIAL: Clock, PLANIFICADO: Hourglass, NUEVO: AlertCircle }
const RADAR_ESTADO_COLORS = { IMPLEMENTADO: '#16a34a', PARCIAL: '#ea580c', PLANIFICADO: '#2563eb', NUEVO: '#dc2626' }

function isoToFlag(code) {
  if (!code || code.length !== 2) return '🌐'
  return String.fromCodePoint(...[...code.toUpperCase()].map(c => 0x1F1E6 - 65 + c.charCodeAt(0)))
}

function RadarIA() {
  const [items, setItems] = React.useState([])
  const [stats, setStats] = React.useState({})
  const [favs, setFavs] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [scanning, setScanning] = React.useState(false)
  const [scanResult, setScanResult] = React.useState(null)
  const [tab, setTab] = React.useState('radar')
  const [fCat, setFCat] = React.useState('')
  const [fEstado, setFEstado] = React.useState('')
  const [fFuente, setFFuente] = React.useState('')
  const [fFav, setFFav] = React.useState(false)
  const [fBuscar, setFBuscar] = React.useState('')
  const [fPeriodo, setFPeriodo] = React.useState('')
  const [notaModal, setNotaModal] = React.useState(null)
  const [notaText, setNotaText] = React.useState('')

  const loadItems = React.useCallback(() => {
    setLoading(true)
    const p = new URLSearchParams()
    if (fCat) p.set('categoria', fCat)
    if (fEstado) p.set('estado', fEstado)
    if (fFuente) p.set('fuente', fFuente)
    if (fFav) p.set('favorito', 'true')
    if (fBuscar) p.set('buscar', fBuscar)
    if (fPeriodo) p.set('periodo', fPeriodo)
    p.set('limit', '150')
    fetch(`${API}/api/radar/items?${p}`).then(r => r.json()).then(d => { setItems(d); setLoading(false) }).catch(() => setLoading(false))
  }, [fCat, fEstado, fFuente, fFav, fBuscar, fPeriodo])

  const loadStats = () => { fetch(`${API}/api/radar/stats`).then(r => r.json()).then(setStats).catch(() => {}) }
  const loadFavs = () => { fetch(`${API}/api/radar/favoritos`).then(r => r.json()).then(setFavs).catch(() => {}) }

  React.useEffect(() => { loadItems(); loadStats() }, [loadItems])
  React.useEffect(() => { if (tab === 'favoritos') loadFavs() }, [tab])

  const doScan = async () => {
    setScanning(true); setScanResult(null)
    try {
      const r = await fetch(`${API}/api/radar/scan`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: '{}' })
      const d = await r.json(); setScanResult(d); loadItems(); loadStats()
    } catch (e) { setScanResult({ status: 'ERROR', error: e.message }) }
    setScanning(false)
  }

  const toggleFav = async (id) => {
    try {
      const r = await fetch(`${API}/api/radar/toggle-favorito`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({item_id: id}) })
      const d = await r.json()
      setItems(prev => prev.map(it => it.id === id ? {...it, favorito: d.favorito} : it))
      loadStats()
    } catch {}
  }

  const saveNota = async () => {
    if (!notaModal) return
    try {
      await fetch(`${API}/api/radar/set-nota`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({item_id: notaModal, nota: notaText}) })
      setItems(prev => prev.map(it => it.id === notaModal ? {...it, nota_usuario: notaText} : it))
    } catch {}
    setNotaModal(null)
  }

  const setPrioridad = async (id, p) => {
    try {
      await fetch(`${API}/api/radar/set-prioridad`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({item_id: id, prioridad: p}) })
      setFavs(prev => prev.map(it => it.id === id ? {...it, prioridad_usuario: p} : it))
    } catch {}
  }

  const archivar = async (id) => {
    try { await fetch(`${API}/api/radar/archivar/${id}`, { method:'POST' }); setItems(prev => prev.filter(it => it.id !== id)); loadStats() } catch {}
  }

  const relColor = (r) => r >= 80 ? '#16a34a' : r >= 60 ? '#ca8a04' : r >= 40 ? '#ea580c' : '#dc2626'
  const estadoLabel = (e) => ({IMPLEMENTADO:'Implementado', PARCIAL:'Parcial', PLANIFICADO:'Planificado', NUEVO:'Nuevo'}[e] || e)
  const maxCat = Math.max(1, ...Object.values(stats.por_categoria || {}))

  return (
    <div className="radar-page">
      <div className="radar-header">
        <div>
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:6}}>
            <Radar size={28} color="#fff" />
            <h1 style={{fontSize:24,fontWeight:800,color:'#fff',margin:0}}>SIGFAR Hub · Radar IA</h1>
            <span className="live-badge"><span className="live-dot"></span>LIVE</span>
          </div>
          <p style={{fontSize:13,color:'rgba(255,255,255,.7)',margin:0}}>Monitorización inteligente de novedades IA en farmacia hospitalaria</p>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Ítems</div>
            <div style={{fontSize:28,fontWeight:800}}>{stats.total || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Nuevos (7d)</div>
            <div style={{fontSize:28,fontWeight:800}}>{stats.nuevos_semana || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Favoritos</div>
            <div style={{fontSize:28,fontWeight:800,color:'#fbbf24'}}>{stats.favoritos || 0}</div>
          </div>
          <button className="radar-scan-btn" onClick={doScan} disabled={scanning}>
            {scanning ? <><span className="radar-spinner"></span> Escaneando...</> : <><RefreshCw size={16}/> Actualizar</>}
          </button>
        </div>
      </div>

      {scanResult && (
        <div className={`radar-scan-result ${scanResult.status === 'OK' ? 'ok' : 'err'}`}>
          {scanResult.status === 'OK'
            ? <><CheckCircle2 size={16}/> Escaneo completado en {scanResult.duracion_seg}s — {scanResult.items_nuevos} nuevos, {scanResult.items_duplicados} duplicados, {scanResult.items_enriquecidos} enriquecidos</>
            : <><XCircle size={16}/> Error: {scanResult.error || 'Error desconocido'}</>}
          <button onClick={() => setScanResult(null)} style={{marginLeft:12,background:'none',border:'none',cursor:'pointer',fontSize:16}}>×</button>
        </div>
      )}

      <div className="radar-tabs">
        <button className={tab==='radar'?'active':''} onClick={()=>setTab('radar')}><Radar size={14}/> Radar</button>
        <button className={tab==='favoritos'?'active':''} onClick={()=>setTab('favoritos')}><Star size={14}/> Favoritos ({stats.favoritos||0})</button>
        <button className={tab==='stats'?'active':''} onClick={()=>setTab('stats')}><BarChart3 size={14}/> Estadísticas</button>
      </div>

      {tab === 'radar' && <>
        <div className="radar-filters">
          <Filter size={16} style={{color:'#64748b',flexShrink:0}} />
          <select value={fCat} onChange={e=>setFCat(e.target.value)}>
            <option value="">Todas las categorías</option>
            {RADAR_CATS.map(c => <option key={c} value={c}>{RADAR_CAT_LABELS[c]}</option>)}
          </select>
          <select value={fEstado} onChange={e=>setFEstado(e.target.value)}>
            <option value="">Todos los estados</option>
            {RADAR_ESTADOS.map(e => <option key={e} value={e}>{estadoLabel(e)}</option>)}
          </select>
          <select value={fFuente} onChange={e=>setFFuente(e.target.value)}>
            <option value="">Todas las fuentes</option>
            {RADAR_FUENTES.map(f => <option key={f} value={f}>{RADAR_FUENTE_LABELS[f]}</option>)}
          </select>
          <select value={fPeriodo} onChange={e=>setFPeriodo(e.target.value)}>
            <option value="">Todo el período</option>
            <option value="7">Última semana</option>
            <option value="30">Último mes</option>
            <option value="90">Últimos 3 meses</option>
          </select>
          <label className="radar-fav-toggle">
            <input type="checkbox" checked={fFav} onChange={e=>setFFav(e.target.checked)} />
            <Star size={12}/> Solo favoritos
          </label>
          <div className="radar-search-wrap">
            <Search size={14} className="radar-search-icon" />
            <input className="radar-search" type="text" placeholder="Buscar..." value={fBuscar} onChange={e=>setFBuscar(e.target.value)} />
          </div>
        </div>

        {loading ? <div className="sf-loading">Cargando ítems del radar...</div> : (
          items.length === 0 ? (
            <div className="radar-empty">
              <Radar size={48} style={{opacity:.3,marginBottom:12}} />
              <p>No hay ítems. Pulsa "Actualizar" para escanear las fuentes.</p>
            </div>
          ) : (
            <div className="radar-grid">
              {items.map(it => {
                const CatIcon = RADAR_CAT_ICONS[it.categoria] || FileText
                const EstIcon = RADAR_ESTADO_ICONS[it.estado_sigfar_hub] || AlertCircle
                const estColor = RADAR_ESTADO_COLORS[it.estado_sigfar_hub] || '#dc2626'
                return (
                  <div key={it.id} className={`radar-card ${it.leido ? 'read' : ''}`}>
                    <div className="radar-card-top">
                      <span className="radar-flag">{isoToFlag(it.pais)}</span>
                      <span className="cat-tag"><CatIcon size={10}/> {RADAR_CAT_LABELS[it.categoria] || it.categoria}</span>
                      <span className="radar-fuente-tag">{RADAR_FUENTE_LABELS[it.fuente] || it.fuente}</span>
                      <span className="metric-badge" style={{background:relColor(it.relevancia),color:'#fff'}}>{it.relevancia}%</span>
                      <button className="fav-btn" onClick={()=>toggleFav(it.id)} title={it.favorito?'Quitar favorito':'Añadir favorito'}>
                        <Star size={16} fill={it.favorito ? 'currentColor' : 'none'} color={it.favorito ? '#f59e0b' : '#94a3b8'} />
                      </button>
                    </div>
                    <h4 className="radar-card-title">
                      <a href={it.url_original} target="_blank" rel="noreferrer">{it.titulo}</a>
                    </h4>
                    {it.institucion && <div className="radar-card-inst">{it.institucion}</div>}
                    <p className="radar-card-resumen">{it.resumen_ia || it.resumen || 'Sin resumen disponible'}</p>
                    {it.como_en_sigfar_hub && (
                      <div className="radar-sigfar-box">
                        <Brain size={12}/> <strong>En SIGFAR Hub:</strong> {it.como_en_sigfar_hub}
                      </div>
                    )}
                    <div className="radar-card-bottom">
                      <span className="radar-estado-badge" style={{color: estColor, borderColor: estColor}}>
                        <EstIcon size={12}/> {estadoLabel(it.estado_sigfar_hub)}
                      </span>
                      {it.modulo_sigfar && <span className="radar-modulo">{it.modulo_sigfar}</span>}
                      {it.fecha_publicacion && <span className="radar-date"><Clock size={10}/> {it.fecha_publicacion}</span>}
                      <div className="radar-card-actions">
                        <button onClick={()=>{setNotaModal(it.id);setNotaText(it.nota_usuario||'')}} title="Añadir nota"><StickyNote size={14}/></button>
                        <button onClick={()=>archivar(it.id)} title="Archivar"><Archive size={14}/></button>
                        <a href={it.url_original} target="_blank" rel="noreferrer" className="radar-link-btn"><ExternalLink size={12}/> Ver fuente</a>
                      </div>
                    </div>
                    {it.tags && <div className="radar-tags">{it.tags.split(',').map((t,i)=><span key={i} className="radar-tag">{t.trim()}</span>)}</div>}
                  </div>
                )
              })}
            </div>
          )
        )}
      </>}

      {tab === 'favoritos' && (
        <div className="radar-favs-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Star size={18} color="#f59e0b"/> Backlog de ideas — Favoritos ({favs.length})</h3>
          {favs.length === 0 ? <p style={{color:'#64748b'}}>No hay favoritos todavía. Marca ítems con <Star size={12}/> para añadirlos aquí.</p> : (
            <div className="radar-grid">
              {favs.map(f => {
                const CatIcon = RADAR_CAT_ICONS[f.categoria] || FileText
                const prioIcon = f.prioridad_usuario === 'ALTA' ? AlertTriangle : f.prioridad_usuario === 'MEDIA' ? AlertCircle : Info
                const PrioIcon = prioIcon
                return (
                  <div key={f.id} className="radar-card">
                    <div className="radar-card-top">
                      <span className="radar-flag">{isoToFlag(f.pais)}</span>
                      <span className="cat-tag"><CatIcon size={10}/> {RADAR_CAT_LABELS[f.categoria]||f.categoria}</span>
                      <span className="metric-badge" style={{background:relColor(f.relevancia),color:'#fff'}}>{f.relevancia}%</span>
                      <select value={f.prioridad_usuario||''} onChange={e=>setPrioridad(f.id,e.target.value)} className="radar-prio-select">
                        <option value="">Prioridad...</option>
                        <option value="ALTA">Alta</option>
                        <option value="MEDIA">Media</option>
                        <option value="BAJA">Baja</option>
                      </select>
                    </div>
                    <h4 className="radar-card-title">
                      <a href={f.url_original} target="_blank" rel="noreferrer">{f.titulo}</a>
                    </h4>
                    <p className="radar-card-resumen">{f.resumen_ia || f.resumen || 'Sin resumen'}</p>
                    {f.nota_usuario && <div className="radar-nota-preview"><StickyNote size={12}/> {f.nota_usuario}</div>}
                    <div className="radar-card-bottom">
                      {f.prioridad_usuario && <span className={`prio-badge prio-${f.prioridad_usuario.toLowerCase()}`}><PrioIcon size={12}/> {f.prioridad_usuario}</span>}
                      <span style={{fontSize:11,color:'#94a3b8'}}>{RADAR_FUENTE_LABELS[f.fuente]||f.fuente}</span>
                      <a href={f.url_original} target="_blank" rel="noreferrer" className="radar-link-btn"><ExternalLink size={12}/> Fuente</a>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {tab === 'stats' && (
        <div className="radar-stats-section">
          <div className="radar-stats-cards">
            <div className="radar-stat-card"><div className="radar-stat-val">{stats.total||0}</div><div className="radar-stat-label">Total ítems</div></div>
            <div className="radar-stat-card"><div className="radar-stat-val">{stats.nuevos_semana||0}</div><div className="radar-stat-label">Nuevos (7 días)</div></div>
            <div className="radar-stat-card"><div className="radar-stat-val" style={{color:'#d97706'}}>{stats.favoritos||0}</div><div className="radar-stat-label">Favoritos</div></div>
            <div className="radar-stat-card"><div className="radar-stat-val">{stats.no_leidos||0}</div><div className="radar-stat-label">No leídos</div></div>
          </div>
          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 16px'}}><BarChart3 size={16}/> Ítems por categoría</h3>
          <div className="radar-bars">
            {RADAR_CATS.map(c => {
              const n = (stats.por_categoria||{})[c] || 0
              const pct = maxCat > 0 ? (n / maxCat * 100) : 0
              const CIcon = RADAR_CAT_ICONS[c] || FileText
              return (
                <div key={c} className="radar-bar-row">
                  <span className="radar-bar-label"><CIcon size={12}/> {RADAR_CAT_LABELS[c]}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width:`${pct}%`}}></div></div>
                  <span className="radar-bar-val">{n}</span>
                </div>
              )
            })}
          </div>
          {stats.ultimo_scan && <p style={{fontSize:12,color:'#94a3b8',marginTop:16}}>Último escaneo: {new Date(stats.ultimo_scan).toLocaleString('es-ES')}</p>}
        </div>
      )}

      {notaModal && (
        <div className="radar-modal-overlay" onClick={()=>setNotaModal(null)}>
          <div className="radar-modal" onClick={e=>e.stopPropagation()}>
            <h4><StickyNote size={16}/> Nota del farmacéutico</h4>
            <textarea value={notaText} onChange={e=>setNotaText(e.target.value)} rows={4} placeholder="Escribe tu nota aquí..." />
            <div style={{display:'flex',gap:8,justifyContent:'flex-end',marginTop:12}}>
              <button className="radar-modal-cancel" onClick={()=>setNotaModal(null)}>Cancelar</button>
              <button className="radar-modal-save" onClick={saveNota}>Guardar</button>
            </div>
          </div>
        </div>
      )}

      {scanning && (
        <div className="radar-scanning-overlay">
          <div className="radar-scanning-box">
            <RefreshCw size={40} className="radar-spin-icon" />
            <h3>Escaneando fuentes...</h3>
            <p>PubMed, Google News, ClinicalTrials, Semantic Scholar</p>
            <p style={{fontSize:12,color:'#94a3b8'}}>Esto puede tardar 1-2 minutos (enriquecimiento con IA incluido)</p>
          </div>
        </div>
      )}
    </div>
  )
}

/* ═══ Catálogo APIs ═══ */
const BLOQUE_LABELS = {
  IA_GENERATIVA: 'IA Generativa', MEDICAMENTOS: 'Medicamentos', EVIDENCIA: 'Evidencia',
  CODIFICACION: 'Codificación', SEGURIDAD: 'Seguridad', CALCULADORAS: 'Calculadoras', HOSPITAL: 'Hospital'
}
const BLOQUE_ICONS = {
  IA_GENERATIVA: Brain, MEDICAMENTOS: Pill, EVIDENCIA: BookOpen,
  CODIFICACION: Tags, SEGURIDAD: ShieldAlert, CALCULADORAS: Calculator, HOSPITAL: Hospital
}
const API_ESTADO_ICONS = { CONECTADA: CheckCircle2, EN_APEX: Database, PENDIENTE: Clock, FUTURO: Hourglass }
const API_ESTADO_COLORS = { CONECTADA: '#16a34a', EN_APEX: '#2563eb', PENDIENTE: '#ea580c', FUTURO: '#888' }

function CatalogoAPIs() {
  const [apis, setApis] = React.useState([])
  const [favApis, setFavApis] = React.useState([])
  const [stats, setStats] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [filtroBloque, setFiltroBloque] = React.useState('')
  const [filtroEstado, setFiltroEstado] = React.useState('')
  const [filtroPrio, setFiltroPrio] = React.useState('')
  const [filtroFav, setFiltroFav] = React.useState(false)
  const [buscar, setBuscar] = React.useState('')
  const [tab, setTab] = React.useState('catalogo')
  const [testing, setTesting] = React.useState(null)
  const [enriching, setEnriching] = React.useState(null)
  const [notaModal, setNotaModal] = React.useState(null)
  const [notaText, setNotaText] = React.useState('')

  const loadApis = () => {
    let url = '/api/apis/catalogo?'
    if (filtroBloque) url += `bloque=${filtroBloque}&`
    if (filtroEstado) url += `estado=${filtroEstado}&`
    if (filtroPrio) url += `prioridad=${filtroPrio}&`
    if (filtroFav) url += `favorito=true&`
    if (buscar) url += `buscar=${encodeURIComponent(buscar)}&`
    fetch(API + url).then(r => r.json()).then(d => { setApis(d); setLoading(false) }).catch(() => setLoading(false))
  }
  const loadStats = () => { fetch(API + '/api/apis/stats').then(r => r.json()).then(setStats).catch(() => {}) }
  const loadFavs = () => { fetch(API + '/api/apis/favoritos').then(r => r.json()).then(setFavApis).catch(() => {}) }

  React.useEffect(() => { loadApis(); loadStats() }, [filtroBloque, filtroEstado, filtroPrio, filtroFav, buscar])
  React.useEffect(() => { if (tab === 'favoritas') loadFavs() }, [tab])

  const testApi = async (id) => {
    setTesting(id)
    try { await fetch(API + `/api/apis/test/${id}`, { method: 'POST' }); loadApis(); loadStats() } catch {}
    setTesting(null)
  }

  const testAll = async () => {
    setTesting('all')
    try { await fetch(API + '/api/apis/test-all', { method: 'POST' }); loadApis(); loadStats() } catch {}
    setTesting(null)
  }

  const enrichApi = async (id) => {
    setEnriching(id)
    try { const r = await fetch(API + `/api/apis/enrich/${id}`, { method: 'POST' }); if (r.ok) loadApis() } catch {}
    setEnriching(null)
  }

  const toggleFav = async (id) => {
    await fetch(API + '/api/apis/toggle-favorito', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ api_id: id }) })
    loadApis(); loadStats(); if (tab === 'favoritas') loadFavs()
  }

  const setApiPrio = async (id, p) => {
    await fetch(API + '/api/apis/set-prioridad', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ api_id: id, prioridad: p }) })
    if (tab === 'favoritas') loadFavs(); else loadApis()
  }

  const saveNota = async () => {
    if (!notaModal) return
    await fetch(API + '/api/apis/set-nota', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ api_id: notaModal, nota: notaText }) })
    setNotaModal(null); loadApis(); if (tab === 'favoritas') loadFavs()
  }

  return (
    <div className="apis-page">
      <div className="apis-header">
        <div>
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:6}}>
            <Plug size={28} color="#fff" />
            <h1 style={{fontSize:24,fontWeight:800,color:'#fff',margin:0}}>SIGFAR Hub · Catálogo APIs</h1>
            <span className="live-badge"><span className="live-dot"></span>{stats ? stats.total : '...'} APIs</span>
          </div>
          <p style={{fontSize:13,color:'rgba(255,255,255,.7)',margin:0}}>Roadmap de integraciones — APIs gratuitas de salud y farmacia</p>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Conectadas</div>
            <div style={{fontSize:28,fontWeight:800,color:'#4ade80'}}>{stats?.conectadas || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Pendientes</div>
            <div style={{fontSize:28,fontWeight:800}}>{stats?.pendientes || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>En APEX</div>
            <div style={{fontSize:28,fontWeight:800,color:'#93c5fd'}}>{stats?.en_apex || 0}</div>
          </div>
          <button className="apis-btn-test-all" onClick={testAll} disabled={testing==='all'}>
            {testing==='all' ? <><span className="apis-spinner"/> Testeando...</> : <><Zap size={16}/> Probar TODAS</>}
          </button>
        </div>
      </div>

      <div className="radar-tabs">
        <button className={tab==='catalogo'?'active':''} onClick={()=>setTab('catalogo')}><Plug size={14}/> Catálogo</button>
        <button className={tab==='favoritas'?'active':''} onClick={()=>setTab('favoritas')}><Star size={14}/> Mis favoritas ({stats?.favoritos||0})</button>
        <button className={tab==='stats'?'active':''} onClick={()=>setTab('stats')}><BarChart3 size={14}/> Estadísticas</button>
      </div>

      {tab === 'catalogo' && (
        <>
          <div className="radar-filters">
            <Filter size={16} style={{color:'#64748b',flexShrink:0}} />
            <select value={filtroBloque} onChange={e=>setFiltroBloque(e.target.value)}>
              <option value="">Todos los bloques</option>
              {Object.entries(BLOQUE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select value={filtroEstado} onChange={e=>setFiltroEstado(e.target.value)}>
              <option value="">Todos los estados</option>
              <option value="CONECTADA">Conectada</option>
              <option value="EN_APEX">En APEX</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="FUTURO">Futuro</option>
            </select>
            <select value={filtroPrio} onChange={e=>setFiltroPrio(e.target.value)}>
              <option value="">Todas prioridades</option>
              <option value="P1">P1</option><option value="P2">P2</option><option value="P3">P3</option>
            </select>
            <label className="radar-fav-toggle">
              <input type="checkbox" checked={filtroFav} onChange={e=>setFiltroFav(e.target.checked)} />
              <Star size={12}/> Favoritas
            </label>
            <div className="radar-search-wrap">
              <Search size={14} className="radar-search-icon" />
              <input className="radar-search" type="text" placeholder="Buscar API..." value={buscar} onChange={e=>setBuscar(e.target.value)} />
            </div>
          </div>

          {loading ? <p className="apis-loading">Cargando catálogo...</p> : (
            <div className="apis-grid">
              {apis.map(a => {
                const BIcon = BLOQUE_ICONS[a.bloque] || Globe
                const EIcon = API_ESTADO_ICONS[a.estado] || Clock
                const eColor = API_ESTADO_COLORS[a.estado] || '#888'
                return (
                  <div key={a.id} className="api-card">
                    <div className="api-card-top">
                      <div className="api-card-icon" style={{background: eColor + '18', color: eColor}}>
                        <BIcon size={22} />
                      </div>
                      <div style={{flex:1,minWidth:0}}>
                        <h3 className="api-card-name">{a.nombre}</h3>
                        <span className="cat-tag">{BLOQUE_LABELS[a.bloque] || a.bloque}</span>
                      </div>
                      <button className="fav-btn" onClick={()=>toggleFav(a.id)}>
                        <Star size={16} fill={a.favorito ? 'currentColor' : 'none'} color={a.favorito ? '#f59e0b' : '#94a3b8'} />
                      </button>
                    </div>

                    <div className="api-card-badges">
                      <span className="api-estado-badge" style={{color: eColor, borderColor: eColor}}>
                        <EIcon size={12}/> {a.estado.replace('_',' ')}
                      </span>
                      {a.prioridad && <span className={`apis-prio apis-prio-${a.prioridad.toLowerCase()}`}>{a.prioridad}</span>}
                      {a.ultimo_test_ok !== null && (
                        <span className={a.ultimo_test_ok ? 'test-ok' : 'test-fail'}>
                          {a.ultimo_test_ok ? <><CheckCircle2 size={12}/> {a.ultimo_test_latencia_ms}ms</> : <><XCircle size={12}/> FAIL</>}
                        </span>
                      )}
                    </div>

                    <p className="api-card-desc">{a.descripcion}</p>

                    {a.donde_integrada && <div className="api-integrada"><Database size={11}/> {a.donde_integrada}</div>}
                    {a.limite_gratis && <div className="api-limite"><Info size={11}/> {a.limite_gratis}</div>}
                    {a.caso_uso && <div className="api-caso-uso">{a.caso_uso}</div>}

                    {a.propuesta_ia && (
                      <div className="apis-propuesta">
                        <strong><Brain size={14}/> Propuesta IA:</strong>
                        <p>{a.propuesta_ia}</p>
                      </div>
                    )}

                    <div className="api-card-actions">
                      <button onClick={()=>testApi(a.id)} disabled={testing===a.id} title="Probar conectividad">
                        {testing===a.id ? <><span className="apis-spinner"/> Probando...</> : <><Zap size={14}/> Probar</>}
                      </button>
                      <button onClick={()=>enrichApi(a.id)} disabled={enriching===a.id} title="Generar propuesta IA">
                        {enriching===a.id ? <><span className="apis-spinner"/> Generando...</> : <><Brain size={14}/> Propuesta IA</>}
                      </button>
                      <button onClick={()=>{setNotaModal(a.id);setNotaText(a.nota_usuario||'')}} title="Nota">
                        <StickyNote size={14}/>
                      </button>
                      {a.url_docs && <a href={a.url_docs} target="_blank" rel="noreferrer" className="api-docs-link"><ExternalLink size={12}/> Docs</a>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}

      {tab === 'favoritas' && (
        <div className="apis-favs-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Star size={18} color="#f59e0b"/> Mis APIs favoritas — Backlog de integraciones ({favApis.length})</h3>
          {favApis.length === 0 ? <p style={{color:'#64748b'}}>No hay APIs favoritas. Marca APIs con <Star size={12}/> para organizar tu backlog aquí.</p> : (
            <div className="apis-grid">
              {favApis.map(a => {
                const BIcon = BLOQUE_ICONS[a.bloque] || Globe
                const EIcon = API_ESTADO_ICONS[a.estado] || Clock
                const eColor = API_ESTADO_COLORS[a.estado] || '#888'
                const PrioIcon = a.prioridad_usuario === 'ALTA' ? AlertTriangle : a.prioridad_usuario === 'MEDIA' ? AlertCircle : Info
                return (
                  <div key={a.id} className="api-card">
                    <div className="api-card-top">
                      <div className="api-card-icon" style={{background: eColor + '18', color: eColor}}>
                        <BIcon size={22} />
                      </div>
                      <div style={{flex:1,minWidth:0}}>
                        <h3 className="api-card-name">{a.nombre}</h3>
                        <span className="cat-tag">{BLOQUE_LABELS[a.bloque]}</span>
                      </div>
                      <button className="fav-btn" onClick={()=>toggleFav(a.id)}>
                        <Star size={16} fill="currentColor" color="#f59e0b" />
                      </button>
                    </div>
                    <div className="api-card-badges">
                      <span className="api-estado-badge" style={{color: eColor, borderColor: eColor}}><EIcon size={12}/> {a.estado.replace('_',' ')}</span>
                      {a.prioridad && <span className={`apis-prio apis-prio-${a.prioridad.toLowerCase()}`}>{a.prioridad}</span>}
                      <select value={a.prioridad_usuario||''} onChange={e=>setApiPrio(a.id,e.target.value)} className="radar-prio-select">
                        <option value="">Mi prioridad...</option>
                        <option value="ALTA">Alta</option>
                        <option value="MEDIA">Media</option>
                        <option value="BAJA">Baja</option>
                      </select>
                      {a.ultimo_test_ok !== null && (
                        <span className={a.ultimo_test_ok ? 'test-ok' : 'test-fail'}>
                          {a.ultimo_test_ok ? <><CheckCircle2 size={12}/> {a.ultimo_test_latencia_ms}ms</> : <><XCircle size={12}/> FAIL</>}
                        </span>
                      )}
                    </div>
                    <p className="api-card-desc">{a.descripcion}</p>
                    {a.prioridad_usuario && <span className={`prio-badge prio-${a.prioridad_usuario.toLowerCase()}`}><PrioIcon size={12}/> {a.prioridad_usuario}</span>}
                    {a.nota_usuario && <div className="radar-nota-preview"><StickyNote size={12}/> {a.nota_usuario}</div>}
                    <div className="api-card-actions">
                      <button onClick={()=>testApi(a.id)} disabled={testing===a.id}><Zap size={14}/> Probar</button>
                      <button onClick={()=>{setNotaModal(a.id);setNotaText(a.nota_usuario||'')}}><StickyNote size={14}/> Nota</button>
                      {a.url_docs && <a href={a.url_docs} target="_blank" rel="noreferrer" className="api-docs-link"><ExternalLink size={12}/> Docs</a>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {tab === 'stats' && stats && (
        <div className="radar-stats-section">
          <div className="apis-stats-cards">
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.total}</span><span>Total APIs</span></div>
            <div className="apis-stat-card conectada"><span className="apis-stat-num">{stats.conectadas}</span><span>Conectadas</span></div>
            <div className="apis-stat-card apex"><span className="apis-stat-num">{stats.en_apex}</span><span>En APEX</span></div>
            <div className="apis-stat-card pendiente"><span className="apis-stat-num">{stats.pendientes}</span><span>Pendientes</span></div>
            <div className="apis-stat-card futuro"><span className="apis-stat-num">{stats.futuro}</span><span>Futuro</span></div>
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.test_ok}</span><span>Test OK</span></div>
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}><BarChart3 size={16}/> Por bloque</h3>
          <div className="radar-bars">
            {stats.por_bloque && Object.entries(stats.por_bloque).map(([k,v]) => {
              const pct = stats.total ? Math.round(v/stats.total*100) : 0
              const BIcon = BLOQUE_ICONS[k] || Globe
              return (
                <div key={k} className="radar-bar-row">
                  <span className="radar-bar-label"><BIcon size={12}/> {BLOQUE_LABELS[k] || k}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%'}}/></div>
                  <span className="radar-bar-val">{v}</span>
                </div>
              )
            })}
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}>Por prioridad</h3>
          <div className="radar-bars">
            {stats.por_prioridad && Object.entries(stats.por_prioridad).map(([k,v]) => {
              const pct = stats.total ? Math.round(v/stats.total*100) : 0
              const colors = { P1: '#ef4444', P2: '#f59e0b', P3: '#22c55e' }
              return (
                <div key={k} className="radar-bar-row">
                  <span className="radar-bar-label">{k}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: colors[k]}}/></div>
                  <span className="radar-bar-val">{v}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {notaModal && (
        <div className="radar-modal-overlay" onClick={()=>setNotaModal(null)}>
          <div className="radar-modal" onClick={e=>e.stopPropagation()}>
            <h4><StickyNote size={16}/> Nota</h4>
            <textarea value={notaText} onChange={e=>setNotaText(e.target.value)} rows={4} placeholder="Escribe tu nota aquí..." />
            <div style={{display:'flex',gap:8,justifyContent:'flex-end',marginTop:12}}>
              <button className="radar-modal-cancel" onClick={()=>setNotaModal(null)}>Cancelar</button>
              <button className="radar-modal-save" onClick={saveNota}>Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* ═══ Algoritmos ML — Lookup maps ═══ */
const ML_CAT_LABELS = {
  VALIDACION: 'Validación', FARMACOCINETICA: 'Farmacocinética', NUTRICION: 'Nutrición',
  PROA: 'PROA', ELABORACION: 'Elaboración', STOCK_LOGISTICA: 'Stock/Logística',
  ROBOTICA: 'Robótica', FARMACOECONOMIA: 'Farmacoeconomía', CUADRO_MANDOS: 'Cuadro Mandos',
  REGULACION: 'Regulación'
}
const ML_CAT_ICONS = {
  VALIDACION: ShieldAlert, FARMACOCINETICA: FlaskConical, NUTRICION: Heart,
  PROA: Shield, ELABORACION: Layers, STOCK_LOGISTICA: Database,
  ROBOTICA: Cpu, FARMACOECONOMIA: Wallet, CUADRO_MANDOS: BarChart3,
  REGULACION: FileText
}
const ML_CAT_COLORS = {
  VALIDACION: '#ef4444', FARMACOCINETICA: '#8b5cf6', NUTRICION: '#22c55e',
  PROA: '#f59e0b', ELABORACION: '#06b6d4', STOCK_LOGISTICA: '#3b82f6',
  ROBOTICA: '#ec4899', FARMACOECONOMIA: '#14b8a6', CUADRO_MANDOS: '#6366f1',
  REGULACION: '#64748b'
}
const ML_TIPO_LABELS = {
  SUPERVISADO: 'Supervisado', NO_SUPERVISADO: 'No supervisado', DEEP_LEARNING: 'Deep Learning',
  NLP: 'NLP', BAYESIANO: 'Bayesiano', SERIES_TEMPORALES: 'Series temporales',
  REFUERZO: 'Refuerzo'
}
const ML_TIPO_COLORS = {
  SUPERVISADO: '#3b82f6', NO_SUPERVISADO: '#8b5cf6', DEEP_LEARNING: '#ec4899',
  NLP: '#06b6d4', BAYESIANO: '#f59e0b', SERIES_TEMPORALES: '#22c55e',
  REFUERZO: '#ef4444'
}
const ML_COMP_COLORS = { BAJA: '#22c55e', MEDIA: '#f59e0b', ALTA: '#ef4444', MUY_ALTA: '#dc2626' }
const ML_ESTADO_ICONS = { IMPLEMENTADO: CheckCircle2, EN_DESARROLLO: RefreshCw, NO_IMPLEMENTADO: Clock }
const ML_ESTADO_COLORS = { IMPLEMENTADO: '#16a34a', EN_DESARROLLO: '#f59e0b', NO_IMPLEMENTADO: '#94a3b8' }

/* ═══ AlgoritmosML ═══ */
function AlgoritmosML() {
  const [algos, setAlgos] = React.useState([])
  const [favs, setFavs] = React.useState([])
  const [stats, setStats] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [filtroCat, setFiltroCat] = React.useState('')
  const [filtroTipo, setFiltroTipo] = React.useState('')
  const [filtroEstado, setFiltroEstado] = React.useState('')
  const [filtroComp, setFiltroComp] = React.useState('')
  const [buscar, setBuscar] = React.useState('')
  const [tab, setTab] = React.useState('catalogo')
  const [enriching, setEnriching] = React.useState(null)
  const [notaModal, setNotaModal] = React.useState(null)
  const [notaText, setNotaText] = React.useState('')

  const loadAlgos = () => {
    let url = '/api/ml/algoritmos?'
    if (filtroCat) url += `categoria=${filtroCat}&`
    if (filtroTipo) url += `tipo=${filtroTipo}&`
    if (filtroEstado) url += `estado=${filtroEstado}&`
    if (filtroComp) url += `complejidad=${filtroComp}&`
    if (buscar) url += `q=${encodeURIComponent(buscar)}&`
    fetch(API + url).then(r => r.json()).then(d => { setAlgos(d); setLoading(false) }).catch(() => setLoading(false))
  }
  const loadStats = () => { fetch(API + '/api/ml/stats').then(r => r.json()).then(setStats).catch(() => {}) }
  const loadFavs = () => { fetch(API + '/api/ml/favoritos').then(r => r.json()).then(setFavs).catch(() => {}) }

  React.useEffect(() => { loadAlgos(); loadStats() }, [filtroCat, filtroTipo, filtroEstado, filtroComp, buscar])
  React.useEffect(() => { if (tab === 'favoritos') loadFavs() }, [tab])

  const enrichAlgo = async (id) => {
    setEnriching(id)
    try { const r = await fetch(API + `/api/ml/enrich/${id}`, { method: 'POST' }); if (r.ok) loadAlgos() } catch {}
    setEnriching(null)
  }

  const toggleFav = async (id) => {
    await fetch(API + '/api/ml/toggle-favorito', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ algoritmo_id: id }) })
    loadAlgos(); loadStats(); if (tab === 'favoritos') loadFavs()
  }

  const setAlgoPrio = async (id, p) => {
    await fetch(API + '/api/ml/set-prioridad', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ algoritmo_id: id, prioridad: p }) })
    if (tab === 'favoritos') loadFavs(); else loadAlgos()
  }

  const saveNota = async () => {
    if (!notaModal) return
    await fetch(API + '/api/ml/set-nota', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ algoritmo_id: notaModal, nota: notaText }) })
    setNotaModal(null); loadAlgos(); if (tab === 'favoritos') loadFavs()
  }

  const renderCard = (a, showPrio = false) => {
    const CIcon = ML_CAT_ICONS[a.categoria_farmacia] || Brain
    const catColor = ML_CAT_COLORS[a.categoria_farmacia] || '#888'
    const EIcon = ML_ESTADO_ICONS[a.estado_sigfar_hub] || Clock
    const eColor = ML_ESTADO_COLORS[a.estado_sigfar_hub] || '#888'
    const compColor = ML_COMP_COLORS[a.complejidad] || '#888'
    const tipoColor = ML_TIPO_COLORS[a.tipo_ml] || '#888'
    return (
      <div key={a.id} className="ml-card">
        <div className="api-card-top">
          <div className="api-card-icon" style={{background: catColor + '18', color: catColor}}>
            <CIcon size={22} />
          </div>
          <div style={{flex:1,minWidth:0}}>
            <h3 className="api-card-name">{a.nombre}</h3>
            <span className="cat-tag" style={{borderColor: catColor, color: catColor}}>{ML_CAT_LABELS[a.categoria_farmacia] || a.categoria_farmacia}</span>
          </div>
          <button className="fav-btn" onClick={()=>toggleFav(a.id)}>
            <Star size={16} fill={a.favorito ? 'currentColor' : 'none'} color={a.favorito ? '#f59e0b' : '#94a3b8'} />
          </button>
        </div>

        <div className="api-card-badges">
          <span className="api-estado-badge" style={{color: eColor, borderColor: eColor}}>
            <EIcon size={12}/> {a.estado_sigfar_hub.replace(/_/g,' ')}
          </span>
          <span className="ml-tipo-badge" style={{color: tipoColor, borderColor: tipoColor}}>
            <BrainCircuit size={12}/> {ML_TIPO_LABELS[a.tipo_ml] || a.tipo_ml}
          </span>
          <span className="ml-comp-badge" style={{color: compColor, borderColor: compColor}}>
            <Gauge size={12}/> {a.complejidad.replace('_',' ')}
          </span>
        </div>

        <p className="api-card-desc">{a.descripcion}</p>

        {a.caso_uso && <div className="ml-caso-uso"><Target size={11}/> {a.caso_uso}</div>}
        {a.librerias_python && <div className="ml-librerias"><Cpu size={11}/> {a.librerias_python}</div>}
        {a.modulo_sigfar && <div className="ml-modulo"><GitBranch size={11}/> Módulo: {a.modulo_sigfar}</div>}

        {a.propuesta_ia && (
          <div className="apis-propuesta">
            <strong><Brain size={14}/> Propuesta IA:</strong>
            <p>{a.propuesta_ia}</p>
          </div>
        )}

        {showPrio && (
          <div className="ml-fav-prio">
            <select value={a.prioridad_usuario||''} onChange={e=>setAlgoPrio(a.id,e.target.value)} className="radar-prio-select">
              <option value="">Mi prioridad...</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>
            {a.prioridad_usuario && (
              <span className={`prio-badge prio-${a.prioridad_usuario.toLowerCase()}`}>
                {a.prioridad_usuario === 'ALTA' ? <AlertTriangle size={12}/> : a.prioridad_usuario === 'MEDIA' ? <AlertCircle size={12}/> : <Info size={12}/>} {a.prioridad_usuario}
              </span>
            )}
          </div>
        )}
        {showPrio && a.nota_usuario && <div className="radar-nota-preview"><StickyNote size={12}/> {a.nota_usuario}</div>}

        <div className="api-card-actions">
          <button onClick={()=>enrichAlgo(a.id)} disabled={enriching===a.id} title="Generar propuesta IA">
            {enriching===a.id ? <><span className="apis-spinner"/> Generando...</> : <><Brain size={14}/> Propuesta IA</>}
          </button>
          <button onClick={()=>{setNotaModal(a.id);setNotaText(a.nota_usuario||'')}} title="Nota">
            <StickyNote size={14}/>
          </button>
          {a.paper_referencia && <a href={a.paper_referencia} target="_blank" rel="noreferrer" className="api-docs-link"><ExternalLink size={12}/> Paper</a>}
        </div>
      </div>
    )
  }

  return (
    <div className="ml-page">
      <div className="ml-header">
        <div>
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:6}}>
            <BrainCircuit size={28} color="#fff" />
            <h1 style={{fontSize:24,fontWeight:800,color:'#fff',margin:0}}>SIGFAR Hub · Algoritmos ML</h1>
            <span className="live-badge"><span className="live-dot"></span>{stats ? stats.total : '...'} Algoritmos</span>
          </div>
          <p style={{fontSize:13,color:'rgba(255,255,255,.7)',margin:0}}>Catálogo de algoritmos de Machine Learning para farmacia hospitalaria</p>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Implementados</div>
            <div style={{fontSize:28,fontWeight:800,color:'#4ade80'}}>{stats?.implementados || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Categorías</div>
            <div style={{fontSize:28,fontWeight:800}}>{stats?.categorias || 0}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Tipos ML</div>
            <div style={{fontSize:28,fontWeight:800,color:'#93c5fd'}}>{stats?.tipos_ml || 0}</div>
          </div>
        </div>
      </div>

      <div className="radar-tabs">
        <button className={tab==='catalogo'?'active':''} onClick={()=>setTab('catalogo')}><BrainCircuit size={14}/> Catálogo</button>
        <button className={tab==='favoritos'?'active':''} onClick={()=>setTab('favoritos')}><Star size={14}/> Mis favoritos ({stats?.favoritos||0})</button>
        <button className={tab==='stats'?'active':''} onClick={()=>setTab('stats')}><BarChart3 size={14}/> Estadísticas</button>
        <button className={tab==='mapa'?'active':''} onClick={()=>setTab('mapa')}><Layers size={14}/> Mapa implementación</button>
      </div>

      {tab === 'catalogo' && (
        <>
          <div className="radar-filters">
            <Filter size={16} style={{color:'#64748b',flexShrink:0}} />
            <select value={filtroCat} onChange={e=>setFiltroCat(e.target.value)}>
              <option value="">Todas las categorías</option>
              {Object.entries(ML_CAT_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select value={filtroTipo} onChange={e=>setFiltroTipo(e.target.value)}>
              <option value="">Todos los tipos</option>
              {Object.entries(ML_TIPO_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select value={filtroEstado} onChange={e=>setFiltroEstado(e.target.value)}>
              <option value="">Todos los estados</option>
              <option value="IMPLEMENTADO">Implementado</option>
              <option value="EN_DESARROLLO">En desarrollo</option>
              <option value="NO_IMPLEMENTADO">No implementado</option>
            </select>
            <select value={filtroComp} onChange={e=>setFiltroComp(e.target.value)}>
              <option value="">Toda complejidad</option>
              <option value="BAJA">Baja</option>
              <option value="MEDIA">Media</option>
              <option value="ALTA">Alta</option>
              <option value="MUY_ALTA">Muy alta</option>
            </select>
            <div className="radar-search-wrap">
              <Search size={14} className="radar-search-icon" />
              <input className="radar-search" type="text" placeholder="Buscar algoritmo..." value={buscar} onChange={e=>setBuscar(e.target.value)} />
            </div>
          </div>

          {loading ? <p className="apis-loading">Cargando catálogo...</p> : (
            <div className="ml-grid">
              {algos.map(a => renderCard(a))}
            </div>
          )}
        </>
      )}

      {tab === 'favoritos' && (
        <div className="apis-favs-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Star size={18} color="#f59e0b"/> Mis algoritmos favoritos — Roadmap de implementación ({favs.length})</h3>
          {favs.length === 0 ? <p style={{color:'#64748b'}}>No hay algoritmos favoritos. Marca algoritmos con <Star size={12}/> para organizar tu roadmap aquí.</p> : (
            <div className="ml-grid">
              {favs.map(a => renderCard(a, true))}
            </div>
          )}
        </div>
      )}

      {tab === 'stats' && stats && (
        <div className="radar-stats-section">
          <div className="apis-stats-cards">
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.total}</span><span>Total</span></div>
            <div className="apis-stat-card conectada"><span className="apis-stat-num">{stats.implementados}</span><span>Implementados</span></div>
            <div className="apis-stat-card pendiente"><span className="apis-stat-num">{stats.no_implementados}</span><span>No implementados</span></div>
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.favoritos}</span><span>Favoritos</span></div>
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}><BarChart3 size={16}/> Por categoría farmacéutica</h3>
          <div className="radar-bars">
            {stats.por_categoria && stats.por_categoria.map(c => {
              const pct = stats.total ? Math.round(c.n/stats.total*100) : 0
              const CIcon = ML_CAT_ICONS[c.categoria_farmacia] || Brain
              const color = ML_CAT_COLORS[c.categoria_farmacia] || '#888'
              return (
                <div key={c.categoria_farmacia} className="radar-bar-row">
                  <span className="radar-bar-label"><CIcon size={12}/> {ML_CAT_LABELS[c.categoria_farmacia] || c.categoria_farmacia}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: color}}/></div>
                  <span className="radar-bar-val">{c.n}</span>
                </div>
              )
            })}
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}><BrainCircuit size={16}/> Por tipo de ML</h3>
          <div className="radar-bars">
            {stats.por_tipo && stats.por_tipo.map(t => {
              const pct = stats.total ? Math.round(t.n/stats.total*100) : 0
              const color = ML_TIPO_COLORS[t.tipo_ml] || '#888'
              return (
                <div key={t.tipo_ml} className="radar-bar-row">
                  <span className="radar-bar-label">{ML_TIPO_LABELS[t.tipo_ml] || t.tipo_ml}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: color}}/></div>
                  <span className="radar-bar-val">{t.n}</span>
                </div>
              )
            })}
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}><Gauge size={16}/> Por complejidad</h3>
          <div className="radar-bars">
            {stats.por_complejidad && stats.por_complejidad.map(c => {
              const pct = stats.total ? Math.round(c.n/stats.total*100) : 0
              const color = ML_COMP_COLORS[c.complejidad] || '#888'
              return (
                <div key={c.complejidad} className="radar-bar-row">
                  <span className="radar-bar-label">{c.complejidad.replace('_',' ')}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: color}}/></div>
                  <span className="radar-bar-val">{c.n}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {tab === 'mapa' && (
        <div className="ml-mapa-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Layers size={18}/> Mapa de implementación por categoría</h3>
          {Object.entries(ML_CAT_LABELS).map(([cat, label]) => {
            const catAlgos = algos.filter(a => a.categoria_farmacia === cat)
            if (catAlgos.length === 0) return null
            const CIcon = ML_CAT_ICONS[cat] || Brain
            const color = ML_CAT_COLORS[cat] || '#888'
            const impl = catAlgos.filter(a => a.estado_sigfar_hub === 'IMPLEMENTADO').length
            return (
              <div key={cat} className="ml-mapa-cat">
                <div className="ml-mapa-cat-header" style={{borderLeftColor: color}}>
                  <CIcon size={18} color={color}/>
                  <span style={{fontWeight:700}}>{label}</span>
                  <span style={{fontSize:12,color:'#64748b'}}>({impl}/{catAlgos.length} implementados)</span>
                </div>
                <div className="ml-mapa-algos">
                  {catAlgos.map(a => {
                    const eColor = ML_ESTADO_COLORS[a.estado_sigfar_hub] || '#888'
                    const compColor = ML_COMP_COLORS[a.complejidad] || '#888'
                    return (
                      <div key={a.id} className="ml-mapa-algo" style={{borderLeftColor: eColor}}>
                        <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:4}}>
                          <span style={{fontWeight:600,fontSize:13}}>{a.nombre}</span>
                          <span className="ml-comp-badge" style={{color: compColor, borderColor: compColor, fontSize:10, padding:'1px 6px'}}>
                            {a.complejidad.replace('_',' ')}
                          </span>
                        </div>
                        <div style={{fontSize:12,color:'#64748b'}}>{a.nombre_tecnico} — {ML_TIPO_LABELS[a.tipo_ml]}</div>
                        {a.estado_sigfar_hub === 'IMPLEMENTADO' && <span style={{fontSize:11,color:'#16a34a',fontWeight:600}}><CheckCircle2 size={11}/> Implementado</span>}
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {notaModal && (
        <div className="radar-modal-overlay" onClick={()=>setNotaModal(null)}>
          <div className="radar-modal" onClick={e=>e.stopPropagation()}>
            <h4><StickyNote size={16}/> Nota</h4>
            <textarea value={notaText} onChange={e=>setNotaText(e.target.value)} rows={4} placeholder="Escribe tu nota aquí..." />
            <div style={{display:'flex',gap:8,justifyContent:'flex-end',marginTop:12}}>
              <button className="radar-modal-cancel" onClick={()=>setNotaModal(null)}>Cancelar</button>
              <button className="radar-modal-save" onClick={saveNota}>Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* ═══ Propuestas Estratégicas — Lookup maps ═══ */
const PROP_EJE_LABELS = {
  CLINICO: 'Clínico', ECONOMICO: 'Económico', LOGISTICO: 'Logístico',
  TECNICO: 'Técnico', DIRECTIVO: 'Directivo', FORMACION: 'Formación'
}
const PROP_EJE_ICONS = {
  CLINICO: HeartPulse, ECONOMICO: TrendingDown, LOGISTICO: Truck,
  TECNICO: Wrench, DIRECTIVO: Presentation, FORMACION: GraduationCap
}
const PROP_EJE_COLORS = {
  CLINICO: '#ef4444', ECONOMICO: '#f59e0b', LOGISTICO: '#3b82f6',
  TECNICO: '#8b5cf6', DIRECTIVO: '#06b6d4', FORMACION: '#10b981'
}
const PROP_ESTADO_LABELS = {
  PROPUESTA: 'Propuesta', EN_ANALISIS: 'En análisis', EN_DESARROLLO: 'En desarrollo',
  PILOTO: 'Piloto', PRODUCCION: 'Producción', DESCARTADA: 'Descartada', GENERADA_IA: 'Generada IA'
}
const PROP_ESTADO_ICONS = {
  PROPUESTA: Circle, EN_ANALISIS: Search, EN_DESARROLLO: Wrench,
  PILOTO: FlaskConical, PRODUCCION: Rocket, DESCARTADA: X, GENERADA_IA: Sparkles
}
const PROP_ESTADO_COLORS = {
  PROPUESTA: '#94a3b8', EN_ANALISIS: '#2563eb', EN_DESARROLLO: '#ea580c',
  PILOTO: '#7c3aed', PRODUCCION: '#16a34a', DESCARTADA: '#dc2626', GENERADA_IA: '#d97706'
}
const PROP_IMPACTO_COLORS = { MUY_ALTO: '#dc2626', ALTO: '#ea580c', MEDIO: '#d97706', BAJO: '#94a3b8' }

/* ═══ PropuestasEstrategicas ═══ */
function PropuestasEstrategicas() {
  const [props, setProps] = React.useState([])
  const [favs, setFavs] = React.useState([])
  const [stats, setStats] = React.useState(null)
  const [matriz, setMatriz] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [filtroEje, setFiltroEje] = React.useState('')
  const [filtroEstado, setFiltroEstado] = React.useState('')
  const [filtroImpacto, setFiltroImpacto] = React.useState('')
  const [filtroOrigen, setFiltroOrigen] = React.useState('')
  const [buscar, setBuscar] = React.useState('')
  const [tab, setTab] = React.useState('catalogo')
  const [generating, setGenerating] = React.useState(false)
  const [enriching, setEnriching] = React.useState(null)
  const [notaModal, setNotaModal] = React.useState(null)
  const [notaText, setNotaText] = React.useState('')
  const [expandedHub, setExpandedHub] = React.useState({})
  const [expandedPlan, setExpandedPlan] = React.useState({})

  const loadProps = () => {
    let url = '/api/propuestas?'
    if (filtroEje) url += `eje=${filtroEje}&`
    if (filtroEstado) url += `estado=${filtroEstado}&`
    if (filtroImpacto) url += `impacto=${filtroImpacto}&`
    if (filtroOrigen) url += `origen=${filtroOrigen}&`
    if (buscar) url += `buscar=${encodeURIComponent(buscar)}&`
    fetch(API + url).then(r => r.json()).then(d => { setProps(d); setLoading(false) }).catch(() => setLoading(false))
  }
  const loadStats = () => { fetch(API + '/api/propuestas/stats').then(r => r.json()).then(setStats).catch(() => {}) }
  const loadFavs = () => { fetch(API + '/api/propuestas/favoritos').then(r => r.json()).then(setFavs).catch(() => {}) }
  const loadMatriz = () => { fetch(API + '/api/propuestas/matriz').then(r => r.json()).then(setMatriz).catch(() => {}) }

  React.useEffect(() => { loadProps(); loadStats() }, [filtroEje, filtroEstado, filtroImpacto, filtroOrigen, buscar])
  React.useEffect(() => { if (tab === 'favoritos') loadFavs(); if (tab === 'matriz') loadMatriz() }, [tab])

  const generar = async () => {
    setGenerating(true)
    try { await fetch(API + '/api/propuestas/generar', { method: 'POST' }); loadProps(); loadStats() } catch {}
    setGenerating(false)
  }

  const analizar = async (id) => {
    setEnriching(id)
    try { await fetch(API + `/api/propuestas/analizar/${id}`, { method: 'POST' }); loadProps() } catch {}
    setEnriching(null)
  }

  const toggleFav = async (id) => {
    await fetch(API + '/api/propuestas/toggle-favorito', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ propuesta_id: id }) })
    loadProps(); loadStats(); if (tab === 'favoritos') loadFavs()
  }

  const cambiarEstado = async (id, estado) => {
    await fetch(API + '/api/propuestas/cambiar-estado', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id, estado }) })
    loadProps(); loadStats()
  }

  const setPrio = async (id, p) => {
    await fetch(API + '/api/propuestas/set-prioridad', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ propuesta_id: id, prioridad: p }) })
    if (tab === 'favoritos') loadFavs(); else loadProps()
  }

  const saveNota = async () => {
    if (!notaModal) return
    await fetch(API + '/api/propuestas/set-nota', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ propuesta_id: notaModal, nota: notaText }) })
    setNotaModal(null); loadProps(); if (tab === 'favoritos') loadFavs()
  }

  const renderCard = (p, showPrio = false) => {
    const EjeIcon = PROP_EJE_ICONS[p.eje] || Lightbulb
    const ejeColor = PROP_EJE_COLORS[p.eje] || '#888'
    const EstIcon = PROP_ESTADO_ICONS[p.estado] || Circle
    const estColor = PROP_ESTADO_COLORS[p.estado] || '#888'
    const impColor = PROP_IMPACTO_COLORS[p.impacto] || '#888'
    return (
      <div key={p.id} className={`propuesta-card eje-${p.eje.toLowerCase()}`}>
        <div className="api-card-top">
          <div className="api-card-icon" style={{background: ejeColor + '18', color: ejeColor}}>
            <EjeIcon size={22} />
          </div>
          <div style={{flex:1,minWidth:0}}>
            <h3 className="api-card-name">{p.titulo}</h3>
            <span className="cat-tag" style={{background: ejeColor}}>{PROP_EJE_LABELS[p.eje]}</span>
          </div>
          <button className="fav-btn" onClick={()=>toggleFav(p.id)}>
            <Star size={16} fill={p.favorito ? 'currentColor' : 'none'} color={p.favorito ? '#f59e0b' : '#94a3b8'} />
          </button>
        </div>

        <div className="api-card-badges">
          <span className="api-estado-badge" style={{color: estColor, borderColor: estColor}}>
            <EstIcon size={12}/> {PROP_ESTADO_LABELS[p.estado]}
          </span>
          <span className="ml-comp-badge" style={{color: impColor, borderColor: impColor}}>
            <TrendingUp size={12}/> {p.impacto.replace('_',' ')}
          </span>
          {p.origen === 'GENERADA_IA' && <span className="prop-origen-ia"><Sparkles size={12}/> Generada IA</span>}
          {p.origen === 'RADAR' && <span className="prop-origen-radar"><Radar size={12}/> Desde Radar</span>}
          {p.tiempo_estimado && <span style={{fontSize:11,color:'#64748b'}}><Clock size={11}/> {p.tiempo_estimado}</span>}
        </div>

        <p className="api-card-desc">{p.descripcion}</p>

        {p.preview_descripcion && (
          <div className="prop-preview"><code>{p.preview_descripcion}</code></div>
        )}

        {p.por_que_hub && (
          <div className="prop-collapse">
            <button className="prop-collapse-btn" onClick={()=>setExpandedHub(prev=>({...prev,[p.id]:!prev[p.id]}))}>
              <ChevronRight size={14} style={{transform: expandedHub[p.id] ? 'rotate(90deg)' : 'none', transition:'.2s'}}/> Por qué Hub y no APEX
            </button>
            {expandedHub[p.id] && <div className="prop-collapse-content">{p.por_que_hub}</div>}
          </div>
        )}

        {p.apis_necesarias && (
          <div className="prop-links"><Plug size={11}/> {p.apis_necesarias.split(',').map((a,i) =>
            <Link key={i} to={`/apis?buscar=${encodeURIComponent(a.trim())}`} className="prop-link-badge">{a.trim()}</Link>
          )}</div>
        )}
        {p.ml_recomendado && (
          <div className="prop-links"><BrainCircuit size={11}/> {p.ml_recomendado.split(',').map((m,i) =>
            <Link key={i} to={`/ml?buscar=${encodeURIComponent(m.trim())}`} className="prop-link-badge prop-link-ml">{m.trim()}</Link>
          )}</div>
        )}
        {p.datos_cruza && (
          <div className="prop-datos"><Database size={11}/> {p.datos_cruza}</div>
        )}
        {p.demo_target && (
          <div style={{fontSize:11,color:'#64748b'}}><Target size={11}/> Demo: {p.demo_target}</div>
        )}

        {p.propuesta_ia && (
          <div className="prop-collapse">
            <button className="prop-collapse-btn" onClick={()=>setExpandedPlan(prev=>({...prev,[p.id]:!prev[p.id]}))}>
              <ChevronRight size={14} style={{transform: expandedPlan[p.id] ? 'rotate(90deg)' : 'none', transition:'.2s'}}/> Plan detallado IA
            </button>
            {expandedPlan[p.id] && <div className="apis-propuesta"><p>{p.propuesta_ia}</p></div>}
          </div>
        )}

        {showPrio && (
          <div className="ml-fav-prio">
            <select value={p.prioridad_usuario||''} onChange={e=>setPrio(p.id,e.target.value)} className="radar-prio-select">
              <option value="">Mi prioridad...</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>
            {p.prioridad_usuario && (
              <span className={`prio-badge prio-${p.prioridad_usuario.toLowerCase()}`}>
                {p.prioridad_usuario === 'ALTA' ? <AlertTriangle size={12}/> : p.prioridad_usuario === 'MEDIA' ? <AlertCircle size={12}/> : <Info size={12}/>} {p.prioridad_usuario}
              </span>
            )}
          </div>
        )}
        {showPrio && p.nota_usuario && <div className="radar-nota-preview"><StickyNote size={12}/> {p.nota_usuario}</div>}

        <div className="api-card-actions">
          <select value={p.estado} onChange={e=>cambiarEstado(p.id,e.target.value)} className="prop-estado-select">
            <option value="PROPUESTA">Propuesta</option>
            <option value="EN_ANALISIS">En análisis</option>
            <option value="EN_DESARROLLO">En desarrollo</option>
            <option value="PILOTO">Piloto</option>
            <option value="PRODUCCION">Producción</option>
            <option value="DESCARTADA">Descartada</option>
          </select>
          <button onClick={()=>analizar(p.id)} disabled={enriching===p.id} title="Analizar con IA">
            {enriching===p.id ? <><span className="apis-spinner"/> Analizando...</> : <><Sparkles size={14}/> Analizar IA</>}
          </button>
          <button onClick={()=>{setNotaModal(p.id);setNotaText(p.nota_usuario||'')}} title="Nota">
            <StickyNote size={14}/>
          </button>
        </div>
      </div>
    )
  }

  const matrizRef = React.useRef(null)
  const [hovered, setHovered] = React.useState(null)

  return (
    <div className="propuestas-page">
      <div className="propuestas-header">
        <div>
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:6}}>
            <Lightbulb size={28} color="#fff" />
            <h1 style={{fontSize:24,fontWeight:800,color:'#fff',margin:0}}>SIGFAR Hub · Propuestas Estratégicas</h1>
            <span className="live-badge"><span className="live-dot"></span>{stats ? stats.total : '...'} Propuestas</span>
          </div>
          <p style={{fontSize:13,color:'rgba(255,255,255,.7)',margin:0}}>Generador inteligente de propuestas de innovación farmacéutica</p>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>En desarrollo</div>
            <div style={{fontSize:28,fontWeight:800,color:'#f59e0b'}}>{(stats?.en_desarrollo||0)+(stats?.en_analisis||0)}</div>
          </div>
          <div style={{textAlign:'right',color:'#fff'}}>
            <div style={{fontSize:13,opacity:.7}}>Favoritas</div>
            <div style={{fontSize:28,fontWeight:800}}>{stats?.favoritos||0}</div>
          </div>
          <button className="prop-generar-btn" onClick={generar} disabled={generating}>
            {generating ? <><span className="radar-spinner"/> Generando...</> : <><Sparkles size={16}/> Generar con IA</>}
          </button>
        </div>
      </div>

      <div className="radar-tabs">
        <button className={tab==='catalogo'?'active':''} onClick={()=>setTab('catalogo')}><Lightbulb size={14}/> Catálogo</button>
        <button className={tab==='favoritos'?'active':''} onClick={()=>setTab('favoritos')}><Star size={14}/> Mis favoritas ({stats?.favoritos||0})</button>
        <button className={tab==='ejes'?'active':''} onClick={()=>setTab('ejes')}><BarChart3 size={14}/> Por eje</button>
        <button className={tab==='matriz'?'active':''} onClick={()=>setTab('matriz')}><Target size={14}/> Matriz impacto</button>
        <button className={tab==='stats'?'active':''} onClick={()=>setTab('stats')}><BarChart3 size={14}/> Estadísticas</button>
      </div>

      {tab === 'catalogo' && (
        <>
          <div className="radar-filters">
            <Filter size={16} style={{color:'#64748b',flexShrink:0}} />
            <select value={filtroEje} onChange={e=>setFiltroEje(e.target.value)}>
              <option value="">Todos los ejes</option>
              {Object.entries(PROP_EJE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select value={filtroEstado} onChange={e=>setFiltroEstado(e.target.value)}>
              <option value="">Todos los estados</option>
              {Object.entries(PROP_ESTADO_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select value={filtroImpacto} onChange={e=>setFiltroImpacto(e.target.value)}>
              <option value="">Todo impacto</option>
              <option value="MUY_ALTO">Muy alto</option>
              <option value="ALTO">Alto</option>
              <option value="MEDIO">Medio</option>
              <option value="BAJO">Bajo</option>
            </select>
            <select value={filtroOrigen} onChange={e=>setFiltroOrigen(e.target.value)}>
              <option value="">Todo origen</option>
              <option value="MANUAL">Manual</option>
              <option value="GENERADA_IA">Generada IA</option>
              <option value="RADAR">Desde Radar</option>
            </select>
            <div className="radar-search-wrap">
              <Search size={14} className="radar-search-icon" />
              <input className="radar-search" type="text" placeholder="Buscar propuesta..." value={buscar} onChange={e=>setBuscar(e.target.value)} />
            </div>
          </div>

          {loading ? <p className="apis-loading">Cargando propuestas...</p> : (
            <div className="propuestas-grid">
              {props.map(p => renderCard(p))}
            </div>
          )}
        </>
      )}

      {tab === 'favoritos' && (
        <div className="apis-favs-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Star size={18} color="#f59e0b"/> Mis propuestas favoritas ({favs.length})</h3>
          {favs.length === 0 ? <p style={{color:'#64748b'}}>No hay propuestas favoritas. Marca propuestas con <Star size={12}/> para organizar tu backlog aquí.</p> : (
            <div className="propuestas-grid">
              {favs.map(p => renderCard(p, true))}
            </div>
          )}
        </div>
      )}

      {tab === 'ejes' && (
        <div className="prop-ejes-section">
          {Object.entries(PROP_EJE_LABELS).map(([eje, label]) => {
            const ejeProps = props.filter(p => p.eje === eje)
            if (ejeProps.length === 0) return null
            const EIcon = PROP_EJE_ICONS[eje]
            const color = PROP_EJE_COLORS[eje]
            const prod = ejeProps.filter(p => p.estado === 'PRODUCCION').length
            const pct = ejeProps.length ? Math.round(prod / ejeProps.length * 100) : 0
            return (
              <div key={eje} className="prop-eje-group">
                <div className="prop-eje-header" style={{borderLeftColor: color}}>
                  <EIcon size={20} color={color}/>
                  <span style={{fontWeight:700,fontSize:16}}>{label}</span>
                  <span style={{fontSize:12,color:'#64748b'}}>({ejeProps.length} propuestas)</span>
                  <div className="prop-eje-progress">
                    <div className="prop-eje-bar" style={{width: pct+'%', background: color}}/>
                  </div>
                  <span style={{fontSize:11,color:'#64748b'}}>{pct}% en producción</span>
                </div>
                <div className="propuestas-grid">
                  {ejeProps.map(p => renderCard(p))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {tab === 'matriz' && (
        <div className="prop-matriz-section">
          <h3 style={{fontSize:18,fontWeight:700,marginBottom:16}}><Target size={18}/> Matriz Impacto vs Esfuerzo</h3>
          <div className="matriz-container" ref={matrizRef}>
            <div className="matriz-labels">
              <span className="matriz-label-y">Impacto</span>
              <span className="matriz-label-x">Esfuerzo</span>
            </div>
            <div className="matriz-quadrants">
              <div className="matriz-q quick-win"><span>QUICK WINS</span></div>
              <div className="matriz-q strategic"><span>ESTRATEGICOS</span></div>
              <div className="matriz-q minor"><span>MEJORAS MENORES</span></div>
              <div className="matriz-q avoid"><span>EVITAR</span></div>
            </div>
            {matriz.map(p => {
              const x = Math.max(5, Math.min(95, p.esfuerzo))
              const y = Math.max(5, Math.min(95, 100 - p.impacto_score))
              const color = PROP_EJE_COLORS[p.eje] || '#888'
              return (
                <div key={p.id} className="matriz-punto"
                  style={{left: x+'%', top: y+'%', background: color}}
                  onMouseEnter={()=>setHovered(p)}
                  onMouseLeave={()=>setHovered(null)}
                  title={`${p.titulo} (${PROP_EJE_LABELS[p.eje]})`}
                />
              )
            })}
            {hovered && (
              <div className="matriz-tooltip" style={{left: Math.min(70, hovered.esfuerzo)+'%', top: Math.max(10, 100-hovered.impacto_score-10)+'%'}}>
                <strong>{hovered.titulo}</strong>
                <div>{PROP_EJE_LABELS[hovered.eje]} · {hovered.impacto.replace('_',' ')}</div>
                <div>Esfuerzo: {hovered.esfuerzo} · Impacto: {hovered.impacto_score}</div>
              </div>
            )}
          </div>
          <div className="matriz-legend">
            {Object.entries(PROP_EJE_LABELS).map(([k,v]) => (
              <span key={k} className="matriz-legend-item">
                <span className="matriz-legend-dot" style={{background: PROP_EJE_COLORS[k]}}/>
                {v}
              </span>
            ))}
          </div>
        </div>
      )}

      {tab === 'stats' && stats && (
        <div className="radar-stats-section">
          <div className="apis-stats-cards">
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.total}</span><span>Total</span></div>
            <div className="apis-stat-card conectada"><span className="apis-stat-num">{stats.produccion||0}</span><span>Producción</span></div>
            <div className="apis-stat-card pendiente"><span className="apis-stat-num">{stats.en_desarrollo||0}</span><span>En desarrollo</span></div>
            <div className="apis-stat-card apex"><span className="apis-stat-num">{stats.en_analisis||0}</span><span>En análisis</span></div>
            <div className="apis-stat-card"><span className="apis-stat-num">{stats.favoritos||0}</span><span>Favoritas</span></div>
            <div className="apis-stat-card futuro"><span className="apis-stat-num">{stats.generadas_ia||0}</span><span>Generadas IA</span></div>
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}><BarChart3 size={16}/> Por eje</h3>
          <div className="radar-bars">
            {stats.por_eje && stats.por_eje.map(e => {
              const pct = stats.total ? Math.round(e.n/stats.total*100) : 0
              const EIcon = PROP_EJE_ICONS[e.eje] || Lightbulb
              const color = PROP_EJE_COLORS[e.eje] || '#888'
              return (
                <div key={e.eje} className="radar-bar-row">
                  <span className="radar-bar-label"><EIcon size={12}/> {PROP_EJE_LABELS[e.eje]}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: color}}/></div>
                  <span className="radar-bar-val">{e.n}</span>
                </div>
              )
            })}
          </div>

          <h3 style={{fontSize:16,fontWeight:700,margin:'24px 0 12px'}}>Por impacto</h3>
          <div className="radar-bars">
            {stats.por_impacto && stats.por_impacto.map(i => {
              const pct = stats.total ? Math.round(i.n/stats.total*100) : 0
              const color = PROP_IMPACTO_COLORS[i.impacto] || '#888'
              return (
                <div key={i.impacto} className="radar-bar-row">
                  <span className="radar-bar-label">{i.impacto.replace('_',' ')}</span>
                  <div className="radar-bar-track"><div className="radar-bar-fill" style={{width: pct+'%', background: color}}/></div>
                  <span className="radar-bar-val">{i.n}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {notaModal && (
        <div className="radar-modal-overlay" onClick={()=>setNotaModal(null)}>
          <div className="radar-modal" onClick={e=>e.stopPropagation()}>
            <h4><StickyNote size={16}/> Nota</h4>
            <textarea value={notaText} onChange={e=>setNotaText(e.target.value)} rows={4} placeholder="Escribe tu nota aquí..." />
            <div style={{display:'flex',gap:8,justifyContent:'flex-end',marginTop:12}}>
              <button className="radar-modal-cancel" onClick={()=>setNotaModal(null)}>Cancelar</button>
              <button className="radar-modal-save" onClick={saveNota}>Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* ═══ App ═══ */
function App() {
  return (
    <BrowserRouter>
      <Nav />
      <main className="sf-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/pacientes" element={<Pacientes />} />
          <Route path="/paciente/:id" element={<FichaPaciente />} />
          <Route path="/emprm" element={<EmprmPendientes />} />
          <Route path="/integraciones" element={<Integraciones />} />
          <Route path="/jefatura" element={<Jefatura />} />
          <Route path="/radar" element={<RadarIA />} />
          <Route path="/apis" element={<CatalogoAPIs />} />
          <Route path="/ml" element={<AlgoritmosML />} />
          <Route path="/propuestas" element={<PropuestasEstrategicas />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
