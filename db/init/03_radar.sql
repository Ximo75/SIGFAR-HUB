-- ════════════════════════════════════════════════════════════════
-- SIGFAR Hub — Radar IA — DDL + Seed queries
-- Ejecutar: docker exec -i sigfar-hub-db psql -U sigfar -d sigfar < db/init/03_radar.sql
-- ════════════════════════════════════════════════════════════════

-- ─── Tabla principal: ítems del radar ───
CREATE TABLE hgu_radar_items (
    id                  SERIAL PRIMARY KEY,
    titulo              VARCHAR(500) NOT NULL,
    resumen             TEXT,
    resumen_ia          TEXT,
    como_en_sigfar_hub  TEXT,
    estado_sigfar_hub   VARCHAR(20) DEFAULT 'NUEVO'
                        CHECK (estado_sigfar_hub IN ('IMPLEMENTADO','PARCIAL','PLANIFICADO','NUEVO')),
    modulo_sigfar       VARCHAR(100),
    categoria           VARCHAR(50) NOT NULL
                        CHECK (categoria IN ('VALIDACION','FARMACOCINETICA','NUTRICION','PROA',
                                             'ELABORACION','STOCK_LOGISTICA','ROBOTICA',
                                             'FARMACOECONOMIA','CUADRO_MANDOS','REGULACION')),
    subcategoria        VARCHAR(100),
    relevancia          INTEGER DEFAULT 50 CHECK (relevancia BETWEEN 0 AND 100),
    pais                VARCHAR(5),
    institucion         VARCHAR(200),
    url_original        VARCHAR(1000) NOT NULL,
    url_extra_1         VARCHAR(1000),
    url_extra_2         VARCHAR(1000),
    url_extra_3         VARCHAR(1000),
    fuente              VARCHAR(50) CHECK (fuente IN ('PUBMED','GOOGLE_NEWS','CLINICALTRIALS','SEMANTIC')),
    fuente_id           VARCHAR(100),
    fecha_publicacion   DATE,
    fecha_scan          TIMESTAMP DEFAULT NOW(),
    fecha_leido         TIMESTAMP,
    leido               BOOLEAN DEFAULT FALSE,
    favorito            BOOLEAN DEFAULT FALSE,
    archivado           BOOLEAN DEFAULT FALSE,
    nota_usuario        TEXT,
    prioridad_usuario   VARCHAR(10) CHECK (prioridad_usuario IN ('ALTA','MEDIA','BAJA')),
    tags                VARCHAR(500),
    json_raw            JSONB,
    json_ia             JSONB,
    UNIQUE(fuente, fuente_id)
);

-- ─── Queries de búsqueda predefinidas ───
CREATE TABLE hgu_radar_queries (
    id          SERIAL PRIMARY KEY,
    fuente      VARCHAR(50) NOT NULL CHECK (fuente IN ('PUBMED','GOOGLE_NEWS','CLINICALTRIALS','SEMANTIC')),
    query_text  VARCHAR(500) NOT NULL,
    categoria   VARCHAR(50) CHECK (categoria IN ('VALIDACION','FARMACOCINETICA','NUTRICION','PROA',
                                                  'ELABORACION','STOCK_LOGISTICA','ROBOTICA',
                                                  'FARMACOECONOMIA','CUADRO_MANDOS','REGULACION')),
    activo      BOOLEAN DEFAULT TRUE,
    descripcion VARCHAR(200)
);

-- ─── Log de ejecuciones ───
CREATE TABLE hgu_radar_log (
    id               SERIAL PRIMARY KEY,
    fecha_ejecucion  TIMESTAMP DEFAULT NOW(),
    tipo             VARCHAR(20) CHECK (tipo IN ('AUTOMATICO','MANUAL')),
    fuentes_ok       INTEGER DEFAULT 0,
    fuentes_error    INTEGER DEFAULT 0,
    items_nuevos     INTEGER DEFAULT 0,
    items_duplicados INTEGER DEFAULT 0,
    duracion_seg     NUMERIC,
    detalles         JSONB
);

-- ─── Índices ───
CREATE INDEX idx_radar_categoria ON hgu_radar_items(categoria);
CREATE INDEX idx_radar_favorito ON hgu_radar_items(favorito);
CREATE INDEX idx_radar_fecha_pub ON hgu_radar_items(fecha_publicacion DESC);
CREATE INDEX idx_radar_relevancia ON hgu_radar_items(relevancia DESC);
CREATE INDEX idx_radar_archivado ON hgu_radar_items(archivado);
CREATE INDEX idx_radar_fuente ON hgu_radar_items(fuente);

