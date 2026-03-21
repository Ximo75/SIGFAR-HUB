import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom'
import Markdown from 'react-markdown'
import { Activity, AlertTriangle, BarChart3, Brain, Building2, CheckCircle2, ChevronDown, ChevronRight, Clipboard, Clock, Database, FileText, FlaskConical, Heart, Home, LayoutDashboard, Mic, MicOff, MonitorSmartphone, Network, Pill, Send, Server, Shield, ShieldAlert, Stethoscope, TrendingDown, TrendingUp, Users, Volume2, VolumeX, Wallet, Zap } from 'lucide-react'
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
        <Link to="/"><span className="nav-icon"><LayoutDashboard size={16}/></span>Dashboard</Link>
        <Link to="/pacientes"><span className="nav-icon"><Users size={16}/></span>Pacientes</Link>
        <Link to="/emprm"><span className="nav-icon"><ShieldAlert size={16}/></span>EM/PRM</Link>
        <Link to="/integraciones"><span className="nav-icon"><Network size={16}/></span>Integraciones</Link>
        <Link to="/jefatura"><span className="nav-icon"><BarChart3 size={16}/></span>Jefatura</Link>
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
  const recognitionRef = React.useRef(null)
  const messagesEndRef = React.useRef(null)

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
    const recog = new SpeechRecognition()
    recog.lang = 'es-ES'
    recog.interimResults = false
    recog.onresult = (e) => {
      const text = e.results[0][0].transcript
      setPregunta(text)
    }
    recog.onend = () => setRecording(false)
    recog.onerror = () => setRecording(false)
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
        </div>
      </div>
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
        </Routes>
      </main>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
