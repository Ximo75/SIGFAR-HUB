-- ════════════════════════════════════════════════════════════════
-- SIGFAR PostgreSQL — DDL Core (traducción de Oracle HGU_*)
-- Se ejecuta automáticamente al crear el contenedor
-- ════════════════════════════════════════════════════════════════

-- Pacientes
CREATE TABLE hgu_pacientes (
    id_episodio     SERIAL PRIMARY KEY,
    nhc             VARCHAR(20),
    nombre          VARCHAR(200),
    fecha_nac       DATE,
    sexo            VARCHAR(10),
    peso            NUMERIC(6,2),
    talla           NUMERIC(5,1),
    ubicacion       VARCHAR(100),
    unidad          VARCHAR(50),
    cama            VARCHAR(20),
    diagnostico     TEXT,
    estado_p        VARCHAR(20) DEFAULT 'ACTIVO',
    fecha_estado_p  TIMESTAMP DEFAULT NOW(),
    fecha_ingreso   DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Evoluciones
CREATE TABLE hgu_evolucion (
    id_ev           SERIAL PRIMARY KEY,
    id_episodio     INTEGER REFERENCES hgu_pacientes(id_episodio),
    fecha           DATE,
    evolucion       TEXT,
    plan            TEXT,
    erprm_json      TEXT,
    prompt_id       INTEGER,
    modelo_ia       VARCHAR(50),
    tokens_in       INTEGER,
    tokens_out      INTEGER,
    tiempo_ms       INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Tratamientos
CREATE TABLE hgu_tratamientos (
    trat_id         SERIAL PRIMARY KEY,
    id_episodio     INTEGER REFERENCES hgu_pacientes(id_episodio),
    id_ev           INTEGER REFERENCES hgu_evolucion(id_ev),
    pauta           TEXT,
    principio_activo VARCHAR(200),
    via             VARCHAR(50),
    dosis           VARCHAR(100),
    frecuencia      VARCHAR(100),
    fecha_inicio    DATE,
    fecha_fin       DATE,
    validacion      VARCHAR(5) DEFAULT 'N',
    validacion_usr  VARCHAR(50),
    validacion_ts   TIMESTAMP,
    atc_codigo      VARCHAR(20),
    atc_nombre      VARCHAR(200),
    codigo_articulo VARCHAR(50),
    nregistro       VARCHAR(20),
    sistema_terapeutico VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- EM/PRM
CREATE TABLE hgu_emprm_lineas (
    codigo          SERIAL PRIMARY KEY,
    id_ev           INTEGER REFERENCES hgu_evolucion(id_ev),
    id_episodio     INTEGER REFERENCES hgu_pacientes(id_episodio),
    farmaco         VARCHAR(200),
    tipo            VARCHAR(50),
    clasificacion   VARCHAR(100),
    gravedad        VARCHAR(50),
    descripcion     TEXT,
    accion          TEXT,
    justificacion   TEXT,
    bibliografia    TEXT,
    decision        VARCHAR(5) DEFAULT 'P',
    comunicada      VARCHAR(20),
    aceptada        VARCHAR(20),
    coincidente     VARCHAR(5) DEFAULT 'N',
    origen          VARCHAR(20) DEFAULT 'GPT',
    usr_decision    VARCHAR(50),
    fecha           DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Prompts
CREATE TABLE hgu_prompts (
    id_prompt       SERIAL PRIMARY KEY,
    fecha           DATE DEFAULT CURRENT_DATE,
    version         VARCHAR(50),
    objetivo        VARCHAR(4000),
    prompt          TEXT,
    farmaceutico    VARCHAR(50),
    estado          VARCHAR(50) DEFAULT 'Inactivo',
    contenido       VARCHAR(4000),
    equipo          VARCHAR(50),
    planta          VARCHAR(50),
    es_nuevo        CHAR(1) DEFAULT 'Y' CHECK (es_nuevo IN ('Y','N')),
    contenido_nl    TEXT
);

-- Analíticas
CREATE TABLE hgu_analiticas (
    id_analitica    SERIAL PRIMARY KEY,
    id_episodio     INTEGER REFERENCES hgu_pacientes(id_episodio),
    fecha           TIMESTAMP,
    parametro       VARCHAR(100),
    valor           VARCHAR(50),
    unidad          VARCHAR(50),
    rango_min       NUMERIC,
    rango_max       NUMERIC,
    estado          VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Score seguimiento
CREATE TABLE hgu_score_seguimiento (
    id_score        SERIAL PRIMARY KEY,
    nhc             VARCHAR(20),
    id_episodio     INTEGER,
    score_total     INTEGER,
    prioridad       VARCHAR(20),
    score_json      TEXT,
    unidad          VARCHAR(50),
    fecha_ref       DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- POF (Plan Optimización Farmacoterapéutica)
CREATE TABLE hgu_pof (
    id_pof          SERIAL PRIMARY KEY,
    nhc             VARCHAR(20),
    id_episodio     INTEGER,
    estado          VARCHAR(20) DEFAULT 'BORRADOR',
    resumen         TEXT,
    propuesta       TEXT,
    datos_json      TEXT,
    score_total     INTEGER,
    prioridad       VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- POF Secciones
CREATE TABLE hgu_pof_secciones (
    id_seccion      SERIAL PRIMARY KEY,
    id_pof          INTEGER REFERENCES hgu_pof(id_pof),
    cod             VARCHAR(30),
    num             INTEGER,
    titulo          VARCHAR(200),
    contenido       TEXT,
    datos_json      TEXT,
    editado         CHAR(1) DEFAULT 'N'
);

-- Audit validación
CREATE TABLE hgu_audit_validacion (
    id_audit        SERIAL PRIMARY KEY,
    id_episodio     INTEGER,
    accion          VARCHAR(50),
    usuario         VARCHAR(50),
    fecha           TIMESTAMP DEFAULT NOW(),
    detalle         TEXT
);

-- Catálogo hospital
CREATE TABLE hgu_catalogo_hospital (
    codigo_articulo VARCHAR(50) PRIMARY KEY,
    descripcion     TEXT,
    principio_activo VARCHAR(500),
    pa_normalizado  VARCHAR(200),
    dosis_num       NUMERIC,
    dosis_unidad    VARCHAR(50),
    via_normalizada VARCHAR(50),
    codigo_nacional VARCHAR(20),
    tipo            VARCHAR(50),
    nregistro       VARCHAR(20),
    dci             VARCHAR(200),
    forma_farmaceutica VARCHAR(200),
    atc_codigo      VARCHAR(20),
    comerc          BOOLEAN,
    cima_estado     VARCHAR(30)
);

-- LLM Log
CREATE TABLE hgu_llm_log (
    id_log          SERIAL PRIMARY KEY,
    modelo          VARCHAR(50),
    endpoint        VARCHAR(200),
    tokens_in       INTEGER,
    tokens_out      INTEGER,
    tiempo_ms       INTEGER,
    usuario         VARCHAR(50),
    pagina          VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════════
-- Índices
-- ════════════════════════════════════════════════════════════════
CREATE INDEX idx_pac_estado ON hgu_pacientes(estado_p);
CREATE INDEX idx_pac_nhc ON hgu_pacientes(nhc);
CREATE INDEX idx_evol_episodio ON hgu_evolucion(id_episodio);
CREATE INDEX idx_trat_episodio ON hgu_tratamientos(id_episodio);
CREATE INDEX idx_emprm_episodio ON hgu_emprm_lineas(id_episodio);
CREATE INDEX idx_emprm_decision ON hgu_emprm_lineas(decision);
CREATE INDEX idx_anal_episodio ON hgu_analiticas(id_episodio);
CREATE INDEX idx_audit_fecha ON hgu_audit_validacion(fecha);
