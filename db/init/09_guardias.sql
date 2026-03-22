-- ═══════════════════════════════════════════════════════════════
-- SIGFAR Hub — Módulo G: Guardias
-- Calendario de guardias del Servicio de Farmacia
-- 15 farmacéuticos × 365 días × 13 tipos de guardia
-- Ejecutar: docker exec -i sigfar-hub-db psql -U sigfar -d sigfar < db/init/09_guardias.sql
-- ═══════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hgu_guardias_intercambios CASCADE;
DROP TABLE IF EXISTS hgu_guardias_calendario CASCADE;
DROP TABLE IF EXISTS hgu_guardias_ruedas CASCADE;
DROP TABLE IF EXISTS hgu_guardias_reglas CASCADE;
DROP TABLE IF EXISTS hgu_guardias_farmaceuticos CASCADE;

-- ═══════════════════════════════════════════════════════════════
-- Tabla 1: Maestro de farmacéuticos del servicio
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_guardias_farmaceuticos (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    codigo              VARCHAR(10) NOT NULL UNIQUE,
    rol                 VARCHAR(20) DEFAULT 'ADJUNTO' CHECK (rol IN (
                            'JEFA','ADJUNTO','RESIDENTE','CONTRATO_VERANO'
                        )),
    activo              BOOLEAN DEFAULT TRUE,
    hace_presenciales   BOOLEAN DEFAULT TRUE,
    factor_localizadas  REAL DEFAULT 1.0,
    email               VARCHAR(200),
    color_hex           VARCHAR(7) DEFAULT '#1a3a2a',
    orden_rueda_gl      INTEGER,
    orden_rueda_gpf     INTEGER,
    orden_rueda_lfe     INTEGER,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_guardias_farm_codigo ON hgu_guardias_farmaceuticos(codigo);
CREATE INDEX idx_guardias_farm_activo ON hgu_guardias_farmaceuticos(activo);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 2: Calendario de guardias (1 fila por día)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_guardias_calendario (
    id                  SERIAL PRIMARY KEY,
    fecha               DATE NOT NULL,
    dia_semana          VARCHAR(2) NOT NULL,
    tipo_dia            VARCHAR(5) NOT NULL CHECK (tipo_dia IN (
                            'LN','LJ','LV','LS','LD','LF','LFE',
                            'PN','PJ','PV','PS','PF','PFE'
                        )),
    es_localizada       BOOLEAN,
    es_presencial       BOOLEAN,
    farmaceutico_id     INTEGER REFERENCES hgu_guardias_farmaceuticos(id),
    estado              VARCHAR(20) DEFAULT 'ASIGNADA' CHECK (estado IN (
                            'ASIGNADA','INTERCAMBIO_PENDIENTE','INTERCAMBIADA','VACANTE'
                        )),
    notas               TEXT,
    anio                INTEGER NOT NULL DEFAULT 2026,
    mes                 INTEGER NOT NULL,
    UNIQUE(fecha)
);

CREATE INDEX idx_guardias_cal_fecha ON hgu_guardias_calendario(fecha);
CREATE INDEX idx_guardias_cal_farm ON hgu_guardias_calendario(farmaceutico_id);
CREATE INDEX idx_guardias_cal_tipo ON hgu_guardias_calendario(tipo_dia);
CREATE INDEX idx_guardias_cal_estado ON hgu_guardias_calendario(estado);
CREATE INDEX idx_guardias_cal_mes ON hgu_guardias_calendario(mes);
CREATE INDEX idx_guardias_cal_anio ON hgu_guardias_calendario(anio);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 3: Intercambios de guardias
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_guardias_intercambios (
    id                  SERIAL PRIMARY KEY,
    solicitante_id      INTEGER REFERENCES hgu_guardias_farmaceuticos(id),
    receptor_id         INTEGER REFERENCES hgu_guardias_farmaceuticos(id),
    guardia_ofrecida_id INTEGER REFERENCES hgu_guardias_calendario(id),
    guardia_pedida_id   INTEGER REFERENCES hgu_guardias_calendario(id),
    motivo              TEXT,
    estado              VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN (
                            'PENDIENTE','ACEPTADA','RECHAZADA','CANCELADA','VALIDADA_JEFA'
                        )),
    validacion_reglas   JSONB,
    cumple_reglas       BOOLEAN,
    fecha_solicitud     TIMESTAMP DEFAULT NOW(),
    fecha_respuesta     TIMESTAMP
);

