-- ═══════════════════════════════════════════════════════════════
-- SIGFAR Hub — Módulo D: Propuestas Estratégicas
-- Tabla + 15 propuestas precargadas cubriendo 6 ejes
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS hgu_propuestas_estrategicas (
    id                  SERIAL PRIMARY KEY,
    titulo              VARCHAR(300) NOT NULL,
    descripcion         TEXT NOT NULL,
    eje                 VARCHAR(20) NOT NULL CHECK (eje IN ('CLINICO','ECONOMICO','LOGISTICO','TECNICO','DIRECTIVO','FORMACION')),
    impacto             VARCHAR(20) DEFAULT 'MEDIO' CHECK (impacto IN ('MUY_ALTO','ALTO','MEDIO','BAJO')),
    estado              VARCHAR(20) DEFAULT 'PROPUESTA' CHECK (estado IN ('PROPUESTA','EN_ANALISIS','EN_DESARROLLO','PILOTO','PRODUCCION','DESCARTADA','GENERADA_IA')),
    preview_descripcion TEXT,
    por_que_hub         TEXT,
    apis_necesarias     TEXT,
    apis_ids            VARCHAR(200),
    ml_recomendado      TEXT,
    ml_ids              VARCHAR(200),
    datos_cruza         TEXT,
    modulos_afectados   VARCHAR(200),
    tiempo_estimado     VARCHAR(50),
    esfuerzo            INTEGER DEFAULT 50,
    impacto_score       INTEGER DEFAULT 50,
    demo_target         VARCHAR(200),
    propuesta_ia        TEXT,
    origen              VARCHAR(20) DEFAULT 'MANUAL' CHECK (origen IN ('MANUAL','GENERADA_IA','RADAR')),
    radar_item_id       INTEGER REFERENCES hgu_radar_items(id),
    favorito            BOOLEAN DEFAULT FALSE,
    prioridad_usuario   VARCHAR(10),
    nota_usuario        TEXT,
    tags                VARCHAR(500),
    fecha_creacion      TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_propuestas_eje ON hgu_propuestas_estrategicas(eje);
CREATE INDEX idx_propuestas_estado ON hgu_propuestas_estrategicas(estado);
CREATE INDEX idx_propuestas_impacto ON hgu_propuestas_estrategicas(impacto);
CREATE INDEX idx_propuestas_favorito ON hgu_propuestas_estrategicas(favorito);
CREATE INDEX idx_propuestas_origen ON hgu_propuestas_estrategicas(origen);

-- ═══════════════════════════════════════════════════════════════
-- SEED: 15 propuestas cubriendo los 6 ejes
-- ═══════════════════════════════════════════════════════════════

INSERT INTO hgu_propuestas_estrategicas
    (titulo, descripcion, eje, impacto, estado, preview_descripcion, por_que_hub, apis_necesarias, ml_recomendado, datos_cruza, modulos_afectados, tiempo_estimado, esfuerzo, impacto_score, demo_target, tags)
VALUES

-- EJE CLINICO (4 propuestas)
(
    'Multi-IA Consenso',
    'Enviar el mismo paciente a 2-3 modelos de IA simultáneamente (Groq, Gemini, LM Studio local) y comparar resultados. Si coinciden → alta confianza. Si discrepan → alerta para revisión manual.',
    'CLINICO', 'MUY_ALTO', 'PROPUESTA',
    'Panel con 3 columnas (Groq/Gemini/Local), cada EM/PRM marcado como CONSENSO (3/3) o REVISAR (2/3 o 1/3), score de confianza global',
    'APEX solo llama a 1 API por Ajax Callback, no tiene procesamiento paralelo, no puede comparar respuestas de 2 LLMs.',
    'Groq, Google Gemini, LM Studio local',
    'Ensemble methods, voting classifier',
    'SIGFAR: datos paciente completos',
    'P15, HUB', '1 semana', 40, 90, 'Substrate AI, Seguridad clínica',
    'multi-ia,consenso,seguridad,llm'
),
(
    'Vigilancia Proactiva 24/7',
    'Job automático cada hora que lee TODOS los pacientes activos de APEX via ORDS, los pasa por IA, y genera alertas priorizadas. Al llegar por la mañana, Hub ya ha analizado los 422 pacientes.',
    'CLINICO', 'MUY_ALTO', 'PROPUESTA',
    'Panel matutino: 4 URGENTES (K+ 6.2 + espironolactona), 18 REVISAR (ATB >7 días), 400 ESTABLES. Tiempo análisis: 14 min. Coste: 0€.',
    'APEX no tiene jobs en background para 422 pacientes, no llama a IA automáticamente, no tiene alertas push proactivas.',
    'ORDS SIGFAR, Groq, APScheduler',
    'Isolation Forest anomalías, LSTM series temporales',
    'SIGFAR: todos los pacientes activos + analíticas + tratamientos',
    'HUB, P15', '2 semanas', 50, 95, 'Substrate AI, Dirección',
    'vigilancia,24h,proactivo,alertas'
),
(
    'Conciliación al alta con IA',
    'Al alta hospitalaria, IA compara tratamiento durante ingreso vs tratamiento previo al ingreso y detecta discrepancias, omisiones y duplicidades automáticamente.',
    'CLINICO', 'ALTO', 'PROPUESTA',
    'Lista de discrepancias: fármaco añadido sin justificación, fármaco domiciliario omitido, dosis cambiada sin documentar',
    'APEX no tiene acceso a la medicación previa del paciente (Abucasis/SIA) ni puede hacer comparación automática.',
    'ORDS SIGFAR, Groq, CIMA',
    'NLP comparación textos',
    'SIGFAR: tratamiento hospitalario + SIA/Abucasis: tratamiento domiciliario',
    'P15, HUB', '3 semanas', 60, 80, 'Comisión Farmacia',
    'conciliacion,alta,discrepancias'
),
(
    'Deprescripción inteligente en ancianos',
    'IA detecta PIM (medicamentos potencialmente inapropiados) con criterios STOPP/START v3 automáticamente en pacientes >65 años.',
    'CLINICO', 'ALTO', 'PROPUESTA',
    'Paciente 78a con 12 fármacos: STOPP detecta 3 PIM (benzodiazepina >4 sem, AINE + anticoagulante, IBP sin indicación). START detecta 1 omisión (vitamina D).',
    'APEX no tiene los criterios STOPP/START codificados. Hub puede aplicarlos vía IA + reglas.',
    'ORDS SIGFAR, CIMA, Groq',
    'LGBM detección PIM, NLP criterios STOPP/START',
    'SIGFAR: pacientes >65, tratamientos, diagnósticos',
    'P15, HUB', '2 semanas', 40, 80, 'Geriatría, Comisión FyT',
    'deprescripcion,stopp-start,ancianos,pim'
),

-- EJE ECONOMICO (3 propuestas)
(
    'Cruce Clínico-Económico',
    'Dashboard que cruza diagnósticos de SIGFAR con costes de GestionAX por paciente y servicio. Muestra top pacientes por coste, fármacos más caros, ahorro potencial por desescalada/switch.',
    'ECONOMICO', 'MUY_ALTO', 'PROPUESTA',
    'Top 5 pacientes por coste/día, ahorro estimado por desescalada antimicrobiana, switch biosimilares detectados automáticamente',
    'APEX no puede cruzar datos de 2 apps diferentes. SIGFAR tiene diagnósticos pero no precios. GestionAX tiene precios pero no diagnósticos. Hub los cruza en tiempo real.',
    'ORDS SIGFAR, ORDS GestionAX, Groq',
    'ElasticNet predicción gasto, Apriori co-prescripción',
    'SIGFAR: diagnósticos, tratamientos + GestionAX: consumos, precios, GFT',
    'HUB', '2 semanas', 30, 95, 'Gerencia, Substrate AI',
    'cruce,costes,ahorro,economico'
),
(
    'Ahorro por desescalada antimicrobiana',
    'Cruzar cultivos (microorganismo sensible) + ATB actual (amplio espectro) + precio → calcular ahorro diario y mensual por desescalada. Ranking de oportunidades de ahorro.',
    'ECONOMICO', 'ALTO', 'PROPUESTA',
    'Paciente Box 7: Meropenem → Amoxicilina-clavulánico (E.coli sensible). Ahorro: 45€/día = 1.350€/mes',
    'GestionAX no tiene datos de cultivos. SIGFAR no tiene precios. Solo Hub puede cruzarlos.',
    'ORDS SIGFAR (PROA), ORDS GestionAX (precios), Groq',
    'Decision tree desescalada',
    'SIGFAR: cultivos, ATB + GestionAX: precios',
    'P43, HUB', '1 semana', 25, 85, 'Gerencia, Comisión ATB',
    'desescalada,antimicrobianos,ahorro,proa'
),
(
    'Switch a biosimilares',
    'Detectar automáticamente pacientes con biológico original donde existe biosimilar aprobado más barato en el catálogo del hospital.',
    'ECONOMICO', 'ALTO', 'PROPUESTA',
    'Detectados 12 pacientes con adalimumab original. Biosimilar disponible. Ahorro potencial: 890€/paciente/mes = 10.680€/mes',
    'Requiere cruzar catálogo GestionAX con prescripciones SIGFAR y precios SNS Nomenclátor.',
    'ORDS GestionAX, ORDS SIGFAR, CIMA, SNS Nomenclátor',
    'Matching algorithm',
    'GestionAX: catálogo + SIGFAR: prescripciones + SNS: precios',
    'HUB', '1 semana', 20, 75, 'Gerencia, Comisión FyT',
    'biosimilares,switch,ahorro'
),

-- EJE LOGISTICO (3 propuestas)
(
    'Predicción de rotura de stock',
    'ML que predice qué medicamentos van a faltar la próxima semana basándose en patrones de consumo y stock actual.',
    'LOGISTICO', 'ALTO', 'PROPUESTA',
    'Alerta: Meropenem 1g stock 45 uds, consumo medio 12/día, rotura estimada en 3.7 días. Acción: pedir urgente.',
    'GestionAX no tiene predicción, solo datos históricos. Hub aplica ML sobre esos datos.',
    'ORDS GestionAX (stock, consumos)',
    'SARIMA/Prophet series temporales, Logistic Regression',
    'GestionAX: stock actual + consumos diarios',
    'HUB', '2 semanas', 40, 80, 'Jefe almacén, Dirección',
    'stock,prediccion,rotura,logistica'
),
(
    'Control de estupefacientes con IA',
    'Detectar patrones anómalos de dispensación de opioides desde armarios automáticos. Alertar sobre dispensaciones fuera de horario, cantidades inusuales o profesionales con patrones sospechosos.',
    'LOGISTICO', 'MUY_ALTO', 'PROPUESTA',
    'Alerta: Enfermera X ha dispensado fentanilo 3 veces en turno noche sin prescripción activa asociada. Patrón anómalo: 2.3 desviaciones estándar sobre la media.',
    'Los armarios solo registran dispensaciones. No analizan patrones ni detectan anomalías. Hub aplica ML sobre los logs.',
    'Hospital: armarios estupefacientes',
    'Isolation Forest anomalías, LSTM series temporales',
    'Hospital: logs dispensación armarios',
    'HUB', '3 semanas', 55, 90, 'Dirección, Inspección',
    'estupefacientes,control,anomalias,opioides'
),
(
    'Alertas de caducidad inteligentes',
    'Predecir qué lotes caducarán sin consumirse y proponer redistribución entre servicios o devolución al proveedor antes de que caduquen.',
    'LOGISTICO', 'ALTO', 'PROPUESTA',
    'Lote X de caspofungina: 20 viales, caducidad 15/04/2026, consumo estimado 8 viales antes de caducidad. Propuesta: redistribuir 12 viales a farmacia de otro centro.',
    'GestionAX registra caducidades pero no predice ni propone acciones.',
    'ORDS GestionAX (stock, caducidades, consumos)',
    'Logistic Regression riesgo caducidad',
    'GestionAX: lotes + caducidades + consumo medio',
    'HUB', '1 semana', 25, 70, 'Jefe almacén',
    'caducidad,lotes,redistribucion'
),

-- EJE TECNICO (1 propuesta)
(
    'Verificación visual de NP con IA',
    'Cámara + red neuronal convolucional que verifica composición y etiquetado de bolsas de NP antes de dispensar. Compara imagen con prescripción.',
    'TECNICO', 'MUY_ALTO', 'PROPUESTA',
    'Fotografía bolsa NP → CNN verifica: volumen correcto, color esperado, etiqueta coincide con prescripción, ausencia de partículas.',
    'Requiere hardware (cámara en cabina). APEX no procesa imágenes. Hub puede ejecutar CNN con TensorFlow.',
    'Hospital: ExactaMix + cámara',
    'CNN/ResNet clasificación imagen',
    'Hospital: imágenes preparaciones + SIGFAR: prescripciones NP',
    'P36, P37', '2 meses', 80, 90, 'Substrate AI',
    'vision,cnn,nutricion-parenteral,verificacion'
),

-- EJE DIRECTIVO (2 propuestas)
(
    'Cuadro de Mandos Dra. Blasco',
    'KPIs SEFH en tiempo real: intervenciones/mes, % aceptación, cobertura validación, ranking farmacéuticos, evolución temporal, benchmarking por servicio. Exportable a PDF/PPTX.',
    'DIRECTIVO', 'ALTO', 'EN_ANALISIS',
    'Dashboard con 4 KPIs arriba, gráfico líneas 12 meses, barras por farmacéutico, tarta por tipo EM/PRM. Botones exportar PDF y PPTX.',
    'APEX tiene gráficos básicos, no dashboards ejecutivos. No genera PDF/PPTX. No cruza SIGFAR+GestionAX.',
    'ORDS SIGFAR, ORDS GestionAX',
    'Prophet forecasting KPIs',
    'SIGFAR: intervenciones, EM/PRM + GestionAX: consumos',
    'HUB', '2 semanas', 35, 80, 'Dra. Blasco, Dirección',
    'kpi,dashboard,directivo,sefh'
),
(
    'Informe automático para comisiones',
    'Generación automática de informes PDF para Comisión de Farmacia y Terapéutica con datos actualizados, gráficos y narrativa generada por IA.',
    'DIRECTIVO', 'ALTO', 'PROPUESTA',
    'PDF de 10 páginas: resumen ejecutivo (IA), tabla indicadores, gráficos evolución, top intervenciones, propuestas para próximo trimestre.',
    'APEX no genera PDFs con narrativa. Hub usa Groq para redactar + ReportLab/WeasyPrint para PDF.',
    'ORDS SIGFAR, ORDS GestionAX, Groq',
    'NLG (Natural Language Generation)',
    'SIGFAR + GestionAX: todo',
    'HUB', '2 semanas', 40, 75, 'Comisión FyT',
    'informes,pdf,comision,automatico'
),

-- EJE FORMACION (1 propuesta)
(
    'Simulador FIR',
    'Generador de casos clínicos ficticios basados en patrones reales para formación de residentes. FIR practica, Hub evalúa y da feedback comparando con IA + guías.',
    'FORMACION', 'ALTO', 'PROPUESTA',
    'Caso: Mujer 68a, Cr 2.8, neumonía + FA + DM2, piperacilina-tazo + digoxina + metformina + enoxaparina. FIR escribe EM/PRM → Hub compara con IA → Score: 4/6 detectados.',
    'APEX no tiene generador de casos ni interfaz de evaluación. Mezclaría datos reales con formación.',
    'Groq/Gemini, CIMA, PubMed',
    NULL,
    'SIGFAR: patrones de casos (anonimizados)',
    'HUB', '3 semanas', 45, 70, 'Convenio UV, Docencia',
    'formacion,fir,simulador,casos-clinicos'
);
