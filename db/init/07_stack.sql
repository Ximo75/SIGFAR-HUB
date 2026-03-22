-- ═══════════════════════════════════════════════════════════════
-- SIGFAR Hub — Módulo A: Stack (Mapa Arquitectura)
-- DROP + CREATE + 27 componentes del ecosistema SIGFAR
-- Ejecutar: docker exec -i sigfar-hub-db psql -U sigfar -d sigfar < db/init/07_stack.sql
-- ═══════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hgu_stack_components CASCADE;

CREATE TABLE hgu_stack_components (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    descripcion         TEXT,
    tipo                VARCHAR(30) NOT NULL CHECK (tipo IN (
                            'DOCKER','APEX_APP','IA','API_EXTERNA','HOSPITAL','REPO','OTRO'
                        )),
    subtipo             VARCHAR(50),
    url                 VARCHAR(500),
    url_docs            VARCHAR(500),
    icono               VARCHAR(50),
    tecnologia          VARCHAR(200),
    puerto              VARCHAR(20),
    estado              VARCHAR(20) DEFAULT 'CONECTADO' CHECK (estado IN (
                            'CONECTADO','PENDIENTE','FUTURO','ERROR'
                        )),
    posicion_diagrama   VARCHAR(20) CHECK (posicion_diagrama IN (
                            'CENTRO','IZQUIERDA','DERECHA','ARRIBA','ABAJO'
                        )),
    grupo               VARCHAR(50),
    detalles            JSONB,
    orden               INTEGER DEFAULT 0,
    fecha_creacion      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stack_grupo ON hgu_stack_components(grupo);
CREATE INDEX idx_stack_tipo ON hgu_stack_components(tipo);
CREATE INDEX idx_stack_estado ON hgu_stack_components(estado);
CREATE INDEX idx_stack_posicion ON hgu_stack_components(posicion_diagrama);

-- ═══════════════════════════════════════════════════════════════
-- SEED: 27 componentes del ecosistema SIGFAR
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_stack_components
    (nombre, descripcion, tipo, subtipo, url, url_docs, icono, tecnologia, puerto, estado, posicion_diagrama, grupo, detalles, orden)
VALUES

-- ── GRUPO: hub_docker (CENTRO) ───────────────────────────────
(
    'PostgreSQL 16',
    'Base de datos local del Hub. 18+ tablas hgu_*, datos de 5 pacientes demo, logs IA, radar, APIs, ML, propuestas, stack.',
    'DOCKER', 'Base de datos', NULL, NULL,
    'Database', 'PostgreSQL 16 Alpine', ':5432',
    'CONECTADO', 'CENTRO', 'hub_docker',
    '{"tablas": 18}', 1
),
(
    'FastAPI Backend',
    'API REST Python con 50+ endpoints. Swagger en /docs. Hot-reload activado. SQLAlchemy async + httpx.',
    'DOCKER', 'Backend API', 'http://localhost:8000/docs', NULL,
    'Server', 'Python 3.12 + FastAPI + SQLAlchemy async', ':8000',
    'CONECTADO', 'CENTRO', 'hub_docker',
    '{"endpoints": 50}', 2
),
(
    'React Frontend',
    'Dashboard visual del Hub. Vite + React 18 + lucide-react. Hot-reload activado. 10 rutas.',
    'DOCKER', 'Frontend', 'http://localhost:3000', NULL,
    'MonitorSmartphone', 'React 18 + Vite + Lucide icons', ':3000',
    'CONECTADO', 'CENTRO', 'hub_docker',
    '{"rutas": 10}', 3
),

-- ── GRUPO: apex_apps (IZQUIERDA) ─────────────────────────────
(
    'Plataforma SIGFAR',
    'Gestión clínica: 422 pacientes, EM/PRM, TDM MAP Bayesiano, PROA 6 agentes, Nutrición Artificial 7 agentes, NPD. Oracle APEX 24.2.',
    'APEX_APP', 'Gestión clínica',
    'https://g8c4d77eb0885ce-d3r53j8rymx0jo3u.adb.eu-madrid-1.oraclecloudapps.com/ords/r/sigfar_uci_we/plataforma-sigfar/login',
    NULL, 'HeartPulse', 'Oracle APEX 24.2 + ADB Always Free', NULL,
    'CONECTADO', 'IZQUIERDA', 'apex_apps',
    '{"pacientes": 422, "modulos": ["P15","P36","P37","P40","P42","P43"]}', 1
),
(
    'GestionAX',
    'Gestión económica: 2M consumos, 2.692 artículos GFT, catálogo hospital. Oracle APEX 24.2.',
    'APEX_APP', 'Gestión económica',
    'https://g8c4d77eb0885ce-qfn41ot5o9ncm53f.adb.eu-madrid-1.oraclecloudapps.com/ords/r/gestion_we/gestionax/login',
    NULL, 'Wallet', 'Oracle APEX 24.2 + ADB Always Free', NULL,
    'CONECTADO', 'IZQUIERDA', 'apex_apps',
    '{"consumos": "2M", "gft": 2692}', 2
),

-- ── GRUPO: ia_modelos (DERECHA) ──────────────────────────────
(
    'Groq Cloud (Llama 3.3 70B)',
    'IA generativa principal. 14.400 req/día gratis. Genera POF, detecta EM/PRM, Sigfarita, Radar IA, enriquecimiento.',
    'IA', 'LLM Cloud', 'https://console.groq.com', 'https://console.groq.com/docs',
    'Zap', 'Llama 3.3 70B vía LPU', NULL,
    'CONECTADO', 'DERECHA', 'ia_modelos',
    '{"modelo": "llama-3.3-70b-versatile", "free_tier": "14.400 req/día"}', 1
),
(
    'Google Gemini',
    'Segundo modelo IA para Multi-IA Consenso. 1.500 req/día gratis. Modelo gemini-2.0-flash.',
    'IA', 'LLM Cloud', 'https://aistudio.google.com', 'https://ai.google.dev/docs',
    'Sparkles', 'Gemini 2.0 Flash', NULL,
    'PENDIENTE', 'DERECHA', 'ia_modelos',
    '{"free_tier": "1.500 req/día"}', 2
),
(
    'LM Studio local',
    'IA local sin internet. Qwen, Llama, Meditron en tu Mac. Para datos sensibles. 256K tokens contexto.',
    'IA', 'LLM Local', 'http://localhost:1234', NULL,
    'Cpu', 'Qwen3-Coder-30B / Llama', ':1234',
    'PENDIENTE', 'DERECHA', 'ia_modelos',
    '{"contexto": "256K tokens"}', 3
),
(
    'Substrate AI (futuro)',
    'Cerebro IA dedicado dentro de la red del hospital. 70-120B parámetros. Sin salida de datos.',
    'IA', 'LLM Hospital', NULL, NULL,
    'Building2', 'Modelo dedicado hospital', NULL,
    'FUTURO', 'DERECHA', 'ia_modelos',
    NULL, 4
),

-- ── GRUPO: apis_externas (ARRIBA) ────────────────────────────
(
    'PubMed / NCBI',
    'Base de datos de 35M artículos biomédicos. eUtils REST API.',
    'API_EXTERNA', 'Evidencia',
    'https://pubmed.ncbi.nlm.nih.gov', 'https://www.ncbi.nlm.nih.gov/books/NBK25501/',
    'BookOpen', 'eUtils REST API', NULL,
    'CONECTADO', 'ARRIBA', 'apis_externas', NULL, 1
),
(
    'ClinicalTrials.gov',
    'Ensayos clínicos activos mundiales. API v2 REST.',
    'API_EXTERNA', 'Evidencia',
    'https://clinicaltrials.gov', 'https://clinicaltrials.gov/data-api/about-api',
    'FlaskConical', 'API v2 REST', NULL,
    'CONECTADO', 'ARRIBA', 'apis_externas', NULL, 2
),
(
    'CIMA / AEMPS',
    'Fichas técnicas medicamentos España. Vía proxy Cloudflare Worker.',
    'API_EXTERNA', 'Medicamentos',
    'https://cima.aemps.es', NULL,
    'Pill', 'REST via cima-proxy.ximomachi.workers.dev', NULL,
    'CONECTADO', 'ARRIBA', 'apis_externas', NULL, 3
),
(
    'OpenFDA',
    'Eventos adversos FAERS, recalls, etiquetado FDA.',
    'API_EXTERNA', 'Farmacovigilancia',
    'https://open.fda.gov', 'https://open.fda.gov/apis/',
    'ShieldAlert', 'REST API', NULL,
    'PENDIENTE', 'ARRIBA', 'apis_externas', NULL, 4
),
(
    'Semantic Scholar',
    'Búsqueda semántica de papers con IA. Graph API.',
    'API_EXTERNA', 'Evidencia',
    'https://www.semanticscholar.org', 'https://api.semanticscholar.org',
    'Search', 'Graph API', NULL,
    'PENDIENTE', 'ARRIBA', 'apis_externas', NULL, 5
),

-- ── GRUPO: hospital_sistemas (ABAJO) ─────────────────────────
(
    'ICCA (UCI)',
    'Datos UCI en tiempo real. Prescripciones, constantes, balances.',
    'HOSPITAL', 'UCI', NULL, NULL,
    'Activity', 'HL7/FHIR', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 1
),
(
    'OMA (Planta)',
    'Prescripción electrónica planta.',
    'HOSPITAL', 'Prescripción', NULL, NULL,
    'Clipboard', 'HL7', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 2
),
(
    'Hosix / Florence (HCE)',
    'Historia clínica electrónica.',
    'HOSPITAL', 'HCE', NULL, NULL,
    'FileText', 'FHIR R4', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 3
),
(
    'Kardex',
    'Sistema de dispensación automatizada.',
    'HOSPITAL', 'Logística', NULL, NULL,
    'Archive', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 4
),
(
    'Armarios estupefacientes',
    'Dispensación controlada de opioides/estupefacientes.',
    'HOSPITAL', 'Logística', NULL, NULL,
    'Shield', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 5
),
(
    'PYXIS',
    'Dispensación automatizada de medicamentos.',
    'HOSPITAL', 'Dispensación', NULL, NULL,
    'Archive', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 6
),
(
    'Versia',
    'Prescripción de nutrición parenteral.',
    'HOSPITAL', 'Elaboración', NULL, NULL,
    'FlaskConical', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 7
),
(
    'ExactaMix Pro',
    'Robot de elaboración de nutrición parenteral.',
    'HOSPITAL', 'Robot', NULL, NULL,
    'Cpu', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 8
),
(
    'ChemoMaker',
    'Robot de elaboración de quimioterapia.',
    'HOSPITAL', 'Robot', NULL, NULL,
    'FlaskConical', 'Propietario', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 9
),
(
    'Laboratorio',
    'Analíticas en tiempo real.',
    'HOSPITAL', 'Laboratorio', NULL, NULL,
    'Activity', 'HL7', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 10
),
(
    'Microbiología',
    'Cultivos y antibiogramas.',
    'HOSPITAL', 'Microbiología', NULL, NULL,
    'FlaskConical', 'HL7', NULL,
    'FUTURO', 'ABAJO', 'hospital_sistemas', NULL, 11
),

-- ── GRUPO: repo ──────────────────────────────────────────────
(
    'GitHub',
    'Repositorio de código fuente de SIGFAR Hub.',
    'REPO', 'Código',
    'https://github.com/Ximo75/SIGFAR-HUB', NULL,
    'GitBranch', 'Git', NULL,
    'CONECTADO', 'DERECHA', 'repo', NULL, 1
);