CREATE INDEX idx_guardias_int_solicitante ON hgu_guardias_intercambios(solicitante_id);
CREATE INDEX idx_guardias_int_receptor ON hgu_guardias_intercambios(receptor_id);
CREATE INDEX idx_guardias_int_estado ON hgu_guardias_intercambios(estado);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 4: Decálogo de reglas parametrizable
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_guardias_reglas (
    id                  SERIAL PRIMARY KEY,
    numero              INTEGER NOT NULL,
    descripcion         TEXT NOT NULL,
    parametros          JSONB,
    activa              BOOLEAN DEFAULT TRUE,
    severidad           VARCHAR(10) DEFAULT 'HARD' CHECK (severidad IN ('HARD','SOFT'))
);

-- ═══════════════════════════════════════════════════════════════
-- Tabla 5: Estado de ruedas rotatorias
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE hgu_guardias_ruedas (
    id                  SERIAL PRIMARY KEY,
    tipo_rueda          VARCHAR(10) NOT NULL CHECK (tipo_rueda IN ('GL','GPF','LFE')),
    orden_actual        INTEGER NOT NULL DEFAULT 1,
    secuencia           JSONB NOT NULL
);

-- ═══════════════════════════════════════════════════════════════
-- SEED: 15 Farmacéuticos del Servicio de Farmacia CHGUV
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_guardias_farmaceuticos
    (nombre, codigo, rol, activo, hace_presenciales, factor_localizadas, color_hex,
     orden_rueda_gl, orden_rueda_gpf, orden_rueda_lfe)
VALUES
    ('Pilar Blasco',       'PBS',     'JEFA',            TRUE, FALSE, 2.0, '#8b5cf6',  1, NULL,  1),
    ('Alejandro Bernalte', 'ABS',     'ADJUNTO',         TRUE, TRUE,  1.0, '#3b82f6',  2,    1,  4),
    ('Pilar Ortega',       'PO',      'ADJUNTO',         TRUE, TRUE,  1.0, '#ef4444',  3,    2,  5),
    ('Xavi Milara',        'XM',      'ADJUNTO',         TRUE, TRUE,  1.0, '#f97316',  4,    3,  2),
    ('Ana Moya',           'AM',      'ADJUNTO',         TRUE, TRUE,  1.0, '#ec4899',  5,    4,  6),
    ('Xelo Jordán',        'XELO',    'ADJUNTO',         TRUE, TRUE,  1.0, '#14b8a6',  6,    5,  3),
    ('Ximo Machí',         'XIMO',    'ADJUNTO',         TRUE, TRUE,  1.0, '#22c55e',  7,    6,  7),
    ('Esperanza Núñez',    'ESPE',    'ADJUNTO',         TRUE, TRUE,  1.0, '#a855f7',  8,    7,  8),
    ('Joan Sanfeliu',      'JOAN',    'ADJUNTO',         TRUE, TRUE,  1.0, '#eab308',  9,    8, 10),
    ('Marta Zaragozá',     'MARTA',   'ADJUNTO',         TRUE, TRUE,  1.0, '#06b6d4', 10,    9,  9),
    ('Sonia Gea',          'SONIA',   'ADJUNTO',         TRUE, TRUE,  1.0, '#f43f5e', 11,   10, 11),
    ('Roberto Maciá',      'ROBERTO', 'ADJUNTO',         TRUE, TRUE,  1.0, '#84cc16', 12,   11, 12),
    ('Manises Así',        'MANISES', 'ADJUNTO',         TRUE, TRUE,  1.0, '#6366f1', 13,   12, NULL),
    ('Contrato Verano 1',  'CV1',     'CONTRATO_VERANO', TRUE, TRUE,  1.0, '#9ca3af', NULL, NULL, NULL),
    ('Contrato Verano 2',  'CV2',     'CONTRATO_VERANO', TRUE, TRUE,  1.0, '#78716c', NULL, NULL, NULL);

