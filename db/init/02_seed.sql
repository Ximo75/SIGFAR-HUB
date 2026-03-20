-- ════════════════════════════════════════════════════════════════
-- SIGFAR — Datos de prueba (pacientes anonimizados ficticios)
-- ════════════════════════════════════════════════════════════════

INSERT INTO hgu_pacientes (nhc, nombre, fecha_nac, sexo, peso, talla, ubicacion, unidad, cama, diagnostico, estado_p, fecha_ingreso) VALUES
('TEST001', 'PACIENTE DEMO 1', '1952-03-15', 'M', 78.5, 172, 'UCI - Box 3', 'UCI', 'B03', 'Sepsis abdominal postquirúrgica. Peritonitis secundaria. DM2. HTA. IRC estadio 3b.', 'ACTIVO', CURRENT_DATE - 5),
('TEST002', 'PACIENTE DEMO 2', '1968-07-22', 'F', 62.0, 158, 'UCI - Box 7', 'UCI', 'B07', 'Neumonía bilateral por SARM. EPOC Gold III. FA anticoagulada.', 'ACTIVO', CURRENT_DATE - 3),
('TEST003', 'PACIENTE DEMO 3', '1945-11-08', 'M', 92.3, 168, 'Cirugía 4ª - Cama 412', 'CIRUGIA', '412', 'Pancreatitis aguda grave Balthazar E. Nutrición parenteral. Obesidad grado I.', 'ACTIVO', CURRENT_DATE - 8),
('TEST004', 'PACIENTE DEMO 4', '1979-01-30', 'F', 55.0, 165, 'Medicina Interna 3ª - Cama 315', 'MI', '315', 'Endocarditis por E. faecalis sobre válvula mitral nativa. Tratamiento con ampicilina + ceftriaxona.', 'ACTIVO', CURRENT_DATE - 12),
('TEST005', 'PACIENTE DEMO 5', '1960-09-14', 'M', 70.0, 175, 'UCI - Box 1', 'UCI', 'B01', 'TCE grave. Craniectomía descompresiva. Estatus epiléptico controlado. NP mixta.', 'ACTIVO', CURRENT_DATE - 2);

-- Tratamientos paciente 1 (sepsis UCI)
INSERT INTO hgu_tratamientos (id_episodio, pauta, principio_activo, via, dosis, frecuencia, fecha_inicio) VALUES
(1, 'MEROPENEM 1G/8H IV', 'MEROPENEM', 'IV', '1g', 'c/8h', CURRENT_DATE - 5),
(1, 'VANCOMICINA 1G/12H IV', 'VANCOMICINA', 'IV', '1g', 'c/12h', CURRENT_DATE - 5),
(1, 'NORADRENALINA 0.15 MCG/KG/MIN IV', 'NORADRENALINA', 'IV', '0.15 mcg/kg/min', 'perfusión continua', CURRENT_DATE - 5),
(1, 'INSULINA ACTRAPID PERFUSION IV', 'INSULINA REGULAR', 'IV', 'según pauta', 'perfusión continua', CURRENT_DATE - 5),
(1, 'ENOXAPARINA 40MG/24H SC', 'ENOXAPARINA', 'SC', '40mg', 'c/24h', CURRENT_DATE - 4),
(1, 'OMEPRAZOL 40MG/24H IV', 'OMEPRAZOL', 'IV', '40mg', 'c/24h', CURRENT_DATE - 5);

-- Tratamientos paciente 2 (SARM)
INSERT INTO hgu_tratamientos (id_episodio, pauta, principio_activo, via, dosis, frecuencia, fecha_inicio) VALUES
(2, 'LINEZOLID 600MG/12H IV', 'LINEZOLID', 'IV', '600mg', 'c/12h', CURRENT_DATE - 3),
(2, 'PIPERACILINA/TAZOBACTAM 4G/0.5G/8H IV', 'PIPERACILINA/TAZOBACTAM', 'IV', '4g/0.5g', 'c/8h', CURRENT_DATE - 3),
(2, 'SALBUTAMOL 2.5MG/6H NEB', 'SALBUTAMOL', 'INH', '2.5mg', 'c/6h', CURRENT_DATE - 3),
(2, 'ACENOCUMAROL 2MG/24H VO', 'ACENOCUMAROL', 'VO', '2mg', 'c/24h', CURRENT_DATE - 3);

