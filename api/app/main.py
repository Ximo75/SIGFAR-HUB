"""
SIGFAR API — FastAPI Backend
Plataforma de Gestión Farmacéutica Asistida por IA
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import httpx
from datetime import date
from contextlib import asynccontextmanager

# ═══════════════════════════════════════
# Config
# ═══════════════════════════════════════
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sigfar:sigfar2026@db:5432/sigfar")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
APEX_SIGFAR_URL = os.getenv("APEX_SIGFAR_URL", "")
APEX_GESTIONAX_URL = os.getenv("APEX_GESTIONAX_URL", "")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ═══════════════════════════════════════
# App
# ═══════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="SIGFAR Hub API",
    description="Hub de Integración Farmacéutica con IA — CHGUV",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════
# Health
# ═══════════════════════════════════════
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "SIGFAR API", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        return {"db": "ok", "value": result.scalar()}

# ═══════════════════════════════════════
# Pacientes
# ═══════════════════════════════════════
@app.get("/api/pacientes", tags=["Pacientes"])
async def get_pacientes(estado: str = "ACTIVO"):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_pacientes WHERE estado_p = :estado ORDER BY fecha_ingreso DESC"),
            {"estado": estado}
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]

@app.get("/api/pacientes/{id_episodio}", tags=["Pacientes"])
async def get_paciente(id_episodio: int):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_pacientes WHERE id_episodio = :id"),
            {"id": id_episodio}
        )
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "Paciente no encontrado")
        return dict(row)

# ═══════════════════════════════════════
# Tratamientos
# ═══════════════════════════════════════
@app.get("/api/pacientes/{id_episodio}/tratamientos", tags=["Tratamientos"])
async def get_tratamientos(id_episodio: int):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_tratamientos WHERE id_episodio = :id ORDER BY fecha_inicio DESC"),
            {"id": id_episodio}
        )
        return [dict(r) for r in result.mappings().all()]

# ═══════════════════════════════════════
# Analíticas
# ═══════════════════════════════════════
@app.get("/api/pacientes/{id_episodio}/analiticas", tags=["Analíticas"])
async def get_analiticas(id_episodio: int):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_analiticas WHERE id_episodio = :id ORDER BY fecha DESC"),
            {"id": id_episodio}
        )
        return [dict(r) for r in result.mappings().all()]

# ═══════════════════════════════════════
# EM/PRM
# ═══════════════════════════════════════
@app.get("/api/pacientes/{id_episodio}/emprm", tags=["EM/PRM"])
async def get_emprm(id_episodio: int):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_emprm_lineas WHERE id_episodio = :id ORDER BY fecha DESC"),
            {"id": id_episodio}
        )
        return [dict(r) for r in result.mappings().all()]

@app.get("/api/emprm/pendientes", tags=["EM/PRM"])
async def get_emprm_pendientes():
    async with async_session() as session:
        result = await session.execute(
            text("SELECT e.*, p.nhc, p.nombre, p.ubicacion FROM hgu_emprm_lineas e JOIN hgu_pacientes p ON p.id_episodio = e.id_episodio WHERE e.decision = 'P' ORDER BY CASE UPPER(e.gravedad) WHEN 'GRAVE' THEN 1 WHEN 'MODERADA' THEN 2 ELSE 3 END")
        )
        return [dict(r) for r in result.mappings().all()]

# ═══════════════════════════════════════
# Stats (Dashboard Home)
# ═══════════════════════════════════════
@app.get("/api/stats", tags=["Dashboard"])
async def get_stats():
    async with async_session() as session:
        pac = await session.execute(text("SELECT COUNT(*) FROM hgu_pacientes WHERE estado_p = 'ACTIVO'"))
        pof = await session.execute(text("SELECT COUNT(*) FROM hgu_evolucion WHERE plan IS NOT NULL AND fecha >= date_trunc('month', CURRENT_DATE)"))
        emprm = await session.execute(text("SELECT COUNT(*) FROM hgu_emprm_lineas WHERE decision = 'P'"))
        emprm_c = await session.execute(text("SELECT COUNT(*) FROM hgu_emprm_lineas WHERE decision = 'P' AND UPPER(COALESCE(gravedad, '')) IN ('ALTA','CRITICA','GRAVE')"))
        val = await session.execute(text("SELECT COUNT(*) FROM hgu_audit_validacion WHERE accion = 'VALIDAR' AND fecha >= date_trunc('month', CURRENT_DATE)"))

        return {
            "pacientes_activos": pac.scalar(),
            "pof_mes": pof.scalar(),
            "emprm_pendientes": emprm.scalar(),
            "emprm_criticos": emprm_c.scalar(),
            "validaciones_mes": val.scalar()
        }

# ═══════════════════════════════════════
# Prompts
# ═══════════════════════════════════════
@app.get("/api/prompts", tags=["Prompts"])
async def get_prompts():
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM hgu_prompts ORDER BY fecha DESC"))
        return [dict(r) for r in result.mappings().all()]

# ═══════════════════════════════════════
# SEND2GPT (simplificado)
# ═══════════════════════════════════════
@app.post("/api/send2gpt/{id_episodio}", tags=["IA"])
async def send2gpt(id_episodio: int):
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-placeholder":
        raise HTTPException(400, "OPENAI_API_KEY no configurada. Añádela en .env")

    async with async_session() as session:
        # Paciente
        pac = await session.execute(
            text("SELECT * FROM hgu_pacientes WHERE id_episodio = :id"), {"id": id_episodio}
        )
        paciente = pac.mappings().first()
        if not paciente:
            raise HTTPException(404, "Paciente no encontrado")

        # Edad
        edad = None
        if paciente.get('fecha_nac'):
            nacimiento = paciente['fecha_nac']
            if isinstance(nacimiento, str):
                nacimiento = date.fromisoformat(nacimiento)
            hoy = date.today()
            edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

        # Tratamientos
        trats = await session.execute(
            text("SELECT pauta, principio_activo, via, dosis, frecuencia FROM hgu_tratamientos WHERE id_episodio = :id"),
            {"id": id_episodio}
        )
        tratamientos = [dict(r) for r in trats.mappings().all()]

        # Analíticas
        anals = await session.execute(
            text("SELECT parametro, valor, unidad, estado FROM hgu_analiticas WHERE id_episodio = :id ORDER BY fecha DESC LIMIT 20"),
            {"id": id_episodio}
        )
        analiticas = [dict(r) for r in anals.mappings().all()]

        # Prompt activo
        prompt_r = await session.execute(
            text("SELECT prompt FROM hgu_prompts WHERE estado = 'Activo' LIMIT 1")
        )
        prompt_row = prompt_r.mappings().first()
        system_prompt = prompt_row["prompt"] if prompt_row and prompt_row["prompt"] else "Eres un farmacéutico clínico experto. Analiza el caso y genera un POF."

    # Construir contexto
    contexto = f"""Paciente: {paciente['nombre']}, {paciente['sexo']}, Peso: {paciente['peso']}kg, Talla: {paciente['talla']}cm, Edad: {edad} años