-- ═══════════════════════════════════════════════════════════════
-- SEED: 10 Reglas del Decálogo
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_guardias_reglas (numero, descripcion, parametros, activa, severidad)
VALUES
    (1,  '50% GPF adjuntos+residente (sábado, L-X). Distribuir en pares para residentes.',
         '{"pct_min": 50, "dias": ["S","L","M","X"]}', TRUE, 'SOFT'),
    (2,  'Festivos especiales según rueda LFE (5 LFE/año, extra).',
         '{"lfe_por_anio": 5}', TRUE, 'HARD'),
    (3,  'PBS doble GL, 0 presenciales.',
         '{"farmaceutico_codigo": "PBS", "factor_gl": 2.0, "presenciales": 0}', TRUE, 'HARD'),
    (4,  'Ruedas independientes de puentes.',
         NULL, TRUE, 'SOFT'),
    (5,  'Cada R1 hace 4 GPF/mes → 8 GPF/mes con R1.',
         '{"gpf_r1_mes": 4, "gpf_con_r1_mes": 8}', TRUE, 'SOFT'),
    (6,  'Cada adjunto 1-3 guardias/mes (loc o pres).',
         '{"min_mes": 1, "max_mes": 3}', TRUE, 'HARD'),
    (7,  'Evitar GPF+GL consecutivas.',
         NULL, TRUE, 'SOFT'),
    (8,  'Puentes = presencia R2-R4.',
         NULL, TRUE, 'SOFT'),
    (9,  'Navidad excluyente (si Navidad no Año Nuevo). No 2 misma sección.',
         '{"fechas_navidad": ["12-24","12-25"], "fechas_anio_nuevo": ["12-31","01-01"]}', TRUE, 'HARD'),
    (10, 'Rueda GPF correlativa L-S, 1 guardia/mes.',
         '{"max_gpf_mes": 1}', TRUE, 'SOFT');

-- ═══════════════════════════════════════════════════════════════
-- SEED: 3 Ruedas Rotatorias (secuencia 2026)
-- GL  = Guardias Localizadas (14 posiciones, PBS aparece ×2)
-- GPF = Guardias Presenciales (12 posiciones, sin PBS)
-- LFE = Festivos Especiales (12 posiciones)
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_guardias_ruedas (tipo_rueda, orden_actual, secuencia)
VALUES
    ('GL', 1, '[
        {"pos":1, "farmaceutico_id":1,  "codigo":"PBS"},
        {"pos":2, "farmaceutico_id":2,  "codigo":"ABS"},
        {"pos":3, "farmaceutico_id":3,  "codigo":"PO"},
        {"pos":4, "farmaceutico_id":4,  "codigo":"XM"},
        {"pos":5, "farmaceutico_id":5,  "codigo":"AM"},
        {"pos":6, "farmaceutico_id":6,  "codigo":"XELO"},
        {"pos":7, "farmaceutico_id":1,  "codigo":"PBS"},
        {"pos":8, "farmaceutico_id":7,  "codigo":"XIMO"},
        {"pos":9, "farmaceutico_id":8,  "codigo":"ESPE"},
        {"pos":10,"farmaceutico_id":9,  "codigo":"JOAN"},
        {"pos":11,"farmaceutico_id":10, "codigo":"MARTA"},
        {"pos":12,"farmaceutico_id":11, "codigo":"SONIA"},
        {"pos":13,"farmaceutico_id":12, "codigo":"ROBERTO"},
        {"pos":14,"farmaceutico_id":13, "codigo":"MANISES"}
    ]'),
    ('GPF', 1, '[
        {"pos":1, "farmaceutico_id":2,  "codigo":"ABS"},
        {"pos":2, "farmaceutico_id":3,  "codigo":"PO"},
        {"pos":3, "farmaceutico_id":4,  "codigo":"XM"},
        {"pos":4, "farmaceutico_id":5,  "codigo":"AM"},
        {"pos":5, "farmaceutico_id":6,  "codigo":"XELO"},
        {"pos":6, "farmaceutico_id":7,  "codigo":"XIMO"},
        {"pos":7, "farmaceutico_id":8,  "codigo":"ESPE"},
        {"pos":8, "farmaceutico_id":9,  "codigo":"JOAN"},
        {"pos":9, "farmaceutico_id":10, "codigo":"MARTA"},
        {"pos":10,"farmaceutico_id":11, "codigo":"SONIA"},
        {"pos":11,"farmaceutico_id":12, "codigo":"ROBERTO"},
        {"pos":12,"farmaceutico_id":13, "codigo":"MANISES"}
    ]'),
    ('LFE', 1, '[
        {"pos":1, "farmaceutico_id":1,  "codigo":"PBS"},
        {"pos":2, "farmaceutico_id":4,  "codigo":"XM"},
        {"pos":3, "farmaceutico_id":6,  "codigo":"XELO"},
        {"pos":4, "farmaceutico_id":2,  "codigo":"ABS"},
        {"pos":5, "farmaceutico_id":3,  "codigo":"PO"},
        {"pos":6, "farmaceutico_id":5,  "codigo":"AM"},
        {"pos":7, "farmaceutico_id":7,  "codigo":"XIMO"},
        {"pos":8, "farmaceutico_id":8,  "codigo":"ESPE"},
        {"pos":9, "farmaceutico_id":10, "codigo":"MARTA"},
        {"pos":10,"farmaceutico_id":9,  "codigo":"JOAN"},
        {"pos":11,"farmaceutico_id":11, "codigo":"SONIA"},
        {"pos":12,"farmaceutico_id":12, "codigo":"ROBERTO"}
    ]');