-- ════════════════════════════════════════════════════════════════
-- Seed: 28 queries iniciales (10 categorías × múltiples fuentes)
-- ════════════════════════════════════════════════════════════════

INSERT INTO hgu_radar_queries (fuente, query_text, categoria, descripcion) VALUES
-- VALIDACION (3)
('PUBMED',          'artificial intelligence hospital pharmacy medication error',           'VALIDACION',       'IA para detección de errores de medicación'),
('GOOGLE_NEWS',     'inteligencia artificial farmacia hospitalaria',                        'VALIDACION',       'Noticias IA en farmacia hospitalaria (ES)'),
('SEMANTIC',        'drug interaction detection natural language processing',               'VALIDACION',       'NLP para detección de interacciones'),

-- FARMACOCINETICA (3)
('PUBMED',          'machine learning drug dosing pharmacokinetics bayesian',               'FARMACOCINETICA',  'ML para dosificación y PK Bayesiana'),
('CLINICALTRIALS',  'machine learning medication dosing',                                   'FARMACOCINETICA',  'Ensayos de ML en dosificación'),
('SEMANTIC',        'model-informed precision dosing pharmacokinetics artificial intelligence', 'FARMACOCINETICA', 'MIPD con IA'),

-- NUTRICION (3)
('PUBMED',          'artificial intelligence parenteral nutrition clinical',                'NUTRICION',        'IA en nutrición parenteral'),
('PUBMED',          'machine learning nutritional screening hospital',                      'NUTRICION',        'ML para cribado nutricional'),
('GOOGLE_NEWS',     'inteligencia artificial nutricion parenteral hospital',                'NUTRICION',        'Noticias NP con IA (ES)'),

-- PROA (3)
('PUBMED',          'antimicrobial stewardship artificial intelligence machine learning',   'PROA',             'IA en stewardship antimicrobiano'),
('CLINICALTRIALS',  'artificial intelligence antimicrobial stewardship',                    'PROA',             'Ensayos PROA con IA'),
('SEMANTIC',        'antibiotic resistance prediction machine learning hospital',           'PROA',             'Predicción resistencias con ML'),

-- ELABORACION (2)
('PUBMED',          'computer vision pharmacy compounding preparation',                     'ELABORACION',      'Visión artificial en elaboración'),
('SEMANTIC',        'automated compounding quality control pharmacy artificial intelligence', 'ELABORACION',     'Control calidad elaboración con IA'),

-- STOCK_LOGISTICA (3)
('PUBMED',          'pharmacy inventory management AI demand prediction',                   'STOCK_LOGISTICA',  'IA en gestión de stock farmacia'),
('GOOGLE_NEWS',     'inteligencia artificial gestión stock hospital farmacia',              'STOCK_LOGISTICA',  'Noticias gestión stock (ES)'),
('SEMANTIC',        'hospital pharmacy supply chain machine learning demand forecasting',   'STOCK_LOGISTICA',  'ML para predicción de demanda'),

-- ROBOTICA (3)
('PUBMED',          'robotic dispensing hospital pharmacy automation',                      'ROBOTICA',         'Dispensación robótica en farmacia'),
('GOOGLE_NEWS',     'robot dispensación farmacia hospital',                                 'ROBOTICA',         'Noticias robots farmacia (ES)'),
('GOOGLE_NEWS',     'AI hospital pharmacy automation 2026',                                'ROBOTICA',         'Automatización farmacia (EN)'),

-- FARMACOECONOMIA (2)
('PUBMED',          'pharmacoeconomics artificial intelligence cost effectiveness',         'FARMACOECONOMIA',  'Farmacoeconomía con IA'),
('SEMANTIC',        'biosimilar switching economic impact artificial intelligence',         'FARMACOECONOMIA',  'Impacto económico biosimilares + IA'),

-- CUADRO_MANDOS (2)
('PUBMED',          'clinical decision support dashboard pharmacy KPI',                    'CUADRO_MANDOS',    'Dashboards y KPIs farmacia'),
('SEMANTIC',        'hospital pharmacy artificial intelligence workflow automation dashboard', 'CUADRO_MANDOS', 'Automatización flujos y dashboards'),

-- REGULACION (4)
('PUBMED',          'software medical device AI regulation SaMD',                          'REGULACION',       'Regulación SaMD/IA'),
('GOOGLE_NEWS',     'FDA AI medical device approved 2026',                                 'REGULACION',       'Aprobaciones FDA IA (EN)'),
('GOOGLE_NEWS',     'EU AI Act dispositivo médico inteligencia artificial',                'REGULACION',       'EU AI Act dispositivos médicos (ES)'),
('CLINICALTRIALS',  'artificial intelligence pharmacy',                                    'REGULACION',       'Ensayos IA farmacia general');