Diagnóstico: {paciente['diagnostico']}
Ubicación: {paciente['ubicacion']}

Tratamientos:
{chr(10).join([f"- {t['pauta']}" for t in tratamientos])}

Analíticas:
{chr(10).join([f"- {a['parametro']}: {a['valor']} {a['unidad']} ({a['estado']})" for a in analiticas])}
"""

    # Llamar a OpenAI
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": contexto}
                ],
                "max_tokens": 4000
            }
        )

    if resp.status_code != 200:
        raise HTTPException(502, f"OpenAI error: {resp.status_code}")

    data = resp.json()
    plan = data["choices"][0]["message"]["content"]

    # Guardar en evolución
    async with async_session() as session:
        await session.execute(
            text("INSERT INTO hgu_evolucion (id_episodio, fecha, plan, modelo_ia) VALUES (:id, CURRENT_DATE, :plan, 'llama-3.3-70b-groq')"),
            {"id": id_episodio, "plan": plan, "modelo": "llama-3.3-70b-versatile"}
        )
        await session.commit()

    return {"status": "OK", "plan": plan}

# ═══════════════════════════════════════
# Integración APEX SIGFAR
# ═══════════════════════════════════════
@app.get("/api/apex/sigfar/pacientes", tags=["APEX SIGFAR"])
async def apex_sigfar_pacientes():
    """Lee pacientes activos desde APEX Plataforma SIGFAR via ORDS"""
    if not APEX_SIGFAR_URL:
        raise HTTPException(400, "APEX_SIGFAR_URL no configurada en .env")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{APEX_SIGFAR_URL}/pacientes/")
        if resp.status_code != 200:
            raise HTTPException(502, f"APEX SIGFAR error: {resp.status_code}")
        return resp.json()

@app.get("/api/apex/sigfar/stats", tags=["APEX SIGFAR"])
async def apex_sigfar_stats():
    """Lee estadísticas desde APEX Plataforma SIGFAR via ORDS"""
    if not APEX_SIGFAR_URL:
        raise HTTPException(400, "APEX_SIGFAR_URL no configurada en .env")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{APEX_SIGFAR_URL}/stats/")
        if resp.status_code != 200:
            raise HTTPException(502, f"APEX SIGFAR error: {resp.status_code}")
        return resp.json()

@app.get("/api/apex/sigfar/evoluciones/{id_episodio}", tags=["APEX SIGFAR"])
async def apex_sigfar_evoluciones(id_episodio: int):
    """Lee evoluciones de un paciente desde APEX SIGFAR"""
    if not APEX_SIGFAR_URL:
        raise HTTPException(400, "APEX_SIGFAR_URL no configurada en .env")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{APEX_SIGFAR_URL}/evoluciones/{id_episodio}")
        if resp.status_code != 200:
            raise HTTPException(502, f"APEX SIGFAR error: {resp.status_code}")
        return resp.json()

# ═══════════════════════════════════════
# Integración APEX GestionAX
# ═══════════════════════════════════════
@app.get("/api/apex/gestionax/consumos", tags=["APEX GestionAX"])
async def apex_gestionax_consumos():
    """Lee consumos desde APEX GestionAX via ORDS"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada en .env")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{APEX_GESTIONAX_URL}/consumos/")
        if resp.status_code != 200:
            raise HTTPException(502, f"APEX GestionAX error: {resp.status_code}")
        return resp.json()