-- ═══════════════════════════════════════════════════════════════
-- SEED: 365 días calendario 2026
-- Genera asignaciones rotando por ruedas GL/GPF/LFE
-- Festivos España + Comunitat Valenciana
-- ═══════════════════════════════════════════════════════════════

DO $$
DECLARE
    d DATE;
    dow INT;
    tipo VARCHAR(5);
    farm_id INT;
    dia_char VARCHAR(2);
    -- Ruedas como arrays de farmaceutico_id
    gl  INT[] := ARRAY[1,2,3,4,5,6,1,7,8,9,10,11,12,13];  -- 14 pos (PBS ×2)
    gpf INT[] := ARRAY[2,3,4,5,6,7,8,9,10,11,12,13];       -- 12 pos (sin PBS)
    lfe INT[] := ARRAY[1,4,6,2,3,5,7,8,10,9,11,12];        -- 12 pos
    gl_i  INT := 1;
    gpf_i INT := 1;
    lfe_i INT := 1;
    pres_counter INT := 0;
    fest_counter INT := 0;
    -- Festivos especiales (LFE) 2026
    festivos_esp DATE[] := ARRAY[
        '2026-01-01'::DATE, '2026-01-06'::DATE, '2026-03-19'::DATE,
        '2026-12-25'::DATE, '2026-12-31'::DATE
    ];
    -- Festivos nacionales + autonómicos (LF/PF) 2026
    festivos_norm DATE[] := ARRAY[
        '2026-04-02'::DATE, '2026-04-03'::DATE, '2026-05-01'::DATE,
        '2026-06-24'::DATE, '2026-08-15'::DATE, '2026-10-09'::DATE,
        '2026-10-12'::DATE, '2026-11-01'::DATE, '2026-12-08'::DATE
    ];