-- Tratamientos paciente 4 (endocarditis)
INSERT INTO hgu_tratamientos (id_episodio, pauta, principio_activo, via, dosis, frecuencia, fecha_inicio) VALUES
(4, 'AMPICILINA 2G/4H IV', 'AMPICILINA', 'IV', '2g', 'c/4h', CURRENT_DATE - 12),
(4, 'CEFTRIAXONA 2G/12H IV', 'CEFTRIAXONA', 'IV', '2g', 'c/12h', CURRENT_DATE - 12),
(4, 'GENTAMICINA 240MG/24H IV', 'GENTAMICINA', 'IV', '240mg', 'c/24h', CURRENT_DATE - 10);

-- Analíticas paciente 1
INSERT INTO hgu_analiticas (id_episodio, fecha, parametro, valor, unidad, rango_min, rango_max, estado) VALUES
(1, NOW() - INTERVAL '1 day', 'Creatinina', '2.1', 'mg/dL', 0.6, 1.2, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'Urea', '85', 'mg/dL', 10, 50, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'PCR', '18.5', 'mg/dL', 0, 0.5, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'Procalcitonina', '4.2', 'ng/mL', 0, 0.5, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'Potasio', '3.7', 'mEq/L', 3.5, 5.0, 'OK'),
(1, NOW() - INTERVAL '1 day', 'Sodio', '141', 'mEq/L', 136, 145, 'OK'),
(1, NOW() - INTERVAL '1 day', 'Glucosa', '185', 'mg/dL', 70, 110, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'Albúmina', '2.1', 'g/dL', 3.5, 5.0, 'BAJO'),
(1, NOW() - INTERVAL '1 day', 'Hemoglobina', '9.8', 'g/dL', 12, 16, 'BAJO'),
(1, NOW() - INTERVAL '1 day', 'Leucocitos', '18500', '/µL', 4000, 11000, 'ALTO'),
(1, NOW() - INTERVAL '1 day', 'Plaquetas', '95000', '/µL', 150000, 400000, 'BAJO');

-- Analíticas paciente 2
INSERT INTO hgu_analiticas (id_episodio, fecha, parametro, valor, unidad, rango_min, rango_max, estado) VALUES
(2, NOW() - INTERVAL '1 day', 'Vancomicina valle', '12.5', 'mg/L', 10, 20, 'OK'),
(2, NOW() - INTERVAL '1 day', 'PCR', '8.2', 'mg/dL', 0, 0.5, 'ALTO'),
(2, NOW() - INTERVAL '1 day', 'Creatinina', '0.9', 'mg/dL', 0.6, 1.2, 'OK'),
(2, NOW() - INTERVAL '1 day', 'INR', '2.8', '', 2.0, 3.0, 'OK');

-- Prompt activo
INSERT INTO hgu_prompts (version, objetivo, farmaceutico, estado, equipo, planta, es_nuevo, contenido_nl) VALUES
('v1.0', 'Validación farmacoterapéutica UCI', 'XIMO', 'Activo', 'UNAF', 'UCI', 'N',
'Prompt para validación de prescripciones en UCI con detección de EM/PRM, ajuste renal, interacciones y revisión de dosis.');

-- Auditorías de ejemplo
INSERT INTO hgu_audit_validacion (id_episodio, accion, usuario, fecha) VALUES
(1, 'VALIDAR', 'XIMO', NOW() - INTERVAL '2 days'),
(2, 'VALIDAR', 'XIMO', NOW() - INTERVAL '1 day'),
(1, 'VALIDAR', 'MARIA', NOW() - INTERVAL '1 day'),
(3, 'VALIDAR', 'CARLOS', NOW() - INTERVAL '3 days'),
(4, 'VALIDAR', 'XIMO', NOW());

-- EM/PRM de ejemplo
INSERT INTO hgu_emprm_lineas (id_ev, id_episodio, farmaco, tipo, clasificacion, gravedad, descripcion, accion, decision, origen, fecha) VALUES
(NULL, 1, 'ENOXAPARINA', 'PRM', 'Dosificación', 'MODERADA', 'Enoxaparina 40mg/24h en paciente con Cr 2.1 mg/dL (FG estimado ~32 mL/min). Riesgo de acumulación.', 'Reducir a 20mg/24h o monitorizar anti-Xa', 'P', 'GPT', CURRENT_DATE),
(NULL, 1, 'VANCOMICINA', 'PRM', 'Monitorización', 'LEVE', 'Vancomicina sin nivel valle solicitado tras 3 días de tratamiento.', 'Solicitar nivel valle pre-4ª dosis', 'P', 'GPT', CURRENT_DATE),
(NULL, 4, 'GENTAMICINA', 'PRM', 'Dosificación', 'GRAVE', 'Gentamicina 240mg/24h en régimen extendido para endocarditis. Las guías IDSA recomiendan gentamicina solo en combinación corta (2 semanas) y monitorizar función renal.', 'Revisar duración y solicitar niveles', 'P', 'GPT', CURRENT_DATE);
