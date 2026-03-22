-- ═══════════════════════════════════════════════════════════════
-- SIGFAR Hub — Módulo A: Stack (Mapa Arquitectura)
-- Tabla + 28 componentes del ecosistema SIGFAR
-- Ejecutar: docker exec -i sigfar-hub-db psql -U sigfar -d sigfar < db/init/07_stack.sql
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS hgu_stack_components (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    nombre_corto        VARCHAR(40),
    descripcion         TEXT,
    grupo               VARCHAR(30) NOT NULL CHECK (grupo IN (
                            'HUB_DOCKER','APEX_APPS','IA_MODELOS',
                            'APIS_EXTERNAS','HOSPITAL_SISTEMAS','REPO'
                        )),
    tipo                VARCHAR(30) DEFAULT 'SERVICIO' CHECK (tipo IN (
                            'CONTENEDOR','APP_ORACLE','MODELO_IA','API_EXTERNA',
                            'SISTEMA_HOSPITAL','REPO','SERVICIO','BASE_DATOS'
                        )),
    tecnologia          VARCHAR(100),
    version             VARCHAR(50),
    url_base            VARCHAR(500),
    url_docs            VARCHAR(500),
    url_health          VARCHAR(500),
    puerto              VARCHAR(20),
    estado              VARCHAR(20) DEFAULT 'OPERATIVO' CHECK (estado IN (
                            'OPERATIVO','DEGRADADO','CAIDO','PENDIENTE','NO_APLICA'
                        )),
    icono               VARCHAR(50),
    color               VARCHAR(7) DEFAULT '#6366f1',
    conexiones          VARCHAR(500),
    depende_de          VARCHAR(200),
    ultimo_check        TIMESTAMP,
    ultimo_check_ok     BOOLEAN,
    latencia_ms         INTEGER,
    notas               TEXT,
    orden_visual        INTEGER DEFAULT 0,
    visible             BOOLEAN DEFAULT TRUE,
    fecha_creacion      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stack_grupo ON hgu_stack_components(grupo);
CREATE INDEX idx_stack_estado ON hgu_stack_components(estado);
CREATE INDEX idx_stack_tipo ON hgu_stack_components(tipo);

-- ═══════════════════════════════════════════════════════════════
-- SEED: 28 componentes del ecosistema SIGFAR
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_stack_components
    (nombre, nombre_corto, descripcion, grupo, tipo, tecnologia, version, url_base, url_health, puerto, estado, icono, color, conexiones, depende_de, orden_visual)
VALUES

-- ── HUB_DOCKER (3 contenedores) ──────────────────────────────
(
    'PostgreSQL 16 (sigfar-hub-db)',
    'Hub DB',
    'Base de datos principal del Hub. Almacena pacientes, tratamientos, EM/PRM, radar, APIs, ML, propuestas y stack. 18 tablas hgu_*.',
    'HUB_DOCKER', 'BASE_DATOS', 'PostgreSQL', '16.x',
    'postgresql://db:5432/sigfar', NULL, '5432',
    'OPERATIVO', 'Database', '#336791',
    'sigfar-hub-api', NULL, 1
),
(
    'FastAPI Backend (sigfar-hub-api)',
    'Hub API',
    'API REST async con SQLAlchemy + httpx. ~2000 líneas. Endpoints: pacientes, EM/PRM, radar, APIs, ML, propuestas, stack, Groq IA.',
    'HUB_DOCKER', 'CONTENEDOR', 'FastAPI / Python', '3.12',
    'http://localhost:8000', 'http://localhost:8000/health', '8000',
    'OPERATIVO', 'Server', '#009688',
    'sigfar-hub-db,groq,gemini,cima,pubmed,openfda,ords-sigfar,ords-gestionax', 'sigfar-hub-db', 2
),
(
    'React 18 + Vite (sigfar-hub-web)',
    'Hub Web',
    'SPA React con lucide-react icons. ~2500 líneas. Módulos: Dashboard, Pacientes, EM/PRM, Radar IA, APIs, ML, Propuestas, Stack.',
    'HUB_DOCKER', 'CONTENEDOR', 'React / Vite', '18.x',
    'http://localhost:3000', NULL, '3000',
    'OPERATIVO', 'MonitorSmartphone', '#61dafb',
    'sigfar-hub-api', 'sigfar-hub-api', 3
),

-- ── APEX_APPS (7 aplicaciones Oracle APEX) ───────────────────
(
    'SIGFAR (P15) — Validación Farmacoterapéutica',
    'SIGFAR',
    'Aplicación principal de farmacia hospitalaria en Oracle APEX. Validación de prescripciones, EM/PRM, intervenciones. ~422 pacientes/día.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'Pill', '#f59e0b',
    'ords-sigfar,sigfar-hub-api', NULL, 10
),
(
    'GestionAX — Gestión Almacén Farmacia',
    'GestionAX',
    'Gestión de stock, consumos, precios, GFT y catálogo de medicamentos del hospital. Datos económicos y logísticos.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'Wallet', '#8b5cf6',
    'ords-gestionax,sigfar-hub-api', NULL, 11
),
(
    'PROA (P43) — Programa Antibióticos',
    'PROA',
    'Programa de Optimización de Uso de Antimicrobianos. Cultivos, antibiogramas, desescalada, seguimiento ATB.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'Shield', '#ef4444',
    'ords-sigfar', NULL, 12
),
(
    'NutriWin (P36/P37) — Nutrición Parenteral',
    'NutriWin',
    'Prescripción y preparación de nutrición parenteral. Integración con ExactaMix para elaboración automatizada.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'FlaskConical', '#10b981',
    'exactamix', NULL, 13
),
(
    'Citostáticos — Preparación Antineoplásicos',
    'Citostáticos',
    'Preparación y control de medicamentos citostáticos. Dosificación, protocolos, trazabilidad.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'Target', '#ec4899',
    NULL, NULL, 14
),
(
    'Ensayos Clínicos',
    'Ensayos',
    'Gestión de medicamentos en investigación. Dispensación a pacientes, trazabilidad, caducidades, aleatorización.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'Clipboard', '#6366f1',
    NULL, NULL, 15
),
(
    'Formulación Magistral',
    'Magistral',
    'Prescripción y elaboración de fórmulas magistrales. Control de materias primas, procedimientos normalizados.',
    'APEX_APPS', 'APP_ORACLE', 'Oracle APEX', '23.x',
    NULL, NULL, NULL,
    'OPERATIVO', 'FlaskConical', '#14b8a6',
    NULL, NULL, 16
),

-- ── IA_MODELOS (4 modelos) ───────────────────────────────────
(
    'Groq — llama-3.3-70b-versatile',
    'Groq',
    'LLM principal del Hub. API gratuita, 30 req/min. Usado en: análisis EM/PRM, enriquecimiento radar, APIs, ML, propuestas. Latencia ~1-3s.',
    'IA_MODELOS', 'MODELO_IA', 'Groq Cloud', 'llama-3.3-70b',
    'https://api.groq.com/openai/v1', 'https://api.groq.com/openai/v1/models', NULL,
    'OPERATIVO', 'Zap', '#f97316',
    'sigfar-hub-api', NULL, 20
),
(
    'Google Gemini',
    'Gemini',
    'LLM secundario para Multi-IA Consenso. API gratuita con limits generosos. Modelo gemini-2.0-flash.',
    'IA_MODELOS', 'MODELO_IA', 'Google AI', 'gemini-2.0-flash',
    'https://generativelanguage.googleapis.com/v1beta', NULL, NULL,
    'PENDIENTE', 'Sparkles', '#4285f4',
    'sigfar-hub-api', NULL, 21
),
(
    'LM Studio Local',
    'LM Studio',
    'LLM local para modo offline y datos sensibles. Sin coste, sin envío de datos a cloud. Modelos GGUF.',
    'IA_MODELOS', 'MODELO_IA', 'LM Studio', 'local',
    'http://localhost:1234/v1', NULL, '1234',
    'PENDIENTE', 'Cpu', '#a855f7',
    'sigfar-hub-api', NULL, 22
),
(
    'OpenAI GPT-4',
    'GPT-4',
    'LLM premium para casos complejos. De pago. Reservado para validación y benchmarking contra modelos gratuitos.',
    'IA_MODELOS', 'MODELO_IA', 'OpenAI', 'gpt-4o',
    'https://api.openai.com/v1', NULL, NULL,
    'PENDIENTE', 'Brain', '#10a37f',
    'sigfar-hub-api', NULL, 23
),

-- ── APIS_EXTERNAS (8 APIs) ───────────────────────────────────
(
    'CIMA — AEMPS Medicamentos',
    'CIMA',
    'API de la Agencia Española del Medicamento. Fichas técnicas, prospectos, principios activos, interacciones. Sin auth, gratuita.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST JSON', 'v1',
    'https://cima.aemps.es/cima/rest', NULL, NULL,
    'OPERATIVO', 'Pill', '#dc2626',
    'sigfar-hub-api', NULL, 30
),
(
    'PubMed / NCBI E-utilities',
    'PubMed',
    'Búsqueda de evidencia científica. esearch + efetch. 3 req/s sin API key, 10 req/s con API key.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST XML', 'v2',
    'https://eutils.ncbi.nlm.nih.gov/entrez/eutils', NULL, NULL,
    'OPERATIVO', 'BookOpen', '#2563eb',
    'sigfar-hub-api', NULL, 31
),
(
    'OpenFDA — Eventos adversos',
    'OpenFDA',
    'API de la FDA. Eventos adversos, retiradas, etiquetado. Gratuita, 240 req/min sin API key.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST JSON', 'v2',
    'https://api.fda.gov', NULL, NULL,
    'OPERATIVO', 'ShieldAlert', '#1d4ed8',
    'sigfar-hub-api', NULL, 32
),
(
    'DrugBank — Interacciones',
    'DrugBank',
    'Base de datos de interacciones farmacológicas, mecanismos de acción, farmacocinética. API académica.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST JSON', 'v1',
    'https://go.drugbank.com/api/v1', NULL, NULL,
    'PENDIENTE', 'AlertTriangle', '#7c3aed',
    'sigfar-hub-api', NULL, 33
),
(
    'ORDS SIGFAR — Oracle REST',
    'ORDS SIGFAR',
    'Endpoint REST Data Services expuesto desde Oracle APEX. Acceso a datos de SIGFAR: pacientes, tratamientos, analíticas.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'ORDS', 'v1',
    NULL, NULL, NULL,
    'PENDIENTE', 'Database', '#f59e0b',
    'sigfar,sigfar-hub-api', NULL, 34
),
(
    'ORDS GestionAX — Oracle REST',
    'ORDS GestionAX',
    'Endpoint REST Data Services expuesto desde Oracle APEX. Acceso a datos de GestionAX: stock, precios, consumos, catálogo.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'ORDS', 'v1',
    NULL, NULL, NULL,
    'PENDIENTE', 'Database', '#8b5cf6',
    'gestionax,sigfar-hub-api', NULL, 35
),
(
    'RxNorm — NLM Terminología',
    'RxNorm',
    'API del NLM para normalización de nombres de medicamentos. Mapeo entre códigos ATC, NDC, SNOMED.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST JSON', 'v1',
    'https://rxnav.nlm.nih.gov/REST', NULL, NULL,
    'OPERATIVO', 'Tags', '#059669',
    'sigfar-hub-api', NULL, 36
),
(
    'SNS Nomenclátor — Precios oficiales',
    'Nomenclátor',
    'Nomenclátor del SNS con precios oficiales de medicamentos en España. Actualización mensual.',
    'APIS_EXTERNAS', 'API_EXTERNA', 'REST/CSV', 'v1',
    'https://www.sanidad.gob.es/profesionales/nomenclator.do', NULL, NULL,
    'PENDIENTE', 'Calculator', '#b91c1c',
    'sigfar-hub-api', NULL, 37
),

-- ── HOSPITAL_SISTEMAS (4 sistemas) ──────────────────────────
(
    'Armarios Automáticos (Pyxis/Omnicell)',
    'Armarios',
    'Dispensación automatizada de medicamentos en planta. Logs de dispensación para control de estupefacientes.',
    'HOSPITAL_SISTEMAS', 'SISTEMA_HOSPITAL', 'Pyxis / Omnicell', NULL,
    NULL, NULL, NULL,
    'OPERATIVO', 'Archive', '#78716c',
    NULL, NULL, 40
),
(
    'ExactaMix — Preparación NP',
    'ExactaMix',
    'Sistema automatizado de preparación de nutrición parenteral. Integración con NutriWin para órdenes.',
    'HOSPITAL_SISTEMAS', 'SISTEMA_HOSPITAL', 'Baxter ExactaMix', NULL,
    NULL, NULL, NULL,
    'OPERATIVO', 'FlaskConical', '#65a30d',
    'nutriwin', NULL, 41
),
(
    'SIA / Abucasis — Atención Primaria',
    'Abucasis',
    'Sistema de Información Ambulatoria de la Comunitat Valenciana. Prescripción de atención primaria, historial domiciliario.',
    'HOSPITAL_SISTEMAS', 'SISTEMA_HOSPITAL', 'GVA SIA', NULL,
    NULL, NULL, NULL,
    'OPERATIVO', 'Stethoscope', '#0284c7',
    NULL, NULL, 42
),
(
    'ORION Clinic — HIS Hospitalario',
    'ORION',
    'Historia clínica electrónica del hospital. Diagnósticos, informes, analíticas, notas clínicas.',
    'HOSPITAL_SISTEMAS', 'SISTEMA_HOSPITAL', 'Dedalus ORION', NULL,
    NULL, NULL, NULL,
    'OPERATIVO', 'Hospital', '#4f46e5',
    NULL, NULL, 43
),

-- ── REPO (2 repositorios) ────────────────────────────────────
(
    'GitHub — sigfar-hub',
    'GitHub',
    'Repositorio del proyecto SIGFAR Hub. Código fuente, CI/CD, issues, documentación.',
    'REPO', 'REPO', 'Git / GitHub', NULL,
    'https://github.com/ximodante/SIGFAR-HUB', NULL, NULL,
    'OPERATIVO', 'GitBranch', '#24292e',
    NULL, NULL, 50
),
(
    'Docker Hub — Images',
    'Docker Hub',
    'Registro de imágenes Docker. Imágenes base para los 3 contenedores del Hub.',
    'REPO', 'REPO', 'Docker Hub', NULL,
    'https://hub.docker.com', NULL, NULL,
    'OPERATIVO', 'Layers', '#2496ed',
    NULL, NULL, 51
);