@app.get("/api/apex/gestionax/catalogo", tags=["APEX GestionAX"])
async def apex_gestionax_catalogo():
    """Lee catálogo hospital desde APEX GestionAX via ORDS"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada en .env")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{APEX_GESTIONAX_URL}/catalogo/")
        if resp.status_code != 200:
            raise HTTPException(502, f"APEX GestionAX error: {resp.status_code}")
        return resp.json()

# ═══════════════════════════════════════
# Vista unificada (Hub)
# ═══════════════════════════════════════
@app.get("/api/hub/dashboard", tags=["Hub Unificado"])
async def hub_dashboard():
    """Dashboard unificado: datos locales + APEX SIGFAR + APEX GestionAX"""
    result = {"local": {}, "sigfar": None, "gestionax": None}

    # Datos locales (PostgreSQL)
    async with async_session() as session:
        pac = await session.execute(text("SELECT COUNT(*) FROM hgu_pacientes WHERE estado_p = 'ACTIVO'"))
        emprm = await session.execute(text("SELECT COUNT(*) FROM hgu_emprm_lineas WHERE decision = 'P'"))
        result["local"] = {
            "pacientes_hub": pac.scalar(),
            "emprm_pendientes_hub": emprm.scalar()
        }

    # APEX SIGFAR (si configurado)
    if APEX_SIGFAR_URL:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{APEX_SIGFAR_URL}/stats/")
                if resp.status_code == 200:
                    result["sigfar"] = resp.json()
        except Exception:
            result["sigfar"] = {"error": "No disponible"}

    # APEX GestionAX (si configurado)
    if APEX_GESTIONAX_URL:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{APEX_GESTIONAX_URL}/stats/")
                if resp.status_code == 200:
                    result["gestionax"] = resp.json()
        except Exception:
            result["gestionax"] = {"error": "No disponible"}

    return result


# ═══════════════════════════════════════
# Cuadro de Mandos Jefatura
# ═══════════════════════════════════════

@app.get("/api/jefatura/resumen", tags=["Jefatura"])
async def jefatura_resumen():
    """KPIs ejecutivos: cruza SIGFAR + GestionAX"""
    result = {}
    # SIGFAR
    if APEX_SIGFAR_URL:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(f"{APEX_SIGFAR_URL}/stats/")
                if r.status_code == 200:
                    result["sigfar"] = r.json()
        except:
            result["sigfar"] = None
    # GestionAX
    if APEX_GESTIONAX_URL:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(f"{APEX_GESTIONAX_URL}/stats/")
                if r.status_code == 200:
                    result["gestionax"] = r.json()
        except:
            result["gestionax"] = None
    return result

@app.get("/api/jefatura/gasto-servicio", tags=["Jefatura"])
async def jefatura_gasto_servicio():
    """Gasto farmacéutico por servicio clínico"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/gasto-servicio/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/top-medicamentos", tags=["Jefatura"])
