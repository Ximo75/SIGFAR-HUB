-- ═══════════════════════════════════════════════════════════════
-- SIGFAR Hub — Módulo F: Evidencia SIGFAR
-- Benchmarking científico + Panel Futuro vs Realidad + Papers
-- Ejecutar: docker exec -i sigfar-hub-db psql -U sigfar -d sigfar < db/init/08_evidencia.sql
-- ═══════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hgu_evidencia_papers CASCADE;
DROP TABLE IF EXISTS hgu_evidencia_comparativas CASCADE;
DROP TABLE IF EXISTS hgu_evidencia_benchmarks CASCADE;

-- ═══════════════════════════════════════════════════════════════
-- Tabla 1: Benchmarks (análisis de artículos)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_evidencia_benchmarks (
    id                  SERIAL PRIMARY KEY,
    titulo_articulo     VARCHAR(500) NOT NULL,
    autores             VARCHAR(500),
    revista             VARCHAR(200),
    anio                INTEGER,
    doi                 VARCHAR(200),
    url                 VARCHAR(500),
    pdf_filename        VARCHAR(200),
    resumen_articulo    TEXT,
    fecha_analisis      TIMESTAMP DEFAULT NOW(),
    cobertura_global    INTEGER,
    json_analisis       JSONB,
    nota_usuario        TEXT,
    favorito            BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_evidencia_bench_favorito ON hgu_evidencia_benchmarks(favorito);
CREATE INDEX idx_evidencia_bench_anio ON hgu_evidencia_benchmarks(anio);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 2: Comparativas (filas artículo vs SIGFAR)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_evidencia_comparativas (
    id                      SERIAL PRIMARY KEY,
    benchmark_id            INTEGER NOT NULL REFERENCES hgu_evidencia_benchmarks(id) ON DELETE CASCADE,
    funcionalidad_articulo  VARCHAR(500) NOT NULL,
    dominio_sefh            VARCHAR(30) CHECK (dominio_sefh IN (
                                'AT_PRESENCIAL','AT_NO_PRESENCIAL','GESTION_LOGISTICA','EDUCACION','INVESTIGACION'
                            )),
    estado_sigfar           VARCHAR(20) CHECK (estado_sigfar IN (
                                'IMPLEMENTADO','PARCIAL','PLANIFICADO','NO_CONTEMPLADO','SUPERA_ARTICULO'
                            )),
    modulo_sigfar           VARCHAR(100),
    descripcion_sigfar      TEXT,
    ventaja_sigfar          TEXT,
    gap                     TEXT,
    es_pionero              BOOLEAN DEFAULT FALSE,
    orden                   INTEGER DEFAULT 0
);

CREATE INDEX idx_evidencia_comp_benchmark ON hgu_evidencia_comparativas(benchmark_id);
CREATE INDEX idx_evidencia_comp_estado ON hgu_evidencia_comparativas(estado_sigfar);
CREATE INDEX idx_evidencia_comp_pionero ON hgu_evidencia_comparativas(es_pionero);
CREATE INDEX idx_evidencia_comp_dominio ON hgu_evidencia_comparativas(dominio_sefh);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 3: Papers generados
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_evidencia_papers (
    id                  SERIAL PRIMARY KEY,
    titulo              VARCHAR(500) NOT NULL,
    contenido_markdown  TEXT,
    benchmarks_usados   INTEGER[],
    fecha_generacion    TIMESTAMP DEFAULT NOW(),
    version             INTEGER DEFAULT 1,
    estado              VARCHAR(20) DEFAULT 'BORRADOR' CHECK (estado IN (
                            'BORRADOR','EN_REVISION','ENVIADO','PUBLICADO'
                        )),
    nota_usuario        TEXT,
    favorito            BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_evidencia_papers_estado ON hgu_evidencia_papers(estado);
CREATE INDEX idx_evidencia_papers_favorito ON hgu_evidencia_papers(favorito);

-- ═══════════════════════════════════════════════════════════════
-- SEED: Benchmark precargado — González-Pérez et al. (2024)
-- "Acercando la IA a los servicios de farmacia hospitalaria"
-- Farmacia Hospitalaria, 2024
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_evidencia_benchmarks
    (titulo_articulo, autores, revista, anio, resumen_articulo, cobertura_global, favorito)
VALUES (
    'Acercando la inteligencia artificial a los servicios de farmacia hospitalaria',
    'González-Pérez P, Gómez-Álvarez S, et al.',
    'Farmacia Hospitalaria',
    2024,
    'Artículo de revisión que analiza las aplicaciones actuales y futuras de la inteligencia artificial en servicios de farmacia hospitalaria. Cubre gestión farmacoterapéutica, medicina de precisión, seguridad clínica, gestión de inventarios, formación y ensayos clínicos. Concluye que la IA tiene potencial transformador pero la mayoría de aplicaciones están en fase temprana.',
    78,
    TRUE
);

INSERT INTO hgu_evidencia_comparativas
    (benchmark_id, funcionalidad_articulo, dominio_sefh, estado_sigfar, modulo_sigfar, descripcion_sigfar, ventaja_sigfar, gap, es_pionero, orden)
VALUES
-- Funcionalidades que el artículo describe y SIGFAR tiene implementadas
(1, 'Gestión farmacoterapia y recomendaciones con IA',
    'AT_PRESENCIAL', 'IMPLEMENTADO', 'P15',
    'Pipeline multiagente con 6 categorías PCNE v9.1 para detección de EM/PRM. Groq/Llama genera POF estructurado.',
    'Pipeline multiagente > sistema experto simple del artículo. Scoring complejidad 14 dims integrado.',
    NULL, FALSE, 1),

(1, 'Medicina de precisión / TDM con IA',
    'AT_PRESENCIAL', 'IMPLEMENTADO', 'P42',
    'Farmacocinética clínica con estimación MAP Bayesiana funcionando para vancomicina, gentamicina, amikacina.',
    'MAP Bayesiano real funcionando en producción, no solo teórico como describe el artículo.',
    NULL, FALSE, 2),

(1, 'Seguridad clínica / detección DDI-RAM',
    'AT_PRESENCIAL', 'IMPLEMENTADO', 'P15',
    'Detección automática de interacciones, RAM, duplicidades, contraindicaciones con IA. 6 categorías PCNE v9.1.',
    'Scoring complejidad integrado + análisis multiagente > alertas simples.',
    NULL, FALSE, 3),

(1, 'Seguimiento paciente crónico / chatbot paciente',
    'AT_NO_PRESENCIAL', 'NO_CONTEMPLADO', NULL,
    NULL, NULL,
    'SIGFAR está orientado al farmacéutico hospitalario, no al paciente directamente. Scope diferente.',
    FALSE, 4),

(1, 'Gestión inventarios con IA',
    'GESTION_LOGISTICA', 'PLANIFICADO', 'Hub',
    'Propuesta Estratégica precargada: Predicción rotura stock con SARIMA/Prophet sobre datos GestionAX.',
    NULL,
    'Pendiente de implementar. Requiere datos históricos de GestionAX vía ORDS.',
    FALSE, 5),

(1, 'Acuerdos de pago y gestión económica con IA',
    'GESTION_LOGISTICA', 'PLANIFICADO', 'Hub',
    'Propuesta Estratégica precargada: Cruce Clínico-Económico SIGFAR + GestionAX.',
    NULL,
    'Pendiente. Requiere cruzar SIGFAR (diagnósticos) con GestionAX (precios).',
    FALSE, 6),

(1, 'Formación farmacéuticos con IA',
    'EDUCACION', 'PLANIFICADO', 'Hub',
    'Propuesta Estratégica precargada: Simulador FIR con generación de casos clínicos por IA.',
    NULL,
    'Pendiente de implementar.',
    FALSE, 7),

(1, 'Ensayos clínicos y evidencia científica',
    'INVESTIGACION', 'IMPLEMENTADO', 'P15 + Hub',
    'ClinicalTrials.gov y PubMed integrados en Hub (Radar IA + APIs). Chat P15 busca evidencia automáticamente.',
    'Integración bidireccional: Radar IA monitoriza + Chat P15 busca en tiempo real.',
    NULL, FALSE, 8),

-- Funcionalidades PIONERAS de SIGFAR (no mencionadas en el artículo)
(1, 'Nutrición Artificial con 7 agentes IA',
    'AT_PRESENCIAL', 'SUPERA_ARTICULO', 'P36',
    '7 agentes especializados: screening, requerimientos, fórmulas, cobertura, balance hídrico, analítica, plan.',
    'NO MENCIONADO en el artículo. SIGFAR es PIONERO con 7 agentes IA para nutrición artificial.',
    NULL, TRUE, 9),

(1, 'PROA antimicrobianos con 6 agentes IA',
    'AT_PRESENCIAL', 'SUPERA_ARTICULO', 'P43',
    '6 agentes PROA: evaluación, cultivos, desescalada, duración, profilaxis, educación.',
    'NO MENCIONADO en el artículo. PROA multiagente con IA es innovación única de SIGFAR.',
    NULL, TRUE, 10),

(1, 'NPD domiciliaria con IA',
    'AT_NO_PRESENCIAL', 'SUPERA_ARTICULO', 'P37',
    'Nutrición Parenteral Domiciliaria gestionada con IA. Seguimiento remoto de pacientes NPD.',
    'NO MENCIONADO en el artículo. Único sistema con IA aplicada a NPD.',
    NULL, TRUE, 11),

(1, 'Scoring complejidad pacientes (14 dimensiones)',
    'AT_PRESENCIAL', 'SUPERA_ARTICULO', 'P40',
    'Dashboard multiagente con scoring de complejidad: 14 dimensiones, 53 puntos, 4 niveles.',
    'NO MENCIONADO en el artículo. Herramienta única de priorización basada en complejidad farmacoterapéutica.',
    NULL, TRUE, 12),

(1, 'Multi-IA consenso (2-3 modelos)',
    'AT_PRESENCIAL', 'PLANIFICADO', 'Hub',
    'Propuesta Estratégica: enviar mismo paciente a Groq + Gemini + LM Studio, comparar y consensuar.',
    'NO MENCIONADO en el artículo. Concepto de consenso multi-modelo es innovación propia.',
    NULL, TRUE, 13),

(1, 'Radar de inteligencia competitiva con IA',
    'INVESTIGACION', 'SUPERA_ARTICULO', 'Hub',
    'Módulo Radar IA: escaneo automático PubMed, Google News, ClinicalTrials, Semantic Scholar. Clasificación con Groq/Llama.',
    'NO EXISTE en la literatura. SIGFAR Hub es el ÚNICO sistema de farmacia hospitalaria con radar de inteligencia competitiva integrado.',
    NULL, TRUE, 14);