BEGIN
    FOR d IN SELECT generate_series('2026-01-01'::DATE, '2026-12-31'::DATE, '1 day')::DATE
    LOOP
        dow := EXTRACT(ISODOW FROM d)::INT;  -- 1=Lun..7=Dom

        CASE dow
            WHEN 1 THEN dia_char := 'L';
            WHEN 2 THEN dia_char := 'M';
            WHEN 3 THEN dia_char := 'X';
            WHEN 4 THEN dia_char := 'J';
            WHEN 5 THEN dia_char := 'V';
            WHEN 6 THEN dia_char := 'S';
            WHEN 7 THEN dia_char := 'D';
        END CASE;

        -- ── Determinar tipo_dia ──────────────────────────────
        IF d = ANY(festivos_esp) THEN
            tipo := 'LFE';
        ELSIF d = ANY(festivos_norm) THEN
            fest_counter := fest_counter + 1;
            IF fest_counter % 2 = 0 THEN tipo := 'PF'; ELSE tipo := 'LF'; END IF;
        ELSIF dow = 7 THEN
            tipo := 'LD';
        ELSIF dow = 6 THEN
            pres_counter := pres_counter + 1;
            IF pres_counter % 3 = 0 THEN tipo := 'PS'; ELSE tipo := 'LS'; END IF;
        ELSIF dow = 5 THEN
            pres_counter := pres_counter + 1;
            IF pres_counter % 3 = 0 THEN tipo := 'PV'; ELSE tipo := 'LV'; END IF;
        ELSIF dow = 4 THEN
            pres_counter := pres_counter + 1;
            IF pres_counter % 3 = 0 THEN tipo := 'PJ'; ELSE tipo := 'LJ'; END IF;
        ELSE  -- Lun, Mar, Mié
            pres_counter := pres_counter + 1;
            IF pres_counter % 8 = 0 THEN tipo := 'PN'; ELSE tipo := 'LN'; END IF;
        END IF;

        -- ── Asignar farmacéutico según rueda ─────────────────
        IF tipo = 'LFE' THEN
            farm_id := lfe[((lfe_i - 1) % 12) + 1];
            lfe_i := lfe_i + 1;
        ELSIF tipo LIKE 'P%' THEN
            farm_id := gpf[((gpf_i - 1) % 12) + 1];
            gpf_i := gpf_i + 1;
        ELSE
            farm_id := gl[((gl_i - 1) % 14) + 1];
            gl_i := gl_i + 1;
        END IF;

        INSERT INTO hgu_guardias_calendario
            (fecha, dia_semana, tipo_dia, es_localizada, es_presencial,
             farmaceutico_id, estado, anio, mes)
        VALUES
            (d, dia_char, tipo, tipo LIKE 'L%', tipo LIKE 'P%',
             farm_id, 'ASIGNADA', 2026, EXTRACT(MONTH FROM d)::INT);
    END LOOP;

    -- ── Contratos verano: CV1 y CV2 cubren guardias jul-ago ──
    -- CV1: 1 localizada + 2 presenciales
    UPDATE hgu_guardias_calendario SET farmaceutico_id = 14
    WHERE id = (SELECT id FROM hgu_guardias_calendario
                WHERE mes = 7 AND tipo_dia LIKE 'L%' AND tipo_dia != 'LFE'
                      AND farmaceutico_id NOT IN (1)
                ORDER BY fecha LIMIT 1);
    UPDATE hgu_guardias_calendario SET farmaceutico_id = 14
    WHERE id IN (SELECT id FROM hgu_guardias_calendario
                 WHERE mes IN (7,8) AND tipo_dia LIKE 'P%'
                       AND farmaceutico_id NOT IN (1)
                 ORDER BY fecha LIMIT 2);

    -- CV2: 1 localizada + 2 presenciales
    UPDATE hgu_guardias_calendario SET farmaceutico_id = 15
    WHERE id = (SELECT id FROM hgu_guardias_calendario
                WHERE mes = 8 AND tipo_dia LIKE 'L%' AND tipo_dia != 'LFE'
                      AND farmaceutico_id NOT IN (1, 14)
                ORDER BY fecha LIMIT 1);
    UPDATE hgu_guardias_calendario SET farmaceutico_id = 15
    WHERE id IN (SELECT id FROM hgu_guardias_calendario
                 WHERE mes IN (7,8) AND tipo_dia LIKE 'P%'
                       AND farmaceutico_id NOT IN (1, 14)
                 ORDER BY fecha DESC LIMIT 2);
END $$;