async def jefatura_top_medicamentos():
    """Top 50 medicamentos por gasto"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/top-medicamentos/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/evolucion-mensual", tags=["Jefatura"])
async def jefatura_evolucion_mensual():
    """Evolución mensual del gasto farmacéutico"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/evolucion-mensual/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/adherencia-gft", tags=["Jefatura"])
async def jefatura_adherencia_gft():
    """Adherencia a la GFT por servicio"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/adherencia-gft/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/proa-antibioticos", tags=["Jefatura"])
async def jefatura_proa():
    """Consumo de antibióticos por servicio (PROA)"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/proa-antibioticos/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/dispensaciones", tags=["Jefatura"])
async def jefatura_dispensaciones():
    """Stats de dispensaciones ambulatorias"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/dispensaciones-stats/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.get("/api/jefatura/dispensaciones-patologia", tags=["Jefatura"])
async def jefatura_dispensaciones_patologia():
    """Top patologías por coste en dispensaciones ambulatorias"""
    if not APEX_GESTIONAX_URL:
        raise HTTPException(400, "APEX_GESTIONAX_URL no configurada")
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{APEX_GESTIONAX_URL}/dispensaciones-patologia/")
        if r.status_code != 200:
            raise HTTPException(502, f"GestionAX error: {r.status_code}")
        return r.json()

@app.post("/api/jefatura/sigfarita", tags=["Jefatura"])
async def sigfarita_chat(pregunta: dict):
    """Sigfarita: asistente IA para la Dra. Blasco. Recibe pregunta en lenguaje natural, consulta datos y responde."""
    texto = pregunta.get("texto", "")
    if not texto:
        raise HTTPException(400, "Falta campo 'texto' con la pregunta")

    # Obtener contexto de datos
    contexto_datos = ""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Stats SIGFAR
            r1 = await client.get(f"{APEX_SIGFAR_URL}/stats/")
            if r1.status_code == 200:
                contexto_datos += f"Datos SIGFAR: {r1.text}\n"
            # Stats GestionAX
            r2 = await client.get(f"{APEX_GESTIONAX_URL}/stats/")
            if r2.status_code == 200:
                contexto_datos += f"Datos GestionAX: {r2.text}\n"
            # Gasto por servicio
            r3 = await client.get(f"{APEX_GESTIONAX_URL}/gasto-servicio/")
            if r3.status_code == 200:
                contexto_datos += f"Gasto por servicio: {r3.text}\n"
    except:
        pass

    # Llamar a Groq con contexto
    system_prompt = """Eres Sigfarita, la asistente IA de la Dra. Pilar Blasco Segura, Jefa del Servicio de Farmacia del Consorcio Hospital General Universitario de Valencia (CHGUV).

Tu función es ayudarla en la gestión del servicio respondiendo preguntas sobre:
- Gasto farmacéutico por servicio clínico
- Top medicamentos por coste
- Indicadores de productividad farmacéutica (validaciones, EM/PRM)
- Adherencia a la Guía Farmacoterapéutica (GFT)
- Dispensaciones ambulatorias
- Indicadores PROA (antibióticos)
- Cualquier cruce de datos clínicos y económicos

Responde siempre en español, de forma clara y concisa. Si tienes datos numéricos disponibles, úsalos. Si no tienes datos suficientes, indícalo. Incluye siempre cifras concretas cuando las tengas. Tutea a la Dra. Blasco. Sé profesional pero cercana."""

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Datos disponibles del hospital:\n{contexto_datos}\n\nPregunta de la Dra. Blasco: {texto}"}
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
        if r.status_code != 200:
            raise HTTPException(502, f"Groq error: {r.status_code} - {r.text}")
        data = r.json()
        respuesta = data["choices"][0]["message"]["content"]

    return {"pregunta": texto, "respuesta": respuesta, "modelo": "llama-3.3-70b-groq"}
