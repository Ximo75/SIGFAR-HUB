"""
SIGFAR API — FastAPI Backend
Plataforma de Gestión Farmacéutica Asistida por IA
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
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


# ═══════════════════════════════════════════════════════════════════
# RADAR IA — Monitorización de novedades IA en farmacia hospitalaria
# ═══════════════════════════════════════════════════════════════════

import asyncio
import json
import hashlib
import re as _re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from pydantic import BaseModel


# --- Modelos Pydantic Radar ---

class RadarScanRequest(BaseModel):
    fuentes: list[str] | None = None

class RadarToggleFav(BaseModel):
    item_id: int

class RadarSetNota(BaseModel):
    item_id: int
    nota: str

class RadarSetPrioridad(BaseModel):
    item_id: int
    prioridad: str


# --- Modelos Pydantic APIs ---

class ApiToggleFav(BaseModel):
    api_id: int

class ApiSetNota(BaseModel):
    api_id: int
    nota: str

class ApiSetPrioridad(BaseModel):
    api_id: int
    prioridad: str


# --- Prompt para clasificación IA ---

RADAR_SYSTEM_PROMPT = """Eres un analista de inteligencia competitiva especializado en farmacia hospitalaria e inteligencia artificial. Analiza el siguiente artículo/noticia y devuelve SOLO un JSON válido (sin markdown, sin backticks, sin texto adicional) con esta estructura exacta:
{"resumen_es": "Resumen de 2-3 frases en español", "categoria": "VALIDACION|FARMACOCINETICA|NUTRICION|PROA|ELABORACION|STOCK_LOGISTICA|ROBOTICA|FARMACOECONOMIA|CUADRO_MANDOS|REGULACION", "subcategoria": "texto libre", "relevancia": 0, "pais": "código ISO 2 letras o null", "institucion": "nombre o null", "estado_sigfar_hub": "IMPLEMENTADO|PARCIAL|PLANIFICADO|NUEVO", "modulo_sigfar": "P15|P36|P37|P40|P42|P43|HUB|null", "como_implementar": "Cómo implementar o mejorar esto en SIGFAR Hub (1-2 frases)", "tags": ["tag1","tag2","tag3"]}

Criterios de relevancia (0-100): 90-100 directamente aplicable a farmacia hospitalaria+IA; 70-89 muy relevante con adaptación menor; 50-69 idea transferible; 30-49 tangencial; 0-29 poco relevante.

Contexto SIGFAR Hub: plataforma multiagente IA para farmacia hospitalaria. Módulos operativos: nutrición artificial (P36, 7 agentes), farmacocinética/TDM MAP Bayesiano (P42), PROA antimicrobianos (P43, 6 agentes), detección EM/PRM (P15), NPD domiciliaria (P37), scoring complejidad (P40). Pendientes: cuadro mandos directivo, farmacoeconomía, multi-IA consenso, vigilancia proactiva 24/7, simulador FIR. Integración prevista con: robots de elaboración (ExactaMix, ChemoMaker), prescripción NP (Versia), dispensadores (PYXIS), HCE (Hosix/Florence), laboratorio, microbiología."""

RADAR_VALID_CATS = {'VALIDACION', 'FARMACOCINETICA', 'NUTRICION', 'PROA', 'ELABORACION',
                    'STOCK_LOGISTICA', 'ROBOTICA', 'FARMACOECONOMIA', 'CUADRO_MANDOS', 'REGULACION'}


# --- Utilidades ---

def _xml_text(el):
    """Extrae todo el texto de un elemento XML incluyendo sub-elementos"""
    return "".join(el.itertext()) if el is not None else ""

def _safe_date(s):
    """Convierte string YYYY-MM-DD a date o None"""
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


# --- Escáneres por fuente ---

async def _radar_scan_pubmed(client, query, categoria):
    """Escanea PubMed: esearch (PMIDs) → efetch (títulos + abstracts)"""
    items = []
    try:
        r = await client.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&retmode=json&retmax=15&sort=date&term={quote_plus(query)}",
            timeout=20)
        if r.status_code != 200:
            return items
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return items
        await asyncio.sleep(0.5)
        r2 = await client.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={','.join(pmids)}&retmode=xml",
            timeout=30)
        if r2.status_code != 200:
            return items
        xml_str = _re.sub(r'<!DOCTYPE[^>]*>', '', r2.text)
        root = ET.fromstring(xml_str)
        for art in root.findall(".//PubmedArticle"):
            try:
                pmid = art.findtext(".//PMID", "")
                titulo = _xml_text(art.find(".//ArticleTitle"))
                abstracts = art.findall(".//AbstractText")
                resumen = " ".join(_xml_text(a) for a in abstracts) if abstracts else ""
                fecha_pub = None
                pd_el = art.find(".//PubDate")
                if pd_el is not None:
                    y = pd_el.findtext("Year", "")
                    m = pd_el.findtext("Month", "01")
                    d = pd_el.findtext("Day", "01")
                    mmap = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                    mn = mmap.get(m, m.zfill(2) if m.isdigit() else "01")
                    dn = d.zfill(2) if d.isdigit() else "01"
                    if y:
                        fecha_pub = f"{y}-{mn}-{dn}"
                if titulo and pmid:
                    items.append({
                        "titulo": titulo[:500],
                        "resumen": resumen[:4000] or None,
                        "categoria": categoria,
                        "fuente": "PUBMED",
                        "fuente_id": pmid,
                        "url_original": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "fecha_publicacion": fecha_pub,
                        "json_raw": {"pmid": pmid, "query": query}
                    })
            except Exception:
                continue
    except Exception:
        pass
    return items


async def _radar_scan_google_news(client, query, categoria):
    """Escanea Google News RSS"""
    items = []
    try:
        r = await client.get(
            f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=es&gl=ES&ceid=ES:es",
            timeout=20)
        if r.status_code != 200:
            return items
        root = ET.fromstring(r.text)
        for el in root.findall(".//item")[:10]:
            try:
                titulo = el.findtext("title", "")
                link = el.findtext("link", "")
                desc = el.findtext("description", "")
                guid = el.findtext("guid", "")
                pub_str = el.findtext("pubDate", "")
                src_el = el.find("source")
                src_name = src_el.text if src_el is not None else ""
                fid = guid[:100] if guid else hashlib.md5(link.encode()).hexdigest()[:20]
                fecha_pub = None
                if pub_str:
                    try:
                        fecha_pub = parsedate_to_datetime(pub_str).strftime("%Y-%m-%d")
                    except Exception:
                        pass
                if desc:
                    desc = _re.sub(r'<[^>]+>', '', desc)
                if titulo and link:
                    items.append({
                        "titulo": titulo[:500],
                        "resumen": desc[:4000] if desc else None,
                        "categoria": categoria,
                        "fuente": "GOOGLE_NEWS",
                        "fuente_id": fid,
                        "url_original": link[:1000],
                        "fecha_publicacion": fecha_pub,
                        "json_raw": {"source": src_name, "query": query}
                    })
            except Exception:
                continue
    except Exception:
        pass
    return items


async def _radar_scan_clinicaltrials(client, query, categoria):
    """Escanea ClinicalTrials.gov API v2"""
    items = []
    try:
        r = await client.get(
            f"https://clinicaltrials.gov/api/v2/studies"
            f"?query.term={quote_plus(query)}&pageSize=10&sort=LastUpdatePostDate:desc",
            timeout=20)
        if r.status_code != 200:
            return items
        for study in r.json().get("studies", []):
            try:
                proto = study.get("protocolSection", {})
                ident = proto.get("identificationModule", {})
                desc = proto.get("descriptionModule", {})
                status_mod = proto.get("statusModule", {})
                nct = ident.get("nctId", "")
                titulo = ident.get("briefTitle", "")
                resumen = desc.get("briefSummary", "")
                last_upd = status_mod.get("lastUpdateSubmitDate", "")
                if titulo and nct:
                    items.append({
                        "titulo": titulo[:500],
                        "resumen": resumen[:4000] if resumen else None,
                        "categoria": categoria,
                        "fuente": "CLINICALTRIALS",
                        "fuente_id": nct,
                        "url_original": f"https://clinicaltrials.gov/study/{nct}",
                        "fecha_publicacion": last_upd[:10] if last_upd else None,
                        "json_raw": {"nctId": nct, "query": query}
                    })
            except Exception:
                continue
    except Exception:
        pass
    return items


async def _radar_scan_semantic(client, query, categoria):
    """Escanea Semantic Scholar Graph API"""
    items = []
    try:
        r = await client.get(
            f"https://api.semanticscholar.org/graph/v1/paper/search"
            f"?query={quote_plus(query)}&limit=10&fields=title,abstract,url,year,venue,externalIds",
            timeout=20)
        if r.status_code != 200:
            return items
        for paper in r.json().get("data", []):
            try:
                pid = paper.get("paperId", "")
                titulo = paper.get("title", "")
                abstract = paper.get("abstract", "")
                purl = paper.get("url") or f"https://www.semanticscholar.org/paper/{pid}"
                year = paper.get("year")
                ext = paper.get("externalIds") or {}
                if titulo and pid:
                    items.append({
                        "titulo": titulo[:500],
                        "resumen": abstract[:4000] if abstract else None,
                        "categoria": categoria,
                        "fuente": "SEMANTIC",
                        "fuente_id": pid[:100],
                        "url_original": purl[:1000],
                        "fecha_publicacion": f"{year}-01-01" if year else None,
                        "json_raw": {"paperId": pid, "doi": ext.get("DOI", ""),
                                     "venue": paper.get("venue", ""), "query": query}
                    })
            except Exception:
                continue
    except Exception:
        pass
    return items


_RADAR_SCANNERS = {
    "PUBMED": _radar_scan_pubmed,
    "GOOGLE_NEWS": _radar_scan_google_news,
    "CLINICALTRIALS": _radar_scan_clinicaltrials,
    "SEMANTIC": _radar_scan_semantic,
}
_RADAR_DELAYS = {"PUBMED": 0.5, "SEMANTIC": 1.0, "GOOGLE_NEWS": 0.3, "CLINICALTRIALS": 0.3}


# --- Enriquecimiento con Groq/Llama ---

async def _radar_enrich_one(client, item_id, titulo, resumen):
    """Enriquece un ítem llamando a Groq/Llama. Retorna True si OK."""
    try:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": RADAR_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Título: {titulo}\nResumen: {resumen or 'No disponible'}"}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=30)
        if resp.status_code != 200:
            return False
        content = resp.json()["choices"][0]["message"]["content"].strip()
        # Limpiar posibles backticks de Llama
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        ia = json.loads(content)

        # Validar campos
        cat = ia.get("categoria")
        if cat not in RADAR_VALID_CATS:
            cat = None
        estado = ia.get("estado_sigfar_hub", "NUEVO")
        if estado not in ('IMPLEMENTADO', 'PARCIAL', 'PLANIFICADO', 'NUEVO'):
            estado = "NUEVO"
        modulo = ia.get("modulo_sigfar")
        if modulo not in ('P15', 'P36', 'P37', 'P40', 'P42', 'P43', 'HUB', None):
            modulo = None
        rel = ia.get("relevancia", 50)
        rel = max(0, min(100, int(rel))) if isinstance(rel, (int, float)) else 50
        tags_list = ia.get("tags", [])
        tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else None

        # Construir UPDATE dinámico
        sets = [
            "resumen_ia = :resumen_ia", "como_en_sigfar_hub = :como",
            "estado_sigfar_hub = :estado", "relevancia = :rel",
            "subcategoria = :subcat", "pais = :pais", "institucion = :inst",
            "tags = :tags", "json_ia = CAST(:json_ia AS jsonb)"
        ]
        params = {
            "id": item_id,
            "resumen_ia": (ia.get("resumen_es") or "")[:4000],
            "como": (ia.get("como_implementar") or "")[:2000],
            "estado": estado, "rel": rel,
            "subcat": (ia.get("subcategoria") or "")[:100],
            "pais": (ia.get("pais") or "")[:5] or None,
            "inst": (ia.get("institucion") or "")[:200] or None,
            "tags": (tags_str or "")[:500] or None,
            "json_ia": json.dumps(ia, ensure_ascii=False)
        }
        if cat:
            sets.append("categoria = :cat")
            params["cat"] = cat
        if modulo is not None:
            sets.append("modulo_sigfar = :modulo")
            params["modulo"] = modulo

        async with async_session() as session:
            await session.execute(
                text(f"UPDATE hgu_radar_items SET {', '.join(sets)} WHERE id = :id"), params)
            await session.commit()
        return True
    except Exception:
        return False


# ─── Endpoints Radar IA ─────────────────────────────────────────

@app.get("/api/radar/items", tags=["Radar IA"])
async def radar_items(
        categoria: str | None = None, estado: str | None = None,
        fuente: str | None = None, favorito: bool | None = None,
        buscar: str | None = None, periodo: int | None = None,
        skip: int = 0, limit: int = 50):
    """Lista ítems del radar con filtros opcionales"""
    conds = ["archivado = FALSE"]
    params = {"lim": min(limit, 200), "off": skip}
    if categoria:
        conds.append("categoria = :cat")
        params["cat"] = categoria
    if estado:
        conds.append("estado_sigfar_hub = :est")
        params["est"] = estado
    if fuente:
        conds.append("fuente = :fuente")
        params["fuente"] = fuente
    if favorito:
        conds.append("favorito = TRUE")
    if buscar:
        conds.append("(LOWER(titulo) LIKE :q OR LOWER(COALESCE(resumen_ia,'')) LIKE :q OR LOWER(COALESCE(resumen,'')) LIKE :q)")
        params["q"] = f"%{buscar.lower()}%"
    if periodo and periodo > 0:
        conds.append("fecha_scan >= NOW() - :dias * INTERVAL '1 day'")
        params["dias"] = periodo
    where = " AND ".join(conds)
    sql = f"""SELECT * FROM hgu_radar_items WHERE {where}
              ORDER BY relevancia DESC, fecha_publicacion DESC NULLS LAST
              LIMIT :lim OFFSET :off"""
    async with async_session() as session:
        result = await session.execute(text(sql), params)
        return [dict(r) for r in result.mappings().all()]


@app.get("/api/radar/items/{item_id}", tags=["Radar IA"])
async def radar_item_detail(item_id: int):
    """Detalle de un ítem — lo marca como leído automáticamente"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_radar_items WHERE id = :id"), {"id": item_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "Ítem no encontrado")
        if not row["leido"]:
            await session.execute(
                text("UPDATE hgu_radar_items SET leido = TRUE, fecha_leido = NOW() WHERE id = :id"),
                {"id": item_id})
            await session.commit()
        return dict(row)


@app.post("/api/radar/scan", tags=["Radar IA"])
async def radar_scan(req: RadarScanRequest | None = None):
    """Ejecutar escaneo completo: fuentes → insertar → enriquecer con IA"""
    if req is None:
        req = RadarScanRequest()
    start = datetime.now()
    all_raw = []
    fuentes_ok = 0
    fuentes_error = 0
    errors = []

    # 1. Leer queries activas
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_radar_queries WHERE activo = TRUE"))
        queries = [dict(r) for r in result.mappings().all()]
    if req.fuentes:
        queries = [q for q in queries if q["fuente"] in req.fuentes]

    # 2. Escanear cada query
    async with httpx.AsyncClient() as client:
        for qr in queries:
            scanner = _RADAR_SCANNERS.get(qr["fuente"])
            if not scanner:
                continue
            try:
                found = await scanner(client, qr["query_text"], qr["categoria"])
                all_raw.extend(found)
                fuentes_ok += 1
            except Exception as e:
                fuentes_error += 1
                errors.append(f"{qr['fuente']}/{qr['query_text'][:30]}: {str(e)[:100]}")
            await asyncio.sleep(_RADAR_DELAYS.get(qr["fuente"], 0.3))

    # 3. Insertar deduplicando por (fuente, fuente_id)
    items_nuevos = 0
    items_dupes = 0
    new_ids = []
    async with async_session() as session:
        for it in all_raw:
            if not it.get("fuente_id"):
                continue
            try:
                fp = _safe_date(it.get("fecha_publicacion"))
                jr = json.dumps(it.get("json_raw", {}), ensure_ascii=False)
                result = await session.execute(text("""
                    INSERT INTO hgu_radar_items
                        (titulo, resumen, categoria, fuente, fuente_id, url_original, fecha_publicacion, json_raw)
                    VALUES (:titulo, :resumen, :cat, :fuente, :fid, :url, :fp, CAST(:jr AS jsonb))
                    ON CONFLICT (fuente, fuente_id) DO NOTHING
                    RETURNING id
                """), {
                    "titulo": it["titulo"], "resumen": it.get("resumen"),
                    "cat": it["categoria"], "fuente": it["fuente"],
                    "fid": it["fuente_id"], "url": it["url_original"],
                    "fp": fp, "jr": jr
                })
                row = result.first()
                if row:
                    items_nuevos += 1
                    new_ids.append(row[0])
                else:
                    items_dupes += 1
            except Exception:
                items_dupes += 1
        await session.commit()

    # 4. Enriquecer nuevos con Groq/Llama (máx 20 por rate limit)
    enriched = 0
    if new_ids:
        async with httpx.AsyncClient() as client:
            for nid in new_ids[:20]:
                async with async_session() as session:
                    r = await session.execute(
                        text("SELECT titulo, resumen FROM hgu_radar_items WHERE id = :id"),
                        {"id": nid})
                    row = r.mappings().first()
                if row:
                    ok = await _radar_enrich_one(client, nid, row["titulo"], row["resumen"])
                    if ok:
                        enriched += 1
                    await asyncio.sleep(2)  # Rate limit Groq free: 30 req/min

    # 5. Registrar en log
    dur = (datetime.now() - start).total_seconds()
    async with async_session() as session:
        await session.execute(text("""
            INSERT INTO hgu_radar_log
                (tipo, fuentes_ok, fuentes_error, items_nuevos, items_duplicados, duracion_seg, detalles)
            VALUES ('MANUAL', :ok, :err, :nue, :dup, :dur, CAST(:det AS jsonb))
        """), {
            "ok": fuentes_ok, "err": fuentes_error,
            "nue": items_nuevos, "dup": items_dupes,
            "dur": round(dur, 1),
            "det": json.dumps({"errors": errors, "enriched": enriched}, ensure_ascii=False)
        })
        await session.commit()

    return {
        "status": "OK", "items_nuevos": items_nuevos,
        "items_duplicados": items_dupes, "items_enriquecidos": enriched,
        "fuentes_ok": fuentes_ok, "fuentes_error": fuentes_error,
        "duracion_seg": round(dur, 1), "errors": errors
    }


@app.post("/api/radar/enrich/{item_id}", tags=["Radar IA"])
async def radar_enrich(item_id: int):
    """Enriquecer un ítem concreto con Groq/Llama"""
    async with async_session() as session:
        r = await session.execute(
            text("SELECT id, titulo, resumen FROM hgu_radar_items WHERE id = :id"),
            {"id": item_id})
        row = r.mappings().first()
        if not row:
            raise HTTPException(404, "Ítem no encontrado")
    async with httpx.AsyncClient() as client:
        ok = await _radar_enrich_one(client, item_id, row["titulo"], row["resumen"])
    if not ok:
        raise HTTPException(502, "Error al enriquecer con Groq/Llama")
    async with async_session() as session:
        r = await session.execute(
            text("SELECT * FROM hgu_radar_items WHERE id = :id"), {"id": item_id})
        return dict(r.mappings().first())


@app.post("/api/radar/toggle-favorito", tags=["Radar IA"])
async def radar_toggle_fav(body: RadarToggleFav):
    """Toggle favorito de un ítem"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_radar_items SET favorito = NOT favorito WHERE id = :id"),
            {"id": body.item_id})
        await session.commit()
        r = await session.execute(
            text("SELECT favorito FROM hgu_radar_items WHERE id = :id"),
            {"id": body.item_id})
        row = r.mappings().first()
        return {"id": body.item_id, "favorito": row["favorito"] if row else False}


@app.post("/api/radar/set-nota", tags=["Radar IA"])
async def radar_set_nota(body: RadarSetNota):
    """Guardar nota del usuario en un ítem"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_radar_items SET nota_usuario = :nota WHERE id = :id"),
            {"id": body.item_id, "nota": body.nota})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/radar/set-prioridad", tags=["Radar IA"])
async def radar_set_prioridad(body: RadarSetPrioridad):
    """Guardar prioridad del usuario"""
    if body.prioridad not in ('ALTA', 'MEDIA', 'BAJA'):
        raise HTTPException(400, "Prioridad debe ser ALTA, MEDIA o BAJA")
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_radar_items SET prioridad_usuario = :p WHERE id = :id"),
            {"id": body.item_id, "p": body.prioridad})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/radar/archivar/{item_id}", tags=["Radar IA"])
async def radar_archivar(item_id: int):
    """Archivar un ítem (no se muestra en listados)"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_radar_items SET archivado = TRUE WHERE id = :id"),
            {"id": item_id})
        await session.commit()
    return {"status": "OK"}


@app.get("/api/radar/stats", tags=["Radar IA"])
async def radar_stats():
    """Estadísticas del radar: totales, por categoría, último scan"""
    async with async_session() as session:
        total = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_radar_items WHERE archivado = FALSE"))).scalar()
        nuevos = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_radar_items WHERE archivado = FALSE AND fecha_scan >= NOW() - INTERVAL '7 days'"))).scalar()
        favs = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_radar_items WHERE favorito = TRUE AND archivado = FALSE"))).scalar()
        no_leidos = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_radar_items WHERE leido = FALSE AND archivado = FALSE"))).scalar()
        cats = await session.execute(
            text("SELECT categoria, COUNT(*) n FROM hgu_radar_items WHERE archivado = FALSE GROUP BY categoria ORDER BY n DESC"))
        por_cat = {r["categoria"]: r["n"] for r in cats.mappings().all()}
        ult = (await session.execute(
            text("SELECT MAX(fecha_ejecucion) FROM hgu_radar_log"))).scalar()
        return {
            "total": total, "nuevos_semana": nuevos,
            "favoritos": favs, "no_leidos": no_leidos,
            "por_categoria": por_cat,
            "ultimo_scan": ult.isoformat() if ult else None
        }


@app.get("/api/radar/favoritos", tags=["Radar IA"])
async def radar_favoritos():
    """Lista de favoritos (backlog de ideas) ordenada por prioridad + relevancia"""
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT * FROM hgu_radar_items
            WHERE favorito = TRUE AND archivado = FALSE
            ORDER BY CASE prioridad_usuario
                WHEN 'ALTA' THEN 1 WHEN 'MEDIA' THEN 2 WHEN 'BAJA' THEN 3 ELSE 4 END,
                relevancia DESC
        """))
        return [dict(r) for r in result.mappings().all()]


# ═══════════════════════════════════════════════════════════════
# ─── Catálogo APIs ────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

APIS_SYSTEM_PROMPT = """Eres un arquitecto de integración de sistemas de farmacia hospitalaria.
Dada la siguiente API y su descripción, genera una propuesta de integración en SIGFAR Hub.
Responde SOLO un JSON válido (sin markdown, sin backticks) con esta estructura:
{"propuesta": "Párrafo de 3-5 frases explicando cómo integrar esta API en SIGFAR Hub, qué módulos beneficiaría y qué pasos seguir.", "prioridad_sugerida": "P1|P2|P3", "tiempo_estimado": "texto corto ej: 2-3 días", "modulos_beneficiados": ["módulo1","módulo2"], "ejemplo_uso": "Ejemplo concreto de un caso de uso clínico."}
"""


async def _api_test_connectivity(client: httpx.AsyncClient, api_row: dict) -> dict:
    """Prueba conectividad real contra url_test de una API. Devuelve dict con resultado."""
    url = api_row.get("url_test") or api_row.get("url_base")
    if not url:
        return {"ok": False, "latencia_ms": 0, "error": "Sin URL de test"}
    headers = {}
    if api_row.get("auth_type") in ("BEARER", "API_KEY") and api_row.get("env_var_key"):
        key = os.getenv(api_row["env_var_key"], "")
        if key and key != "sk-placeholder":
            if api_row["auth_type"] == "BEARER":
                headers["Authorization"] = f"Bearer {key}"
            else:
                headers["Authorization"] = f"Api-Key {key}"
    try:
        import time
        t0 = time.monotonic()
        r = await client.get(url, headers=headers, timeout=15, follow_redirects=True)
        latencia = int((time.monotonic() - t0) * 1000)
        ok = r.status_code < 400
        return {"ok": ok, "latencia_ms": latencia, "status_code": r.status_code,
                "error": None if ok else f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "latencia_ms": 0, "error": str(e)[:200]}


@app.get("/api/apis/catalogo", tags=["APIs"])
async def apis_catalogo(bloque: str | None = None, estado: str | None = None,
                        prioridad: str | None = None, buscar: str | None = None,
                        favorito: bool | None = None):
    """Lista el catálogo de APIs con filtros opcionales"""
    conds = []
    params = {}
    if bloque:
        conds.append("bloque = :bloque")
        params["bloque"] = bloque
    if estado:
        conds.append("estado = :estado")
        params["estado"] = estado
    if prioridad:
        conds.append("prioridad = :prioridad")
        params["prioridad"] = prioridad
    if favorito:
        conds.append("favorito = TRUE")
    if buscar:
        conds.append("(LOWER(nombre) LIKE :q OR LOWER(COALESCE(descripcion,'')) LIKE :q OR LOWER(COALESCE(caso_uso,'')) LIKE :q)")
        params["q"] = f"%{buscar.lower()}%"
    where = "WHERE " + " AND ".join(conds) if conds else ""
    sql = f"""SELECT * FROM hgu_hub_apis {where}
              ORDER BY CASE prioridad WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END,
                       nombre"""
    async with async_session() as session:
        result = await session.execute(text(sql), params)
        return [dict(r) for r in result.mappings().all()]


@app.get("/api/apis/stats", tags=["APIs"])
async def apis_stats():
    """Estadísticas del catálogo de APIs"""
    async with async_session() as session:
        total = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis"))).scalar()
        conectadas = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE estado = 'CONECTADA'"))).scalar()
        pendientes = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE estado = 'PENDIENTE'"))).scalar()
        en_apex = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE estado = 'EN_APEX'"))).scalar()
        futuro = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE estado = 'FUTURO'"))).scalar()
        favs = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE favorito = TRUE"))).scalar()
        por_bloque = await session.execute(
            text("SELECT bloque, COUNT(*) n FROM hgu_hub_apis GROUP BY bloque ORDER BY n DESC"))
        bloques = {r["bloque"]: r["n"] for r in por_bloque.mappings().all()}
        por_prio = await session.execute(
            text("SELECT prioridad, COUNT(*) n FROM hgu_hub_apis WHERE prioridad IS NOT NULL GROUP BY prioridad ORDER BY prioridad"))
        prioridades = {r["prioridad"]: r["n"] for r in por_prio.mappings().all()}
        test_ok = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE ultimo_test_ok = TRUE"))).scalar()
        test_fail = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_hub_apis WHERE ultimo_test_ok = FALSE"))).scalar()
        return {
            "total": total, "conectadas": conectadas, "pendientes": pendientes,
            "en_apex": en_apex, "futuro": futuro, "favoritos": favs,
            "por_bloque": bloques, "por_prioridad": prioridades,
            "test_ok": test_ok, "test_fail": test_fail
        }


@app.get("/api/apis/favoritos", tags=["APIs"])
async def apis_favoritos():
    """Lista de APIs favoritas ordenadas por prioridad_usuario → prioridad (backlog personal)"""
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT * FROM hgu_hub_apis
            WHERE favorito = TRUE
            ORDER BY CASE prioridad_usuario
                WHEN 'ALTA' THEN 1 WHEN 'MEDIA' THEN 2 WHEN 'BAJA' THEN 3 ELSE 4 END,
                CASE prioridad
                WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END,
                nombre
        """))
        return [dict(r) for r in result.mappings().all()]


@app.get("/api/apis/{api_id}", tags=["APIs"])
async def apis_detail(api_id: int):
    """Detalle completo de una API"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_hub_apis WHERE id = :id"), {"id": api_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "API no encontrada")
        return dict(row)


@app.post("/api/apis/test/{api_id}", tags=["APIs"])
async def apis_test(api_id: int):
    """Testear conectividad de una API en tiempo real"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_hub_apis WHERE id = :id"), {"id": api_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "API no encontrada")
        api_data = dict(row)

    async with httpx.AsyncClient() as client:
        test_result = await _api_test_connectivity(client, api_data)

    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_hub_apis
            SET ultimo_test = NOW(),
                ultimo_test_ok = :ok,
                ultimo_test_latencia_ms = :lat
            WHERE id = :id
        """), {"ok": test_result["ok"], "lat": test_result["latencia_ms"], "id": api_id})
        await session.commit()

    return {
        "api_id": api_id, "nombre": api_data["nombre"],
        **test_result
    }


@app.post("/api/apis/test-all", tags=["APIs"])
async def apis_test_all():
    """Testear conectividad de TODAS las APIs del catálogo"""
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM hgu_hub_apis ORDER BY id"))
        apis = [dict(r) for r in result.mappings().all()]

    results = []
    async with httpx.AsyncClient() as client:
        for api_data in apis:
            test_result = await _api_test_connectivity(client, api_data)
            async with async_session() as session:
                await session.execute(text("""
                    UPDATE hgu_hub_apis
                    SET ultimo_test = NOW(),
                        ultimo_test_ok = :ok,
                        ultimo_test_latencia_ms = :lat
                    WHERE id = :id
                """), {"ok": test_result["ok"], "lat": test_result["latencia_ms"],
                       "id": api_data["id"]})
                await session.commit()
            results.append({
                "api_id": api_data["id"], "nombre": api_data["nombre"],
                **test_result
            })
            await asyncio.sleep(0.3)

    ok_count = sum(1 for r in results if r["ok"])
    return {
        "total": len(results), "ok": ok_count,
        "fail": len(results) - ok_count,
        "results": results
    }


@app.post("/api/apis/enrich/{api_id}", tags=["APIs"])
async def apis_enrich(api_id: int):
    """Generar propuesta de integración IA para una API"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_hub_apis WHERE id = :id"), {"id": api_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "API no encontrada")
        api_data = dict(row)

    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-placeholder":
        raise HTTPException(503, "Groq API key no configurada")

    user_msg = (
        f"API: {api_data['nombre']}\n"
        f"Descripción: {api_data.get('descripcion', 'N/A')}\n"
        f"URL: {api_data.get('url_base', 'N/A')}\n"
        f"Bloque: {api_data.get('bloque', 'N/A')}\n"
        f"Caso de uso actual: {api_data.get('caso_uso', 'N/A')}\n"
        f"Módulo destino: {api_data.get('modulo_uso', 'N/A')}\n"
        f"Estado actual: {api_data.get('estado', 'N/A')}"
    )

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": APIS_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.3, "max_tokens": 600
                },
                timeout=30
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = _re.sub(r'^```(?:json)?\s*', '', raw)
            raw = _re.sub(r'\s*```$', '', raw)
            data = json.loads(raw)
        except Exception as e:
            raise HTTPException(502, f"Error Groq: {str(e)[:200]}")

    propuesta = data.get("propuesta", raw)
    prioridad = data.get("prioridad_sugerida", api_data.get("prioridad"))
    tiempo = data.get("tiempo_estimado", api_data.get("tiempo_estimado"))

    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_hub_apis
            SET propuesta_ia = :prop,
                prioridad = COALESCE(:prio, prioridad),
                tiempo_estimado = COALESCE(:tiempo, tiempo_estimado)
            WHERE id = :id
        """), {"prop": propuesta, "prio": prioridad, "tiempo": tiempo, "id": api_id})
        await session.commit()
        result = await session.execute(
            text("SELECT * FROM hgu_hub_apis WHERE id = :id"), {"id": api_id})
        return dict(result.mappings().first())


@app.post("/api/apis/toggle-favorito", tags=["APIs"])
async def apis_toggle_fav(body: ApiToggleFav):
    """Toggle favorito de una API"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_hub_apis SET favorito = NOT favorito WHERE id = :id"),
            {"id": body.api_id})
        await session.commit()
        r = await session.execute(
            text("SELECT favorito FROM hgu_hub_apis WHERE id = :id"),
            {"id": body.api_id})
        row = r.mappings().first()
        return {"id": body.api_id, "favorito": row["favorito"] if row else False}


@app.post("/api/apis/set-nota", tags=["APIs"])
async def apis_set_nota(body: ApiSetNota):
    """Guardar nota del usuario en una API"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_hub_apis SET nota_usuario = :nota WHERE id = :id"),
            {"id": body.api_id, "nota": body.nota})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/apis/set-prioridad", tags=["APIs"])
async def apis_set_prioridad(body: ApiSetPrioridad):
    """Guardar prioridad personal del farmacéutico en una API"""
    if body.prioridad not in ('ALTA', 'MEDIA', 'BAJA'):
        raise HTTPException(400, "Prioridad debe ser ALTA, MEDIA o BAJA")
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_hub_apis SET prioridad_usuario = :p WHERE id = :id"),
            {"id": body.api_id, "p": body.prioridad})
        await session.commit()
    return {"status": "OK"}


# ═══════════════════════════════════════════════════════════════════
# ALGORITMOS ML — Catálogo de algoritmos de Machine Learning
# ═══════════════════════════════════════════════════════════════════

# --- Modelos Pydantic ML ---

class MlToggleFav(BaseModel):
    algoritmo_id: int

class MlSetNota(BaseModel):
    algoritmo_id: int
    nota: str

class MlSetPrioridad(BaseModel):
    algoritmo_id: int
    prioridad: str


# --- Prompt para enriquecimiento IA de algoritmos ML ---

ML_SYSTEM_PROMPT = """Eres un experto en Machine Learning aplicado a farmacia hospitalaria.
Dado el siguiente algoritmo ML y su descripción, genera una propuesta detallada de implementación en SIGFAR Hub.
Responde SOLO un JSON válido (sin markdown, sin backticks) con esta estructura:
{"propuesta_ia": "Párrafo de 4-6 frases explicando cómo implementar este algoritmo en SIGFAR Hub: datos necesarios, pipeline de entrenamiento, integración con módulos existentes, métricas de evaluación y beneficio clínico esperado.", "datasets_sugeridos": ["dataset1","dataset2"], "librerias_alternativas": ["lib1","lib2"], "tiempo_implementacion": "texto corto ej: 2-4 semanas", "complejidad_real": "BAJA|MEDIA|ALTA|MUY_ALTA", "quick_win": true}

Contexto SIGFAR Hub: plataforma multiagente IA para farmacia hospitalaria CHGUV. Módulos: nutrición artificial (P36), farmacocinética MAP Bayesiano (P42), PROA antimicrobianos (P43), detección EM/PRM (P15), NPD domiciliaria (P37), scoring complejidad (P40). Datos disponibles: prescripciones electrónicas, analíticas de laboratorio, microbiología, consumos de farmacia, registros de dispensación, alertas AEMPS."""


# --- Endpoints ML ---

@app.get("/api/ml/stats", tags=["Algoritmos ML"])
async def ml_stats():
    """Estadísticas del catálogo de algoritmos ML"""
    async with async_session() as session:
        r = await session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado_sigfar_hub = 'IMPLEMENTADO') as implementados,
                COUNT(*) FILTER (WHERE estado_sigfar_hub = 'EN_DESARROLLO') as en_desarrollo,
                COUNT(*) FILTER (WHERE estado_sigfar_hub = 'NO_IMPLEMENTADO') as no_implementados,
                COUNT(*) FILTER (WHERE favorito = true) as favoritos,
                COUNT(DISTINCT categoria_farmacia) as categorias,
                COUNT(DISTINCT tipo_ml) as tipos_ml
            FROM hgu_ml_algoritmos
        """))
        stats = dict(r.mappings().first())

        r2 = await session.execute(text("""
            SELECT categoria_farmacia, COUNT(*) as n
            FROM hgu_ml_algoritmos GROUP BY categoria_farmacia
            ORDER BY n DESC
        """))
        stats["por_categoria"] = [dict(row) for row in r2.mappings().all()]

        r3 = await session.execute(text("""
            SELECT tipo_ml, COUNT(*) as n
            FROM hgu_ml_algoritmos GROUP BY tipo_ml
            ORDER BY n DESC
        """))
        stats["por_tipo"] = [dict(row) for row in r3.mappings().all()]

        r4 = await session.execute(text("""
            SELECT complejidad, COUNT(*) as n
            FROM hgu_ml_algoritmos GROUP BY complejidad
            ORDER BY n DESC
        """))
        stats["por_complejidad"] = [dict(row) for row in r4.mappings().all()]

        return stats


@app.get("/api/ml/favoritos", tags=["Algoritmos ML"])
async def ml_favoritos():
    """Lista de algoritmos ML marcados como favoritos"""
    async with async_session() as session:
        r = await session.execute(text(
            "SELECT * FROM hgu_ml_algoritmos WHERE favorito = true ORDER BY nombre"
        ))
        return [dict(row) for row in r.mappings().all()]


@app.get("/api/ml/algoritmos", tags=["Algoritmos ML"])
async def ml_catalogo(
    categoria: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    complejidad: str | None = None,
    q: str | None = None
):
    """Catálogo de algoritmos ML con filtros opcionales"""
    where = []
    params = {}
    if categoria:
        where.append("categoria_farmacia = :cat")
        params["cat"] = categoria
    if tipo:
        where.append("tipo_ml = :tipo")
        params["tipo"] = tipo
    if estado:
        where.append("estado_sigfar_hub = :est")
        params["est"] = estado
    if complejidad:
        where.append("complejidad = :comp")
        params["comp"] = complejidad
    if q:
        where.append("(nombre ILIKE :q OR descripcion ILIKE :q OR caso_uso ILIKE :q)")
        params["q"] = f"%{q}%"
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    async with async_session() as session:
        r = await session.execute(
            text(f"SELECT * FROM hgu_ml_algoritmos{clause} ORDER BY categoria_farmacia, nombre"),
            params
        )
        return [dict(row) for row in r.mappings().all()]


@app.get("/api/ml/algoritmos/{alg_id}", tags=["Algoritmos ML"])
async def ml_detail(alg_id: int):
    """Detalle de un algoritmo ML"""
    async with async_session() as session:
        r = await session.execute(
            text("SELECT * FROM hgu_ml_algoritmos WHERE id = :id"), {"id": alg_id})
        row = r.mappings().first()
        if not row:
            raise HTTPException(404, "Algoritmo no encontrado")
        return dict(row)


@app.post("/api/ml/enrich/{alg_id}", tags=["Algoritmos ML"])
async def ml_enrich(alg_id: int):
    """Generar propuesta IA para un algoritmo ML usando Groq"""
    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")

    async with async_session() as session:
        r = await session.execute(
            text("SELECT * FROM hgu_ml_algoritmos WHERE id = :id"), {"id": alg_id})
        alg = r.mappings().first()
        if not alg:
            raise HTTPException(404, "Algoritmo no encontrado")
        alg_data = dict(alg)

    user_msg = (
        f"Algoritmo: {alg_data['nombre']} ({alg_data['nombre_tecnico']})\n"
        f"Tipo ML: {alg_data['tipo_ml']}\n"
        f"Categoría farmacia: {alg_data['categoria_farmacia']}\n"
        f"Descripción: {alg_data['descripcion']}\n"
        f"Caso de uso: {alg_data['caso_uso']}\n"
        f"Ejemplo SIGFAR: {alg_data.get('ejemplo_sigfar', 'N/A')}\n"
        f"Librerías: {alg_data.get('librerias_python', 'N/A')}\n"
        f"Datos necesarios: {alg_data.get('datos_necesarios', 'N/A')}\n"
        f"Complejidad: {alg_data['complejidad']}\n"
        f"Estado actual: {alg_data['estado_sigfar_hub']}\n"
        f"Módulo SIGFAR: {alg_data.get('modulo_sigfar', 'N/A')}"
    )

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": ML_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.3, "max_tokens": 800
                },
                timeout=30
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = _re.sub(r'^```(?:json)?\s*', '', raw)
            raw = _re.sub(r'\s*```$', '', raw)
            data = json.loads(raw)
        except Exception as e:
            raise HTTPException(502, f"Error Groq: {str(e)[:200]}")

    propuesta = data.get("propuesta_ia", raw)

    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_ml_algoritmos
            SET propuesta_ia = :prop
            WHERE id = :id
        """), {"prop": propuesta, "id": alg_id})
        await session.commit()
        result = await session.execute(
            text("SELECT * FROM hgu_ml_algoritmos WHERE id = :id"), {"id": alg_id})
        return dict(result.mappings().first())


@app.post("/api/ml/toggle-favorito", tags=["Algoritmos ML"])
async def ml_toggle_fav(body: MlToggleFav):
    """Toggle favorito de un algoritmo ML"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_ml_algoritmos SET favorito = NOT favorito WHERE id = :id"),
            {"id": body.algoritmo_id})
        await session.commit()
        r = await session.execute(
            text("SELECT favorito FROM hgu_ml_algoritmos WHERE id = :id"),
            {"id": body.algoritmo_id})
        row = r.mappings().first()
        return {"id": body.algoritmo_id, "favorito": row["favorito"] if row else False}


@app.post("/api/ml/set-nota", tags=["Algoritmos ML"])
async def ml_set_nota(body: MlSetNota):
    """Guardar nota del usuario en un algoritmo ML"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_ml_algoritmos SET nota_usuario = :nota WHERE id = :id"),
            {"id": body.algoritmo_id, "nota": body.nota})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/ml/set-prioridad", tags=["Algoritmos ML"])
async def ml_set_prioridad(body: MlSetPrioridad):
    """Guardar prioridad personal del farmacéutico en un algoritmo ML"""
    if body.prioridad not in ('ALTA', 'MEDIA', 'BAJA'):
        raise HTTPException(400, "Prioridad debe ser ALTA, MEDIA o BAJA")
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_ml_algoritmos SET prioridad_usuario = :p WHERE id = :id"),
            {"id": body.algoritmo_id, "p": body.prioridad})
        await session.commit()
    return {"status": "OK"}


# ═══════════════════════════════════════════════════════════════════
# PROPUESTAS ESTRATÉGICAS — Generador inteligente de propuestas
# ═══════════════════════════════════════════════════════════════════

# --- Modelos Pydantic Propuestas ---

class PropuestaToggleFav(BaseModel):
    propuesta_id: int

class PropuestaSetNota(BaseModel):
    propuesta_id: int
    nota: str

class PropuestaSetPrioridad(BaseModel):
    propuesta_id: int
    prioridad: str

class PropuestaCambiarEstado(BaseModel):
    id: int
    estado: str


# --- Prompt para enriquecimiento IA de propuestas ---

PROPUESTAS_SYSTEM_PROMPT = """Eres un consultor estratégico experto en innovación farmacéutica hospitalaria e inteligencia artificial.
Dada esta propuesta estratégica, genera un plan de implementación detallado para SIGFAR Hub.
Responde SOLO un JSON válido (sin markdown, sin backticks) con esta estructura:
{"plan": "Plan detallado de 5-8 frases: fases de desarrollo, APIs y endpoints necesarios, modelo de datos, algoritmos ML a usar, interfaz propuesta, métricas de éxito, riesgos y mitigación, estimación de tiempo. Sé muy específico con el stack: FastAPI + PostgreSQL + React + Groq."}

Contexto SIGFAR Hub: plataforma multiagente IA para farmacia hospitalaria CHGUV. Stack: FastAPI + PostgreSQL + React. Módulos APEX: P15 (Dashboard paciente), P36 (Nutrición Artificial, 7 agentes), P37 (NPD domiciliaria), P40 (Scoring complejidad), P42 (Farmacocinética MAP Bayesiano), P43 (PROA 6 agentes). Datos: 422 pacientes activos, 2M registros consumos GestionAX, 2.692 medicamentos GFT. Sistemas hospital: Kardex, armarios estupefacientes, PYXIS, Versia (NP), ExactaMix, ChemoMaker, ICCA (UCI), OMA (planta), Hosix (HCE)."""

PROPUESTAS_GENERAR_PROMPT = """Eres un consultor estratégico experto en innovación farmacéutica hospitalaria e inteligencia artificial. Dado el contexto del Hospital General Universitario de Valencia, genera exactamente 5 propuestas estratégicas NUEVAS en formato JSON.

Contexto:
- Novedades recientes del Radar IA: {radar}
- APIs disponibles: {apis}
- Algoritmos ML catalogados: {ml}
- Datos reales hospital: 422 pacientes activos, 2M registros consumos, 2.692 medicamentos GFT
- Sistemas hospitalarios: Kardex, armarios estupefacientes, PYXIS, Versia (NP), ExactaMix (robots NP), ChemoMaker (robots quimio), ICCA (UCI), OMA (planta), Hosix (HCE)
- Propuestas YA existentes (NO repetir): {existentes}

Responde SOLO un JSON válido (sin markdown, sin backticks):
{{"propuestas": [{{"titulo": "...", "descripcion": "2-3 frases", "eje": "CLINICO|ECONOMICO|LOGISTICO|TECNICO|DIRECTIVO|FORMACION", "impacto": "MUY_ALTO|ALTO|MEDIO|BAJO", "preview_descripcion": "mini-descripción visual", "por_que_hub": "por qué APEX no puede", "apis_necesarias": "api1, api2", "ml_recomendado": "algoritmo1, algoritmo2", "datos_cruza": "qué datos necesita", "tiempo_estimado": "X semanas", "esfuerzo": 0-100, "impacto_score": 0-100, "demo_target": "para quién", "tags": "tag1,tag2"}}]}}

Prioriza propuestas que: 1) crucen datos de SIGFAR+GestionAX (imposible en APEX), 2) usen APIs ya conectadas, 3) tengan impacto medible, 4) sean demostrables para Substrate AI."""


# --- Endpoints Propuestas ---

PROPUESTAS_ESTADOS_VALIDOS = ('PROPUESTA', 'EN_ANALISIS', 'EN_DESARROLLO', 'PILOTO', 'PRODUCCION', 'DESCARTADA', 'GENERADA_IA')
PROPUESTAS_IMPACTO_MAP = {'MUY_ALTO': 4, 'ALTO': 3, 'MEDIO': 2, 'BAJO': 1}


@app.get("/api/propuestas/stats", tags=["Propuestas"])
async def propuestas_stats():
    """Estadísticas de propuestas estratégicas"""
    async with async_session() as session:
        r = await session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'EN_DESARROLLO') as en_desarrollo,
                COUNT(*) FILTER (WHERE estado = 'EN_ANALISIS') as en_analisis,
                COUNT(*) FILTER (WHERE estado = 'PILOTO') as piloto,
                COUNT(*) FILTER (WHERE estado = 'PRODUCCION') as produccion,
                COUNT(*) FILTER (WHERE estado = 'PROPUESTA') as propuestas,
                COUNT(*) FILTER (WHERE estado = 'GENERADA_IA') as generadas_ia,
                COUNT(*) FILTER (WHERE favorito = true) as favoritos
            FROM hgu_propuestas_estrategicas WHERE estado != 'DESCARTADA'
        """))
        stats = dict(r.mappings().first())

        r2 = await session.execute(text("""
            SELECT eje, COUNT(*) as n
            FROM hgu_propuestas_estrategicas WHERE estado != 'DESCARTADA'
            GROUP BY eje ORDER BY n DESC
        """))
        stats["por_eje"] = [dict(row) for row in r2.mappings().all()]

        r3 = await session.execute(text("""
            SELECT estado, COUNT(*) as n
            FROM hgu_propuestas_estrategicas
            GROUP BY estado ORDER BY n DESC
        """))
        stats["por_estado"] = [dict(row) for row in r3.mappings().all()]

        r4 = await session.execute(text("""
            SELECT impacto, COUNT(*) as n
            FROM hgu_propuestas_estrategicas WHERE estado != 'DESCARTADA'
            GROUP BY impacto ORDER BY n DESC
        """))
        stats["por_impacto"] = [dict(row) for row in r4.mappings().all()]

        return stats


@app.get("/api/propuestas/favoritos", tags=["Propuestas"])
async def propuestas_favoritos():
    """Lista de propuestas favoritas"""
    async with async_session() as session:
        r = await session.execute(text(
            "SELECT * FROM hgu_propuestas_estrategicas WHERE favorito = true AND estado != 'DESCARTADA' ORDER BY impacto_score DESC"
        ))
        return [dict(row) for row in r.mappings().all()]


@app.get("/api/propuestas/matriz", tags=["Propuestas"])
async def propuestas_matriz():
    """Datos para gráfico matriz impacto vs esfuerzo"""
    async with async_session() as session:
        r = await session.execute(text("""
            SELECT id, titulo, esfuerzo, impacto_score, eje, estado, impacto
            FROM hgu_propuestas_estrategicas
            WHERE estado NOT IN ('DESCARTADA')
            ORDER BY impacto_score DESC
        """))
        return [dict(row) for row in r.mappings().all()]


@app.get("/api/propuestas", tags=["Propuestas"])
async def propuestas_list(
    eje: str | None = None,
    estado: str | None = None,
    impacto: str | None = None,
    favorito: str | None = None,
    origen: str | None = None,
    buscar: str | None = None,
    skip: int = 0,
    limit: int = 100
):
    """Catálogo de propuestas estratégicas con filtros"""
    where = []
    params = {}
    if eje:
        where.append("eje = :eje")
        params["eje"] = eje
    if estado:
        where.append("estado = :estado")
        params["estado"] = estado
    if impacto:
        where.append("impacto = :impacto")
        params["impacto"] = impacto
    if favorito and favorito.lower() == 'true':
        where.append("favorito = true")
    if origen:
        where.append("origen = :origen")
        params["origen"] = origen
    if buscar:
        where.append("(titulo ILIKE :q OR descripcion ILIKE :q OR apis_necesarias ILIKE :q OR ml_recomendado ILIKE :q)")
        params["q"] = f"%{buscar}%"
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    params["skip"] = skip
    params["limit"] = limit
    async with async_session() as session:
        r = await session.execute(
            text(f"SELECT * FROM hgu_propuestas_estrategicas{clause} ORDER BY impacto_score DESC, fecha_creacion DESC OFFSET :skip LIMIT :limit"),
            params
        )
        return [dict(row) for row in r.mappings().all()]


@app.get("/api/propuestas/{prop_id}", tags=["Propuestas"])
async def propuestas_detail(prop_id: int):
    """Detalle de una propuesta estratégica"""
    async with async_session() as session:
        r = await session.execute(
            text("SELECT * FROM hgu_propuestas_estrategicas WHERE id = :id"), {"id": prop_id})
        row = r.mappings().first()
        if not row:
            raise HTTPException(404, "Propuesta no encontrada")
        return dict(row)


@app.post("/api/propuestas/generar", tags=["Propuestas"])
async def propuestas_generar():
    """Generador inteligente: cruza Radar+APIs+ML y genera 5 propuestas nuevas con IA"""
    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")

    async with async_session() as session:
        # Recopilar contexto
        r1 = await session.execute(text(
            "SELECT titulo, resumen_ia, categoria, relevancia FROM hgu_radar_items WHERE archivado = false ORDER BY relevancia DESC NULLS LAST LIMIT 20"
        ))
        radar_items = [dict(row) for row in r1.mappings().all()]

        r2 = await session.execute(text(
            "SELECT nombre, estado, bloque, caso_uso FROM hgu_hub_apis WHERE estado IN ('CONECTADA','EN_APEX') OR prioridad = 'P1'"
        ))
        apis = [dict(row) for row in r2.mappings().all()]

        r3 = await session.execute(text(
            "SELECT nombre, tipo_ml, categoria_farmacia, caso_uso FROM hgu_ml_algoritmos WHERE favorito = true OR relevancia >= 70"
        ))
        ml_algos = [dict(row) for row in r3.mappings().all()]

        r4 = await session.execute(text(
            "SELECT titulo FROM hgu_propuestas_estrategicas WHERE estado != 'DESCARTADA'"
        ))
        existentes = [row["titulo"] for row in r4.mappings().all()]

    radar_txt = "; ".join([f"{i['titulo']} (rel:{i['relevancia']})" for i in radar_items[:15]]) if radar_items else "Sin datos aún"
    apis_txt = "; ".join([f"{a['nombre']} ({a['estado']})" for a in apis]) if apis else "Sin APIs conectadas aún"
    ml_txt = "; ".join([f"{m['nombre']} ({m['tipo_ml']})" for m in ml_algos]) if ml_algos else "Sin algoritmos favoritos aún"
    exist_txt = ", ".join(existentes) if existentes else "Ninguna"

    prompt = PROPUESTAS_GENERAR_PROMPT.format(
        radar=radar_txt, apis=apis_txt, ml=ml_txt, existentes=exist_txt
    )

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "Genera 5 propuestas estratégicas nuevas para SIGFAR Hub. Formato JSON estricto."}
                    ],
                    "temperature": 0.7, "max_tokens": 2000
                },
                timeout=60
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = _re.sub(r'^```(?:json)?\s*', '', raw)
            raw = _re.sub(r'\s*```$', '', raw)
            data = json.loads(raw)
        except Exception as e:
            raise HTTPException(502, f"Error Groq: {str(e)[:300]}")

    propuestas = data.get("propuestas", [])
    inserted = []

    async with async_session() as session:
        for p in propuestas[:5]:
            await session.execute(text("""
                INSERT INTO hgu_propuestas_estrategicas
                    (titulo, descripcion, eje, impacto, estado, preview_descripcion, por_que_hub,
                     apis_necesarias, ml_recomendado, datos_cruza, tiempo_estimado,
                     esfuerzo, impacto_score, demo_target, origen, tags)
                VALUES
                    (:titulo, :desc, :eje, :impacto, 'GENERADA_IA', :preview, :hub,
                     :apis, :ml, :datos, :tiempo,
                     :esfuerzo, :impacto_score, :demo, 'GENERADA_IA', :tags)
            """), {
                "titulo": p.get("titulo", "Sin título"),
                "desc": p.get("descripcion", ""),
                "eje": p.get("eje", "CLINICO") if p.get("eje") in ('CLINICO','ECONOMICO','LOGISTICO','TECNICO','DIRECTIVO','FORMACION') else 'CLINICO',
                "impacto": p.get("impacto", "MEDIO") if p.get("impacto") in ('MUY_ALTO','ALTO','MEDIO','BAJO') else 'MEDIO',
                "preview": p.get("preview_descripcion", ""),
                "hub": p.get("por_que_hub", ""),
                "apis": p.get("apis_necesarias", ""),
                "ml": p.get("ml_recomendado", ""),
                "datos": p.get("datos_cruza", ""),
                "tiempo": p.get("tiempo_estimado", ""),
                "esfuerzo": min(100, max(0, int(p.get("esfuerzo", 50)))),
                "impacto_score": min(100, max(0, int(p.get("impacto_score", 50)))),
                "demo": p.get("demo_target", ""),
                "tags": p.get("tags", "")
            })
            inserted.append(p)
        await session.commit()

    return {"status": "OK", "generadas": len(inserted), "propuestas": inserted}


@app.post("/api/propuestas/analizar/{prop_id}", tags=["Propuestas"])
async def propuestas_analizar(prop_id: int):
    """Generar plan detallado de implementación con IA"""
    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY no configurada")

    async with async_session() as session:
        r = await session.execute(
            text("SELECT * FROM hgu_propuestas_estrategicas WHERE id = :id"), {"id": prop_id})
        prop = r.mappings().first()
        if not prop:
            raise HTTPException(404, "Propuesta no encontrada")
        prop_data = dict(prop)

    user_msg = (
        f"Propuesta: {prop_data['titulo']}\n"
        f"Eje: {prop_data['eje']}\n"
        f"Descripción: {prop_data['descripcion']}\n"
        f"APIs necesarias: {prop_data.get('apis_necesarias', 'N/A')}\n"
        f"ML recomendado: {prop_data.get('ml_recomendado', 'N/A')}\n"
        f"Datos que cruza: {prop_data.get('datos_cruza', 'N/A')}\n"
        f"Impacto: {prop_data['impacto']}\n"
        f"Tiempo estimado: {prop_data.get('tiempo_estimado', 'N/A')}"
    )

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": PROPUESTAS_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.3, "max_tokens": 1000
                },
                timeout=30
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = _re.sub(r'^```(?:json)?\s*', '', raw)
            raw = _re.sub(r'\s*```$', '', raw)
            data = json.loads(raw)
        except Exception as e:
            raise HTTPException(502, f"Error Groq: {str(e)[:200]}")

    plan = data.get("plan", raw)

    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_propuestas_estrategicas
            SET propuesta_ia = :plan, fecha_actualizacion = NOW()
            WHERE id = :id
        """), {"plan": plan, "id": prop_id})
        await session.commit()
        result = await session.execute(
            text("SELECT * FROM hgu_propuestas_estrategicas WHERE id = :id"), {"id": prop_id})
        return dict(result.mappings().first())


@app.post("/api/propuestas/cambiar-estado", tags=["Propuestas"])
async def propuestas_cambiar_estado(body: PropuestaCambiarEstado):
    """Cambiar estado de una propuesta"""
    if body.estado not in PROPUESTAS_ESTADOS_VALIDOS:
        raise HTTPException(400, f"Estado inválido. Válidos: {PROPUESTAS_ESTADOS_VALIDOS}")
    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_propuestas_estrategicas
            SET estado = :estado, fecha_actualizacion = NOW()
            WHERE id = :id
        """), {"estado": body.estado, "id": body.id})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/propuestas/toggle-favorito", tags=["Propuestas"])
async def propuestas_toggle_fav(body: PropuestaToggleFav):
    """Toggle favorito de una propuesta"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_propuestas_estrategicas SET favorito = NOT favorito WHERE id = :id"),
            {"id": body.propuesta_id})
        await session.commit()
        r = await session.execute(
            text("SELECT favorito FROM hgu_propuestas_estrategicas WHERE id = :id"),
            {"id": body.propuesta_id})
        row = r.mappings().first()
        return {"id": body.propuesta_id, "favorito": row["favorito"] if row else False}


@app.post("/api/propuestas/set-nota", tags=["Propuestas"])
async def propuestas_set_nota(body: PropuestaSetNota):
    """Guardar nota del usuario en una propuesta"""
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_propuestas_estrategicas SET nota_usuario = :nota, fecha_actualizacion = NOW() WHERE id = :id"),
            {"id": body.propuesta_id, "nota": body.nota})
        await session.commit()
    return {"status": "OK"}


@app.post("/api/propuestas/set-prioridad", tags=["Propuestas"])
async def propuestas_set_prioridad(body: PropuestaSetPrioridad):
    """Guardar prioridad personal del farmacéutico"""
    if body.prioridad not in ('ALTA', 'MEDIA', 'BAJA'):
        raise HTTPException(400, "Prioridad debe ser ALTA, MEDIA o BAJA")
    async with async_session() as session:
        await session.execute(
            text("UPDATE hgu_propuestas_estrategicas SET prioridad_usuario = :p, fecha_actualizacion = NOW() WHERE id = :id"),
            {"id": body.propuesta_id, "p": body.prioridad})
        await session.commit()
    return {"status": "OK"}


# ═══════════════════════════════════════════════════════════════════
# STACK — Mapa de Arquitectura del ecosistema SIGFAR
# ═══════════════════════════════════════════════════════════════════


async def _stack_test_component(client: httpx.AsyncClient, comp: dict) -> dict:
    """Prueba conectividad real de un componente del stack."""
    url = comp.get("url") or comp.get("url_docs")
    if not url:
        return {"ok": None, "latencia_ms": 0, "error": "Sin URL de test"}
    if not url.startswith("http"):
        return {"ok": None, "latencia_ms": 0, "error": "URL no testeable"}
    try:
        import time
        t0 = time.time()
        resp = await client.get(url, timeout=10.0, follow_redirects=True)
        latencia = int((time.time() - t0) * 1000)
        return {"ok": resp.status_code < 400, "latencia_ms": latencia,
                "status_code": resp.status_code}
    except Exception as e:
        return {"ok": False, "latencia_ms": 0, "error": str(e)[:200]}


@app.get("/api/stack/stats", tags=["Stack"])
async def stack_stats():
    """Estadísticas del stack de componentes"""
    async with async_session() as session:
        total = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_stack_components"))).scalar()
        conectados = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_stack_components WHERE estado = 'CONECTADO'"))).scalar()
        pendientes = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_stack_components WHERE estado = 'PENDIENTE'"))).scalar()
        futuros = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_stack_components WHERE estado = 'FUTURO'"))).scalar()
        errores = (await session.execute(
            text("SELECT COUNT(*) FROM hgu_stack_components WHERE estado = 'ERROR'"))).scalar()
        por_grupo = await session.execute(
            text("SELECT grupo, COUNT(*) n FROM hgu_stack_components GROUP BY grupo ORDER BY grupo"))
        grupos = {r["grupo"]: r["n"] for r in por_grupo.mappings().all()}
        por_tipo = await session.execute(
            text("SELECT tipo, COUNT(*) n FROM hgu_stack_components GROUP BY tipo ORDER BY n DESC"))
        tipos = {r["tipo"]: r["n"] for r in por_tipo.mappings().all()}
        return {
            "total": total, "conectados": conectados, "pendientes": pendientes,
            "futuros": futuros, "errores": errores,
            "por_grupo": grupos, "por_tipo": tipos
        }


@app.get("/api/stack/components", tags=["Stack"])
async def stack_components(grupo: str | None = None, estado: str | None = None,
                           tipo: str | None = None):
    """Lista todos los componentes del stack con filtros opcionales"""
    conds = []
    params = {}
    if grupo:
        conds.append("grupo = :grupo")
        params["grupo"] = grupo
    if estado:
        conds.append("estado = :estado")
        params["estado"] = estado
    if tipo:
        conds.append("tipo = :tipo")
        params["tipo"] = tipo
    where = "WHERE " + " AND ".join(conds) if conds else ""
    sql = f"SELECT * FROM hgu_stack_components {where} ORDER BY posicion_diagrama, grupo, orden, nombre"
    async with async_session() as session:
        result = await session.execute(text(sql), params)
        rows = result.mappings().all()
        out = []
        for r in rows:
            d = dict(r)
            if d.get("detalles") and isinstance(d["detalles"], str):
                try:
                    d["detalles"] = json.loads(d["detalles"])
                except Exception:
                    pass
            out.append(d)
        return out


@app.get("/api/stack/components/{comp_id}", tags=["Stack"])
async def stack_component_detail(comp_id: int):
    """Detalle de un componente del stack"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_stack_components WHERE id = :id"), {"id": comp_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "Componente no encontrado")
        d = dict(row)
        if d.get("detalles") and isinstance(d["detalles"], str):
            try:
                d["detalles"] = json.loads(d["detalles"])
            except Exception:
                pass
        return d


@app.post("/api/stack/test/{comp_id}", tags=["Stack"])
async def stack_test_component(comp_id: int):
    """Testear conectividad de un componente en tiempo real"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_stack_components WHERE id = :id"), {"id": comp_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(404, "Componente no encontrado")
        comp_data = dict(row)

    async with httpx.AsyncClient() as client:
        test_result = await _stack_test_component(client, comp_data)

    # Actualizar estado si el test devolvió un resultado real
    if test_result["ok"] is not None:
        new_estado = "CONECTADO" if test_result["ok"] else "ERROR"
        async with async_session() as session:
            await session.execute(text("""
                UPDATE hgu_stack_components SET estado = :estado WHERE id = :id
            """), {"estado": new_estado, "id": comp_id})
            await session.commit()

    return {
        "comp_id": comp_id, "nombre": comp_data["nombre"],
        **test_result
    }


@app.post("/api/stack/test-all", tags=["Stack"])
async def stack_test_all():
    """Testear conectividad de TODOS los componentes con URL"""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT * FROM hgu_stack_components ORDER BY grupo, orden"))
        components = [dict(r) for r in result.mappings().all()]

    results = []
    async with httpx.AsyncClient() as client:
        for comp in components:
            test_result = await _stack_test_component(client, comp)
            if test_result["ok"] is not None:
                new_estado = "CONECTADO" if test_result["ok"] else "ERROR"
                async with async_session() as session:
                    await session.execute(text(
                        "UPDATE hgu_stack_components SET estado = :estado WHERE id = :id"
                    ), {"estado": new_estado, "id": comp["id"]})
                    await session.commit()
            results.append({
                "comp_id": comp["id"], "nombre": comp["nombre"],
                "grupo": comp["grupo"], "tipo": comp["tipo"],
                **test_result
            })
            await asyncio.sleep(0.3)

    ok_count = sum(1 for r in results if r.get("ok") is True)
    fail_count = sum(1 for r in results if r.get("ok") is False)
    skip_count = sum(1 for r in results if r.get("ok") is None)
    return {
        "total": len(results), "ok": ok_count,
        "fail": fail_count, "sin_url": skip_count,
        "results": results
    }


# ═══════════════════════════════════════════════════════════════
#  MÓDULO F — Evidencia SIGFAR
#  Benchmarking científico, Panel Futuro vs Realidad, Papers
# ═══════════════════════════════════════════════════════════════

SIGFAR_CONTEXT_PROMPT = """SIGFAR es una plataforma de IA para farmacia hospitalaria del Hospital General Universitario de Valencia que incluye:
- P15: Dashboard seguimiento pacientes con pipeline multiagente EM/PRM (6 categorías PCNE v9.1)
- P36: Nutrición Artificial con 7 agentes IA (screening, requerimientos, fórmulas, cobertura, balance hídrico, analítica, plan)
- P37: Nutrición Parenteral Domiciliaria con IA
- P40: Dashboard multiagente con scoring complejidad (14 dimensiones, 53 puntos, 4 niveles)
- P42: Farmacocinética clínica con estimación MAP Bayesiana (vancomicina, gentamicina, amikacina)
- P43: PROA antimicrobianos con 6 agentes IA (evaluación, cultivos, desescalada, duración, profilaxis, educación)
- Hub: Radar inteligencia competitiva, catálogo APIs/ML, propuestas estratégicas con IA, cuadro mandos dirección con Sigfarita (asistente IA jefatura)
- Integraciones: ClinicalTrials.gov, PubMed, CIMA/AEMPS, Groq/Llama 3.3 70B"""


# ─── GET /api/evidencia/benchmarks ─────────────────────────────
@app.get("/api/evidencia/benchmarks", tags=["Evidencia"])
async def evidencia_benchmarks():
    async with async_session() as session:
        rows = await session.execute(text("""
            SELECT b.*,
                   (SELECT count(*) FROM hgu_evidencia_comparativas WHERE benchmark_id = b.id) as num_comparativas
            FROM hgu_evidencia_benchmarks b
            ORDER BY b.fecha_analisis DESC
        """))
        items = [dict(r._mapping) for r in rows]
        for it in items:
            if it.get("fecha_analisis"):
                it["fecha_analisis"] = str(it["fecha_analisis"])
            if it.get("json_analisis") and isinstance(it["json_analisis"], str):
                it["json_analisis"] = json.loads(it["json_analisis"])
        return items


# ─── GET /api/evidencia/benchmarks/{id} ────────────────────────
@app.get("/api/evidencia/benchmarks/{bench_id}", tags=["Evidencia"])
async def evidencia_benchmark_detail(bench_id: int):
    async with async_session() as session:
        row = await session.execute(text(
            "SELECT * FROM hgu_evidencia_benchmarks WHERE id = :id"
        ), {"id": bench_id})
        bench = row.mappings().first()
        if not bench:
            raise HTTPException(404, "Benchmark no encontrado")
        bench = dict(bench)
        if bench.get("fecha_analisis"):
            bench["fecha_analisis"] = str(bench["fecha_analisis"])
        if bench.get("json_analisis") and isinstance(bench["json_analisis"], str):
            bench["json_analisis"] = json.loads(bench["json_analisis"])

        comps = await session.execute(text(
            "SELECT * FROM hgu_evidencia_comparativas WHERE benchmark_id = :id ORDER BY orden"
        ), {"id": bench_id})
        comparativas = [dict(r._mapping) for r in comps]

        # Conteos
        por_estado = {}
        por_dominio = {}
        pioneros = 0
        for c in comparativas:
            e = c.get("estado_sigfar", "")
            d = c.get("dominio_sefh", "")
            por_estado[e] = por_estado.get(e, 0) + 1
            por_dominio[d] = por_dominio.get(d, 0) + 1
            if c.get("es_pionero"):
                pioneros += 1

        bench["comparativas"] = comparativas
        bench["por_estado"] = por_estado
        bench["por_dominio"] = por_dominio
        bench["total_pioneros"] = pioneros
        return bench


# ─── POST /api/evidencia/buscar-articulo ─────────────────────
@app.post("/api/evidencia/buscar-articulo", tags=["Evidencia"])
async def evidencia_buscar_articulo(body: dict):
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(400, "Introduce DOI, PMID o título")

    resultados = []
    is_doi = "10." in query and "/" in query
    is_pmid = query.isdigit() and 6 <= len(query) <= 9

    async with httpx.AsyncClient(timeout=20) as client:
        if is_doi:
            # CrossRef por DOI
            try:
                cr = await client.get(f"https://api.crossref.org/works/{query}",
                    headers={"User-Agent": "SIGFAR-Hub/1.0 (mailto:sigfar@chguv.es)"})
                if cr.status_code == 200:
                    w = cr.json().get("message", {})
                    titulo_cr = " ".join(w.get("title", ["Sin título"]))
                    autores_cr = ", ".join([f"{a.get('family', '')} {a.get('given', '')}" for a in w.get("author", [])])
                    revista_cr = " ".join(w.get("container-title", [""]))
                    anio_cr = None
                    dp = w.get("published-print", w.get("published-online", {}))
                    if dp and "date-parts" in dp and dp["date-parts"]:
                        anio_cr = dp["date-parts"][0][0] if dp["date-parts"][0] else None
                    abstract_cr = w.get("abstract", "")
                    if abstract_cr:
                        abstract_cr = _re.sub(r"<[^>]+>", "", abstract_cr)
                    resultados.append({
                        "titulo": titulo_cr, "autores": autores_cr, "revista": revista_cr,
                        "anio": anio_cr, "doi": query, "abstract": abstract_cr,
                        "url_pdf_oa": None, "fuente": "CrossRef"
                    })
            except Exception:
                pass
            # Unpaywall
            try:
                up = await client.get(f"https://api.unpaywall.org/v2/{query}?email=sigfar@chguv.es")
                if up.status_code == 200:
                    ud = up.json()
                    oa_url = None
                    best = ud.get("best_oa_location")
                    if best:
                        oa_url = best.get("url_for_pdf") or best.get("url")
                    if resultados:
                        resultados[0]["url_pdf_oa"] = oa_url
                    if not resultados:
                        resultados.append({
                            "titulo": ud.get("title", ""), "autores": "", "revista": ud.get("journal_name", ""),
                            "anio": ud.get("year"), "doi": query, "abstract": "",
                            "url_pdf_oa": oa_url, "fuente": "Unpaywall"
                        })
            except Exception:
                pass

        elif is_pmid:
            # PubMed efetch por PMID
            try:
                pm = await client.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={query}&retmode=xml")
                if pm.status_code == 200:
                    xml = pm.text
                    titulo_pm = _re.search(r"<ArticleTitle>(.+?)</ArticleTitle>", xml, _re.DOTALL)
                    abstract_pm = _re.search(r"<AbstractText[^>]*>(.+?)</AbstractText>", xml, _re.DOTALL)
                    journal_pm = _re.search(r"<Title>(.+?)</Title>", xml)
                    year_pm = _re.search(r"<PubDate>\s*<Year>(\d{4})</Year>", xml)
                    doi_pm = _re.search(r'<ArticleId IdType="doi">(.+?)</ArticleId>', xml)
                    authors_pm = _re.findall(r"<LastName>(.+?)</LastName>\s*<ForeName>(.+?)</ForeName>", xml)
                    resultados.append({
                        "titulo": _re.sub(r"<[^>]+>", "", titulo_pm.group(1)) if titulo_pm else "",
                        "autores": ", ".join([f"{a[0]} {a[1]}" for a in authors_pm[:6]]) + ("..." if len(authors_pm) > 6 else ""),
                        "revista": journal_pm.group(1) if journal_pm else "",
                        "anio": int(year_pm.group(1)) if year_pm else None,
                        "doi": doi_pm.group(1) if doi_pm else None,
                        "pmid": query,
                        "abstract": _re.sub(r"<[^>]+>", "", abstract_pm.group(1)) if abstract_pm else "",
                        "url_pdf_oa": None, "fuente": "PubMed"
                    })
            except Exception:
                pass

        else:
            # Búsqueda por texto libre — CrossRef + PubMed
            try:
                safe_q = query.replace(" ", "+")
                cr = await client.get(f"https://api.crossref.org/works?query={safe_q}&rows=6",
                    headers={"User-Agent": "SIGFAR-Hub/1.0 (mailto:sigfar@chguv.es)"})
                if cr.status_code == 200:
                    for w in cr.json().get("message", {}).get("items", []):
                        titulo_w = " ".join(w.get("title", ["?"]))
                        autores_w = ", ".join([f"{a.get('family', '')} {a.get('given', '')}" for a in w.get("author", [])[:4]])
                        revista_w = " ".join(w.get("container-title", [""]))
                        dp = w.get("published-print", w.get("published-online", {}))
                        anio_w = dp["date-parts"][0][0] if dp and dp.get("date-parts") and dp["date-parts"][0] else None
                        abstract_w = _re.sub(r"<[^>]+>", "", w.get("abstract", "")) if w.get("abstract") else ""
                        resultados.append({
                            "titulo": titulo_w, "autores": autores_w, "revista": revista_w,
                            "anio": anio_w, "doi": w.get("DOI"), "abstract": abstract_w,
                            "url_pdf_oa": None, "fuente": "CrossRef"
                        })
            except Exception:
                pass
            try:
                pm = await client.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=4&retmode=json")
                if pm.status_code == 200:
                    ids = pm.json().get("esearchresult", {}).get("idlist", [])
                    for pid in ids:
                        ef = await client.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=xml")
                        if ef.status_code == 200:
                            xml = ef.text
                            t = _re.search(r"<ArticleTitle>(.+?)</ArticleTitle>", xml, _re.DOTALL)
                            ab = _re.search(r"<AbstractText[^>]*>(.+?)</AbstractText>", xml, _re.DOTALL)
                            j = _re.search(r"<Title>(.+?)</Title>", xml)
                            y = _re.search(r"<PubDate>\s*<Year>(\d{4})</Year>", xml)
                            d = _re.search(r'<ArticleId IdType="doi">(.+?)</ArticleId>', xml)
                            aus = _re.findall(r"<LastName>(.+?)</LastName>\s*<ForeName>(.+?)</ForeName>", xml)
                            # Deduplicar por DOI
                            doi_val = d.group(1) if d else None
                            if doi_val and any(r.get("doi") == doi_val for r in resultados):
                                continue
                            resultados.append({
                                "titulo": _re.sub(r"<[^>]+>", "", t.group(1)) if t else "",
                                "autores": ", ".join([f"{a[0]} {a[1]}" for a in aus[:4]]) + ("..." if len(aus) > 4 else ""),
                                "revista": j.group(1) if j else "",
                                "anio": int(y.group(1)) if y else None,
                                "doi": doi_val, "pmid": pid,
                                "abstract": _re.sub(r"<[^>]+>", "", ab.group(1)) if ab else "",
                                "url_pdf_oa": None, "fuente": "PubMed"
                            })
            except Exception:
                pass

    return {"query": query, "tipo": "DOI" if is_doi else "PMID" if is_pmid else "TEXTO", "resultados": resultados[:10]}


# ─── POST /api/evidencia/benchmarks/analizar ───────────────────
@app.post("/api/evidencia/benchmarks/analizar", tags=["Evidencia"])
async def evidencia_analizar_articulo(body: dict):
    titulo = body.get("titulo_articulo", "").strip()
    contenido = body.get("contenido_texto", "").strip()
    doi = body.get("doi", "")
    url_articulo = body.get("url_articulo", "").strip()
    autores = body.get("autores", "")
    revista = body.get("revista", "")
    anio = body.get("anio")

    # Si hay URL, intentar fetch del contenido
    if url_articulo and not contenido:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url_articulo, follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 SIGFAR-Hub/1.0"})
                if resp.status_code == 200:
                    html = resp.text
                    # Extraer texto limpio del HTML
                    text_clean = _re.sub(r"<script[^>]*>.*?</script>", "", html, flags=_re.DOTALL)
                    text_clean = _re.sub(r"<style[^>]*>.*?</style>", "", text_clean, flags=_re.DOTALL)
                    text_clean = _re.sub(r"<[^>]+>", " ", text_clean)
                    text_clean = _re.sub(r"\s+", " ", text_clean).strip()
                    if len(text_clean) > 200:
                        contenido = text_clean
        except Exception:
            pass

    # Si hay DOI pero no contenido, buscar abstract
    if doi and not contenido:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                cr = await client.get(f"https://api.crossref.org/works/{doi}",
                    headers={"User-Agent": "SIGFAR-Hub/1.0 (mailto:sigfar@chguv.es)"})
                if cr.status_code == 200:
                    w = cr.json().get("message", {})
                    ab = w.get("abstract", "")
                    if ab:
                        contenido = _re.sub(r"<[^>]+>", "", ab)
                    if not titulo:
                        titulo = " ".join(w.get("title", [""]))
                    if not autores:
                        autores = ", ".join([f"{a.get('family', '')} {a.get('given', '')}" for a in w.get("author", [])[:6]])
                    if not revista:
                        revista = " ".join(w.get("container-title", [""]))
                    dp = w.get("published-print", w.get("published-online", {}))
                    if not anio and dp and dp.get("date-parts") and dp["date-parts"][0]:
                        anio = dp["date-parts"][0][0]
        except Exception:
            pass

    if not titulo:
        raise HTTPException(400, "titulo_articulo es obligatorio")
    if not contenido:
        raise HTTPException(400, "No se pudo obtener contenido del artículo. Pega el texto manualmente.")

    # Truncar a ~12000 chars para no exceder contexto Groq
    contenido_truncado = contenido[:12000]

    prompt_sistema = f"""Eres un analista de tecnología farmacéutica hospitalaria.
{SIGFAR_CONTEXT_PROMPT}

Analiza el artículo y genera un JSON con esta estructura:
{{
  "resumen_articulo": "resumen de 3-4 líneas",
  "cobertura_global": porcentaje 0-100 de lo que SIGFAR cubre del artículo,
  "comparativas": [
    {{
      "funcionalidad_articulo": "lo que el artículo describe",
      "dominio_sefh": "AT_PRESENCIAL|AT_NO_PRESENCIAL|GESTION_LOGISTICA|EDUCACION|INVESTIGACION",
      "estado_sigfar": "IMPLEMENTADO|PARCIAL|PLANIFICADO|NO_CONTEMPLADO|SUPERA_ARTICULO",
      "modulo_sigfar": "P15|P36|P37|P40|P42|P43|Hub|—",
      "descripcion_sigfar": "qué tiene SIGFAR para esta funcionalidad",
      "ventaja_sigfar": "en qué SIGFAR va más allá (si aplica, null si no)",
      "gap": "qué falta (si aplica, null si no)",
      "es_pionero": true o false (true si SIGFAR tiene algo que el artículo ni menciona)
    }}
  ]
}}
IMPORTANTE: Incluye también funcionalidades que SIGFAR tiene y el artículo NO menciona (como PIONERO/SUPERA_ARTICULO).
Responde SOLO con el JSON, sin markdown ni explicaciones."""

    prompt_user = f"TÍTULO: {titulo}\n\nTEXTO DEL ARTÍCULO:\n{contenido_truncado}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.3,
                "max_tokens": 3000,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_user}
                ]
            }
        )
    if resp.status_code != 200:
        raise HTTPException(502, f"Error Groq: {resp.status_code} — {resp.text[:300]}")

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    # Limpiar posible markdown wrapping
    if raw.startswith("```"):
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```$", "", raw)

    try:
        analisis = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(502, f"Groq devolvió JSON inválido: {raw[:500]}")

    resumen = analisis.get("resumen_articulo", "")
    cobertura = analisis.get("cobertura_global", 50)
    comparativas = analisis.get("comparativas", [])

    # Insertar benchmark
    async with async_session() as session:
        result = await session.execute(text("""
            INSERT INTO hgu_evidencia_benchmarks
                (titulo_articulo, autores, revista, anio, resumen_articulo, cobertura_global, json_analisis)
            VALUES (:titulo, :autores, :revista, :anio, :resumen, :cobertura, :json_raw)
            RETURNING id
        """), {
            "titulo": titulo, "autores": autores, "revista": revista,
            "anio": anio, "resumen": resumen, "cobertura": cobertura,
            "json_raw": json.dumps(analisis, ensure_ascii=False)
        })
        bench_id = result.scalar()

        # Insertar comparativas
        for idx, comp in enumerate(comparativas):
            estado = comp.get("estado_sigfar", "NO_CONTEMPLADO")
            if estado not in ("IMPLEMENTADO", "PARCIAL", "PLANIFICADO", "NO_CONTEMPLADO", "SUPERA_ARTICULO"):
                estado = "NO_CONTEMPLADO"
            dominio = comp.get("dominio_sefh", "AT_PRESENCIAL")
            if dominio not in ("AT_PRESENCIAL", "AT_NO_PRESENCIAL", "GESTION_LOGISTICA", "EDUCACION", "INVESTIGACION"):
                dominio = "AT_PRESENCIAL"

            await session.execute(text("""
                INSERT INTO hgu_evidencia_comparativas
                    (benchmark_id, funcionalidad_articulo, dominio_sefh, estado_sigfar,
                     modulo_sigfar, descripcion_sigfar, ventaja_sigfar, gap, es_pionero, orden)
                VALUES (:bid, :func, :dom, :estado, :mod, :desc, :ventaja, :gap, :pionero, :orden)
            """), {
                "bid": bench_id,
                "func": comp.get("funcionalidad_articulo", ""),
                "dom": dominio,
                "estado": estado,
                "mod": comp.get("modulo_sigfar"),
                "desc": comp.get("descripcion_sigfar"),
                "ventaja": comp.get("ventaja_sigfar"),
                "gap": comp.get("gap"),
                "pionero": bool(comp.get("es_pionero", False)),
                "orden": idx + 1
            })
        await session.commit()

    # Devolver benchmark completo
    return await evidencia_benchmark_detail(bench_id)


# ─── POST /api/evidencia/benchmarks/{id}/toggle-favorito ──────
@app.post("/api/evidencia/benchmarks/{bench_id}/toggle-favorito", tags=["Evidencia"])
async def evidencia_toggle_favorito(bench_id: int):
    async with async_session() as session:
        await session.execute(text(
            "UPDATE hgu_evidencia_benchmarks SET favorito = NOT favorito WHERE id = :id"
        ), {"id": bench_id})
        await session.commit()
        row = await session.execute(text(
            "SELECT favorito FROM hgu_evidencia_benchmarks WHERE id = :id"
        ), {"id": bench_id})
        val = row.scalar()
        return {"id": bench_id, "favorito": val}


# ─── POST /api/evidencia/benchmarks/{id}/set-nota ─────────────
@app.post("/api/evidencia/benchmarks/{bench_id}/set-nota", tags=["Evidencia"])
async def evidencia_set_nota(bench_id: int, body: dict):
    nota = body.get("nota", "")
    async with async_session() as session:
        await session.execute(text(
            "UPDATE hgu_evidencia_benchmarks SET nota_usuario = :nota WHERE id = :id"
        ), {"id": bench_id, "nota": nota})
        await session.commit()
        return {"id": bench_id, "nota_usuario": nota}


# ─── DELETE /api/evidencia/benchmarks/{id} ─────────────────────
@app.delete("/api/evidencia/benchmarks/{bench_id}", tags=["Evidencia"])
async def evidencia_delete_benchmark(bench_id: int):
    async with async_session() as session:
        await session.execute(text(
            "DELETE FROM hgu_evidencia_benchmarks WHERE id = :id"
        ), {"id": bench_id})
        await session.commit()
        return {"deleted": bench_id}


# ─── GET /api/evidencia/panel ──────────────────────────────────
@app.get("/api/evidencia/panel", tags=["Evidencia"])
async def evidencia_panel():
    """Panel Futuro vs Realidad — agrega todos los benchmarks."""
    async with async_session() as session:
        # Cobertura media
        cob = await session.execute(text(
            "SELECT COALESCE(AVG(cobertura_global), 0) FROM hgu_evidencia_benchmarks"
        ))
        cobertura_media = round(cob.scalar() or 0)

        # Conteos por dominio y estado
        rows = await session.execute(text("""
            SELECT dominio_sefh, estado_sigfar, count(*) as cnt
            FROM hgu_evidencia_comparativas
            GROUP BY dominio_sefh, estado_sigfar
        """))
        dominios = {}
        for r in rows:
            d = r.dominio_sefh or "OTRO"
            if d not in dominios:
                dominios[d] = {"IMPLEMENTADO": 0, "PARCIAL": 0, "PLANIFICADO": 0,
                               "NO_CONTEMPLADO": 0, "SUPERA_ARTICULO": 0, "total": 0}
            dominios[d][r.estado_sigfar] = r.cnt
            dominios[d]["total"] += r.cnt

        # Calcular % implementación por dominio
        for d in dominios:
            total = dominios[d]["total"]
            impl = dominios[d]["IMPLEMENTADO"] + dominios[d]["SUPERA_ARTICULO"]
            dominios[d]["pct_implementado"] = round(impl / total * 100) if total else 0

        # Funcionalidades pioneras
        pioneros = await session.execute(text("""
            SELECT c.*, b.titulo_articulo
            FROM hgu_evidencia_comparativas c
            JOIN hgu_evidencia_benchmarks b ON b.id = c.benchmark_id
            WHERE c.es_pionero = TRUE
            ORDER BY c.orden
        """))
        pioneros_list = [dict(r._mapping) for r in pioneros]

        # Total benchmarks
        total_bench = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_benchmarks"
        ))

        return {
            "cobertura_media": cobertura_media,
            "total_benchmarks": total_bench.scalar(),
            "dominios": dominios,
            "pioneros": pioneros_list
        }


# ─── POST /api/evidencia/generar-paper ─────────────────────────
@app.post("/api/evidencia/generar-paper", tags=["Evidencia"])
async def evidencia_generar_paper(body: dict):
    benchmark_ids = body.get("benchmark_ids", [])
    if not benchmark_ids:
        raise HTTPException(400, "benchmark_ids obligatorio (array de IDs)")

    # Cargar benchmarks + comparativas
    datos_texto = ""
    async with async_session() as session:
        for bid in benchmark_ids:
            bench = await session.execute(text(
                "SELECT * FROM hgu_evidencia_benchmarks WHERE id = :id"
            ), {"id": bid})
            b = bench.mappings().first()
            if not b:
                continue
            datos_texto += f"\n\n### Artículo: {b['titulo_articulo']}"
            datos_texto += f"\nAutores: {b['autores'] or 'N/D'} | Revista: {b['revista'] or 'N/D'} | Año: {b['anio'] or 'N/D'}"
            datos_texto += f"\nCobertura SIGFAR: {b['cobertura_global']}%"
            datos_texto += f"\nResumen: {b['resumen_articulo'] or ''}"

            comps = await session.execute(text(
                "SELECT * FROM hgu_evidencia_comparativas WHERE benchmark_id = :id ORDER BY orden"
            ), {"id": bid})
            datos_texto += "\n\n| Funcionalidad artículo | Estado SIGFAR | Módulo | Ventaja SIGFAR | Gap |"
            datos_texto += "\n|---|---|---|---|---|"
            for c in comps:
                datos_texto += f"\n| {c.funcionalidad_articulo} | {c.estado_sigfar} | {c.modulo_sigfar or '—'} | {c.ventaja_sigfar or '—'} | {c.gap or '—'} |"

    if not datos_texto.strip():
        raise HTTPException(404, "No se encontraron benchmarks con esos IDs")

    prompt_sistema = f"""Eres un farmacéutico investigador experto en redacción científica.
{SIGFAR_CONTEXT_PROMPT}

Con los datos de estos análisis comparativos, genera un borrador de artículo científico en español con estructura IMRyD.
El artículo debe incluir:
- Título propuesto (conciso, publicable en Farmacia Hospitalaria)
- Resumen estructurado: Objetivo, Métodos, Resultados, Conclusiones (250 palabras)
- Introducción: contexto de la IA en farmacia hospitalaria, justificación, estado del arte
- Material y Métodos: descripción de la arquitectura SIGFAR Hub (FastAPI + PostgreSQL + React + Groq/Llama), módulos, tecnologías
- Resultados: tabla comparativa SIGFAR vs literatura, % cobertura por dominio, funcionalidades pioneras
- Discusión: innovaciones clave, limitaciones (estudio piloto, mono-centro, sin validación externa), líneas futuras (marcado CE, Substrate AI)
- Conclusiones
- Bibliografía (usar los artículos analizados como referencias)
Formato: Markdown con ## para secciones y | para tablas."""

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.4,
                "max_tokens": 4000,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Datos de los análisis comparativos:\n{datos_texto}"}
                ]
            }
        )
    if resp.status_code != 200:
        raise HTTPException(502, f"Error Groq: {resp.status_code} — {resp.text[:300]}")

    contenido = resp.json()["choices"][0]["message"]["content"].strip()

    # Extraer título (primera línea con # o ##)
    titulo = "Borrador artículo SIGFAR Hub"
    for linea in contenido.split("\n"):
        linea_strip = linea.strip().lstrip("#").strip()
        if linea_strip:
            titulo = linea_strip[:200]
            break

    # Guardar en BD
    async with async_session() as session:
        result = await session.execute(text("""
            INSERT INTO hgu_evidencia_papers
                (titulo, contenido_markdown, benchmarks_usados, estado)
            VALUES (:titulo, :contenido, :bench_ids, 'BORRADOR')
            RETURNING id
        """), {
            "titulo": titulo, "contenido": contenido,
            "bench_ids": benchmark_ids
        })
        paper_id = result.scalar()
        await session.commit()

    return {
        "id": paper_id, "titulo": titulo,
        "contenido_markdown": contenido,
        "benchmarks_usados": benchmark_ids
    }


# ─── GET /api/evidencia/papers ─────────────────────────────────
@app.get("/api/evidencia/papers", tags=["Evidencia"])
async def evidencia_papers():
    async with async_session() as session:
        rows = await session.execute(text("""
            SELECT id, titulo, fecha_generacion, version, estado, favorito,
                   benchmarks_usados, length(contenido_markdown) as chars
            FROM hgu_evidencia_papers
            ORDER BY fecha_generacion DESC
        """))
        items = []
        for r in rows:
            d = dict(r._mapping)
            if d.get("fecha_generacion"):
                d["fecha_generacion"] = str(d["fecha_generacion"])
            items.append(d)
        return items


# ─── GET /api/evidencia/papers/{id} ────────────────────────────
@app.get("/api/evidencia/papers/{paper_id}", tags=["Evidencia"])
async def evidencia_paper_detail(paper_id: int):
    async with async_session() as session:
        row = await session.execute(text(
            "SELECT * FROM hgu_evidencia_papers WHERE id = :id"
        ), {"id": paper_id})
        paper = row.mappings().first()
        if not paper:
            raise HTTPException(404, "Paper no encontrado")
        d = dict(paper)
        if d.get("fecha_generacion"):
            d["fecha_generacion"] = str(d["fecha_generacion"])
        return d


# ─── POST /api/evidencia/papers/{id}/toggle-favorito ──────────
@app.post("/api/evidencia/papers/{paper_id}/toggle-favorito", tags=["Evidencia"])
async def evidencia_paper_toggle_favorito(paper_id: int):
    async with async_session() as session:
        await session.execute(text(
            "UPDATE hgu_evidencia_papers SET favorito = NOT favorito WHERE id = :id"
        ), {"id": paper_id})
        await session.commit()
        row = await session.execute(text(
            "SELECT favorito FROM hgu_evidencia_papers WHERE id = :id"
        ), {"id": paper_id})
        return {"id": paper_id, "favorito": row.scalar()}


# ─── POST /api/evidencia/papers/{id}/set-nota ─────────────────
@app.post("/api/evidencia/papers/{paper_id}/set-nota", tags=["Evidencia"])
async def evidencia_paper_set_nota(paper_id: int, body: dict):
    nota = body.get("nota", "")
    async with async_session() as session:
        await session.execute(text(
            "UPDATE hgu_evidencia_papers SET nota_usuario = :nota WHERE id = :id"
        ), {"id": paper_id, "nota": nota})
        await session.commit()
        return {"id": paper_id, "nota_usuario": nota}


# ─── GET /api/evidencia/stats ──────────────────────────────────
@app.get("/api/evidencia/stats", tags=["Evidencia"])
async def evidencia_stats():
    async with async_session() as session:
        bench_count = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_benchmarks"
        ))
        paper_count = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_papers"
        ))
        cob = await session.execute(text(
            "SELECT COALESCE(AVG(cobertura_global), 0) FROM hgu_evidencia_benchmarks"
        ))
        pioneros = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_comparativas WHERE es_pionero = TRUE"
        ))
        gaps = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_comparativas WHERE estado_sigfar = 'NO_CONTEMPLADO'"
        ))
        total_comp = await session.execute(text(
            "SELECT count(*) FROM hgu_evidencia_comparativas"
        ))

        # Dominio con más y menos cobertura
        dom_rows = await session.execute(text("""
            SELECT dominio_sefh,
                   count(*) FILTER (WHERE estado_sigfar IN ('IMPLEMENTADO','SUPERA_ARTICULO')) as impl,
                   count(*) as total
            FROM hgu_evidencia_comparativas
            WHERE dominio_sefh IS NOT NULL
            GROUP BY dominio_sefh
        """))
        dominios_pct = {}
        for r in dom_rows:
            pct = round(r.impl / r.total * 100) if r.total else 0
            dominios_pct[r.dominio_sefh] = pct

        mejor = max(dominios_pct, key=dominios_pct.get) if dominios_pct else None
        peor = min(dominios_pct, key=dominios_pct.get) if dominios_pct else None

        return {
            "total_benchmarks": bench_count.scalar(),
            "total_papers": paper_count.scalar(),
            "cobertura_media": round(cob.scalar() or 0),
            "total_comparativas": total_comp.scalar(),
            "pioneros": pioneros.scalar(),
            "gaps": gaps.scalar(),
            "dominio_mejor": {"dominio": mejor, "pct": dominios_pct.get(mejor, 0)} if mejor else None,
            "dominio_peor": {"dominio": peor, "pct": dominios_pct.get(peor, 0)} if peor else None,
            "dominios_pct": dominios_pct
        }


# ═══════════════════════════════════════════════════════════════
# MÓDULO G: GUARDIAS — Calendario de guardias del Servicio
# 17 endpoints: farmacéuticos, calendario, intercambios,
#               equidad, ruedas, iCal, IA sugerencias, conflictos
# ═══════════════════════════════════════════════════════════════


# ─── GET /api/guardias/farmaceuticos ─────────────────────────
@app.get("/api/guardias/farmaceuticos", tags=["Guardias"])
async def guardias_farmaceuticos():
    async with async_session() as session:
        rows = await session.execute(text("""
            SELECT f.*,
                   COUNT(c.id) FILTER (WHERE c.es_localizada) AS total_loc,
                   COUNT(c.id) FILTER (WHERE c.es_presencial) AS total_pres,
                   COUNT(c.id) AS total_guardias
            FROM hgu_guardias_farmaceuticos f
            LEFT JOIN hgu_guardias_calendario c ON c.farmaceutico_id = f.id
            WHERE f.activo = TRUE
            GROUP BY f.id
            ORDER BY f.id
        """))
        return [dict(r._mapping) for r in rows]


# ─── GET /api/guardias/farmaceuticos/{id} ────────────────────
@app.get("/api/guardias/farmaceuticos/{farm_id}", tags=["Guardias"])
async def guardias_farmaceutico_detalle(farm_id: int):
    async with async_session() as session:
        farm = await session.execute(text(
            "SELECT * FROM hgu_guardias_farmaceuticos WHERE id = :id"
        ), {"id": farm_id})
        f = farm.first()
        if not f:
            raise HTTPException(404, "Farmacéutico no encontrado")
        result = dict(f._mapping)

        guardias = await session.execute(text("""
            SELECT id, fecha, dia_semana, tipo_dia, es_localizada, es_presencial, estado, notas, mes
            FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id
            ORDER BY fecha
        """), {"id": farm_id})
        result["guardias"] = [dict(r._mapping) for r in guardias]

        stats = await session.execute(text("""
            SELECT tipo_dia, COUNT(*) AS n
            FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id
            GROUP BY tipo_dia ORDER BY tipo_dia
        """), {"id": farm_id})
        result["stats_por_tipo"] = {r.tipo_dia: r.n for r in stats}

        prox = await session.execute(text("""
            SELECT fecha, tipo_dia FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id AND fecha >= CURRENT_DATE
            ORDER BY fecha LIMIT 1
        """), {"id": farm_id})
        p = prox.first()
        result["proxima_guardia"] = {"fecha": str(p.fecha), "tipo": p.tipo_dia} if p else None

        return result


# ─── GET /api/guardias/calendario ────────────────────────────
@app.get("/api/guardias/calendario", tags=["Guardias"])
async def guardias_calendario(
    mes: int = None, farmaceutico_id: int = None,
    tipo: str = None, es_localizada: bool = None, es_presencial: bool = None
):
    async with async_session() as session:
        where = ["1=1"]
        params = {}
        if mes:
            where.append("c.mes = :mes")
            params["mes"] = mes
        if farmaceutico_id:
            where.append("c.farmaceutico_id = :fid")
            params["fid"] = farmaceutico_id
        if tipo:
            where.append("c.tipo_dia = :tipo")
            params["tipo"] = tipo
        if es_localizada is not None:
            where.append("c.es_localizada = :loc")
            params["loc"] = es_localizada
        if es_presencial is not None:
            where.append("c.es_presencial = :pres")
            params["pres"] = es_presencial

        rows = await session.execute(text(f"""
            SELECT c.*, f.nombre AS farm_nombre, f.codigo AS farm_codigo, f.color_hex
            FROM hgu_guardias_calendario c
            LEFT JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE {' AND '.join(where)}
            ORDER BY c.fecha
        """), params)
        return [dict(r._mapping) for r in rows]


# ─── GET /api/guardias/calendario/mes/{anio}/{mes} ──────────
@app.get("/api/guardias/calendario/mes/{anio}/{mes}", tags=["Guardias"])
async def guardias_calendario_mes(anio: int, mes: int):
    """Vista mensual optimizada para grid 7×5: 35-42 celdas."""
    from datetime import date as dt_date
    import calendar

    first_day = dt_date(anio, mes, 1)
    # weekday(): 0=Mon..6=Sun
    start_weekday = first_day.weekday()  # 0=Lun
    days_in_month = calendar.monthrange(anio, mes)[1]

    # Calcular rango: incluir días del mes anterior/siguiente para completar grid
    start_date = first_day - timedelta(days=start_weekday)
    total_cells = 42  # 6 filas × 7 columnas
    end_date = start_date + timedelta(days=total_cells - 1)

    async with async_session() as session:
        rows = await session.execute(text("""
            SELECT c.fecha, c.dia_semana, c.tipo_dia, c.es_localizada, c.es_presencial,
                   c.estado, f.nombre AS farm_nombre, f.codigo AS farm_codigo, f.color_hex
            FROM hgu_guardias_calendario c
            LEFT JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE c.fecha BETWEEN :start AND :end
            ORDER BY c.fecha
        """), {"start": start_date, "end": end_date})

        cal_map = {}
        for r in rows:
            cal_map[str(r.fecha)] = dict(r._mapping)

    today = dt_date.today()
    celdas = []
    for i in range(total_cells):
        d = start_date + timedelta(days=i)
        ds = str(d)
        info = cal_map.get(ds, {})
        celdas.append({
            "fecha": ds,
            "dia_del_mes": d.day,
            "dia_semana": info.get("dia_semana", ["L","M","X","J","V","S","D"][d.weekday()]),
            "es_mes_actual": d.month == mes,
            "es_hoy": d == today,
            "es_weekend": d.weekday() >= 5,
            "tipo_dia": info.get("tipo_dia"),
            "es_localizada": info.get("es_localizada"),
            "es_presencial": info.get("es_presencial"),
            "estado": info.get("estado"),
            "farm_nombre": info.get("farm_nombre"),
            "farm_codigo": info.get("farm_codigo"),
            "color_hex": info.get("color_hex"),
        })

    return {"anio": anio, "mes": mes, "celdas": celdas}


# ─── GET /api/guardias/calendario/hoy ────────────────────────
@app.get("/api/guardias/calendario/hoy", tags=["Guardias"])
async def guardias_hoy():
    async with async_session() as session:
        row = await session.execute(text("""
            SELECT c.*, f.nombre AS farm_nombre, f.codigo AS farm_codigo, f.color_hex
            FROM hgu_guardias_calendario c
            LEFT JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE c.fecha = CURRENT_DATE
        """))
        r = row.first()
        if not r:
            return {"mensaje": "No hay guardia asignada para hoy"}
        return dict(r._mapping)


# ─── GET /api/guardias/stats ─────────────────────────────────
@app.get("/api/guardias/stats", tags=["Guardias"])
async def guardias_stats():
    async with async_session() as session:
        total = await session.execute(text(
            "SELECT COUNT(*) FROM hgu_guardias_calendario WHERE farmaceutico_id IS NOT NULL"
        ))
        por_tipo = await session.execute(text("""
            SELECT tipo_dia, COUNT(*) AS n FROM hgu_guardias_calendario
            GROUP BY tipo_dia ORDER BY tipo_dia
        """))
        adjuntos = await session.execute(text("""
            SELECT f.codigo,
                   COUNT(c.id) FILTER (WHERE c.es_localizada) AS loc,
                   COUNT(c.id) FILTER (WHERE c.es_presencial) AS pres,
                   COUNT(c.id) AS total
            FROM hgu_guardias_farmaceuticos f
            JOIN hgu_guardias_calendario c ON c.farmaceutico_id = f.id
            WHERE f.rol = 'ADJUNTO'
            GROUP BY f.id, f.codigo
        """))
        adj_list = [dict(r._mapping) for r in adjuntos]
        totals = [a["total"] for a in adj_list]
        media = round(sum(totals) / len(totals), 1) if totals else 0
        desv_max = max(abs(t - media) for t in totals) if totals else 0

        ruedas = await session.execute(text("SELECT * FROM hgu_guardias_ruedas ORDER BY id"))
        ruedas_info = []
        for r in ruedas:
            seq = r.secuencia if isinstance(r.secuencia, list) else json.loads(r.secuencia) if isinstance(r.secuencia, str) else r.secuencia
            siguiente = seq[(r.orden_actual - 1) % len(seq)] if seq else None
            ruedas_info.append({
                "tipo": r.tipo_rueda, "orden_actual": r.orden_actual,
                "siguiente": siguiente
            })

        return {
            "total_asignadas": total.scalar(),
            "por_tipo": {r.tipo_dia: r.n for r in por_tipo},
            "media_por_adjunto": media,
            "desviacion_maxima": round(desv_max, 1),
            "ruedas": ruedas_info
        }


# ─── GET /api/guardias/stats/{farmaceutico_id} ──────────────
@app.get("/api/guardias/stats/{farm_id}", tags=["Guardias"])
async def guardias_stats_personal(farm_id: int):
    async with async_session() as session:
        farm = await session.execute(text(
            "SELECT nombre, codigo FROM hgu_guardias_farmaceuticos WHERE id = :id"
        ), {"id": farm_id})
        f = farm.first()
        if not f:
            raise HTTPException(404, "Farmacéutico no encontrado")

        por_tipo = await session.execute(text("""
            SELECT tipo_dia, COUNT(*) AS n FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id GROUP BY tipo_dia ORDER BY tipo_dia
        """), {"id": farm_id})
        tipos = {r.tipo_dia: r.n for r in por_tipo}

        total_loc = sum(v for k, v in tipos.items() if k.startswith("L"))
        total_pres = sum(v for k, v in tipos.items() if k.startswith("P"))

        prox = await session.execute(text("""
            SELECT fecha, tipo_dia FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id AND fecha >= CURRENT_DATE
            ORDER BY fecha LIMIT 1
        """), {"id": farm_id})
        p = prox.first()

        # Cuota media adjuntos
        media = await session.execute(text("""
            SELECT AVG(cnt) FROM (
                SELECT COUNT(*) AS cnt FROM hgu_guardias_calendario c
                JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
                WHERE f.rol = 'ADJUNTO'
                GROUP BY f.id
            ) sub
        """))
        cuota = round(media.scalar() or 0, 1)

        return {
            "farmaceutico": f.nombre, "codigo": f.codigo,
            "por_tipo": tipos,
            "total_localizadas": total_loc, "total_presenciales": total_pres,
            "total": total_loc + total_pres,
            "cuota_media_adjunto": cuota,
            "diferencia_cuota": round((total_loc + total_pres) - cuota, 1),
            "proxima_guardia": {"fecha": str(p.fecha), "tipo": p.tipo_dia} if p else None
        }


# ─── GET /api/guardias/equidad ───────────────────────────────
@app.get("/api/guardias/equidad", tags=["Guardias"])
async def guardias_equidad():
    async with async_session() as session:
        rows = await session.execute(text("""
            SELECT f.id, f.nombre, f.codigo, f.rol,
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LN') AS "LN",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LJ') AS "LJ",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LV') AS "LV",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LS') AS "LS",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LD') AS "LD",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LF') AS "LF",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'LFE') AS "LFE",
                   COUNT(c.id) FILTER (WHERE c.es_localizada) AS total_loc,
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'PN') AS "PN",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'PJ') AS "PJ",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'PV') AS "PV",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'PS') AS "PS",
                   COUNT(c.id) FILTER (WHERE c.tipo_dia = 'PF') AS "PF",
                   COUNT(c.id) FILTER (WHERE c.es_presencial) AS total_pres,
                   COUNT(c.id) AS total
            FROM hgu_guardias_farmaceuticos f
            LEFT JOIN hgu_guardias_calendario c ON c.farmaceutico_id = f.id
            WHERE f.activo = TRUE
            GROUP BY f.id ORDER BY f.id
        """))
        data = [dict(r._mapping) for r in rows]

        # Calcular cuota media solo de adjuntos
        adj = [d for d in data if d["rol"] == "ADJUNTO"]
        if adj:
            media_loc = round(sum(d["total_loc"] for d in adj) / len(adj), 1)
            media_pres = round(sum(d["total_pres"] for d in adj) / len(adj), 1)
        else:
            media_loc = media_pres = 0

        for d in data:
            if d["rol"] == "ADJUNTO":
                d["desviacion_loc"] = round(d["total_loc"] - media_loc, 1)
                d["desviacion_pres"] = round(d["total_pres"] - media_pres, 1)
            else:
                d["desviacion_loc"] = None
                d["desviacion_pres"] = None

        return {
            "farmaceuticos": data,
            "cuota_media_loc": media_loc,
            "cuota_media_pres": media_pres
        }


# ─── POST /api/guardias/intercambios ────────────────────────
@app.post("/api/guardias/intercambios", tags=["Guardias"])
async def guardias_crear_intercambio(body: dict):
    sol_id = body.get("solicitante_id")
    rec_id = body.get("receptor_id")
    ofr_id = body.get("guardia_ofrecida_id")
    ped_id = body.get("guardia_pedida_id")
    motivo = body.get("motivo", "")
    dry_run = body.get("dry_run", False)

    if not all([sol_id, rec_id, ofr_id, ped_id]):
        raise HTTPException(400, "solicitante_id, receptor_id, guardia_ofrecida_id, guardia_pedida_id son obligatorios")

    async with async_session() as session:
        # Obtener guardias
        g_ofr = await session.execute(text(
            "SELECT * FROM hgu_guardias_calendario WHERE id = :id"), {"id": ofr_id})
        g_ped = await session.execute(text(
            "SELECT * FROM hgu_guardias_calendario WHERE id = :id"), {"id": ped_id})
        ofrecida = g_ofr.first()
        pedida = g_ped.first()
        if not ofrecida or not pedida:
            raise HTTPException(404, "Guardia no encontrada")

        # Obtener farmacéuticos
        f_sol = await session.execute(text(
            "SELECT * FROM hgu_guardias_farmaceuticos WHERE id = :id"), {"id": sol_id})
        f_rec = await session.execute(text(
            "SELECT * FROM hgu_guardias_farmaceuticos WHERE id = :id"), {"id": rec_id})
        solicitante = f_sol.first()
        receptor = f_rec.first()
        if not solicitante or not receptor:
            raise HTTPException(404, "Farmacéutico no encontrado")

        # Validar las 10 reglas
        reglas_rows = await session.execute(text(
            "SELECT * FROM hgu_guardias_reglas WHERE activa = TRUE ORDER BY numero"))
        reglas = [dict(r._mapping) for r in reglas_rows]

        validacion = []
        cumple_hard = True
        for regla in reglas:
            num = regla["numero"]
            sev = regla["severidad"]
            cumple = True
            mensaje = "OK"

            if num == 3:
                # PBS doble GL, 0 presenciales
                if receptor.codigo == "PBS" and pedida.es_presencial:
                    cumple = False
                    mensaje = "PBS no puede asumir guardias presenciales"
                if solicitante.codigo == "PBS" and ofrecida.es_presencial:
                    cumple = False
                    mensaje = "PBS no puede asumir guardias presenciales"

            elif num == 6:
                # 1-3 guardias/mes por adjunto
                for fid, fname in [(rec_id, receptor.nombre), (sol_id, solicitante.nombre)]:
                    cnt = await session.execute(text("""
                        SELECT COUNT(*) FROM hgu_guardias_calendario
                        WHERE farmaceutico_id = :fid AND mes = :mes
                    """), {"fid": fid, "mes": ofrecida.mes})
                    c = cnt.scalar()
                    if c > 3:
                        cumple = False
                        mensaje = f"{fname} ya tiene {c} guardias en ese mes (máx 3)"

            elif num == 9:
                # Navidad excluyente
                sol_fechas = await session.execute(text("""
                    SELECT fecha FROM hgu_guardias_calendario
                    WHERE farmaceutico_id = :id AND fecha IN ('2026-12-24','2026-12-25','2026-12-31','2027-01-01')
                """), {"id": sol_id})
                sf = [str(r.fecha) for r in sol_fechas]
                nav = any("12-24" in f or "12-25" in f for f in sf)
                nye = any("12-31" in f or "01-01" in f for f in sf)
                if nav and nye:
                    cumple = False
                    mensaje = "No puede tener Navidad Y Año Nuevo"

            elif num == 7:
                # Evitar GPF+GL consecutivas
                for fid in [sol_id, rec_id]:
                    consec = await session.execute(text("""
                        SELECT fecha, es_localizada, es_presencial
                        FROM hgu_guardias_calendario
                        WHERE farmaceutico_id = :fid
                        ORDER BY fecha
                    """), {"fid": fid})
                    prev = None
                    for r in consec:
                        if prev and (r.fecha - prev.fecha).days == 1:
                            if prev.es_presencial and r.es_localizada:
                                cumple = False
                                mensaje = "Guardia presencial seguida de localizada detectada"
                        prev = r

            if not cumple and sev == "HARD":
                cumple_hard = False

            validacion.append({
                "regla_num": num,
                "descripcion": regla["descripcion"],
                "severidad": sev,
                "cumple": cumple,
                "mensaje": mensaje
            })

        cumple_todas = all(v["cumple"] for v in validacion)

        if dry_run:
            return {
                "dry_run": True,
                "cumple_reglas": cumple_hard,
                "cumple_todas": cumple_todas,
                "validacion_reglas": validacion
            }

        # Crear intercambio
        result = await session.execute(text("""
            INSERT INTO hgu_guardias_intercambios
                (solicitante_id, receptor_id, guardia_ofrecida_id, guardia_pedida_id,
                 motivo, validacion_reglas, cumple_reglas)
            VALUES (:sol, :rec, :ofr, :ped, :mot, :val, :cumple)
            RETURNING id
        """), {
            "sol": sol_id, "rec": rec_id, "ofr": ofr_id, "ped": ped_id,
            "mot": motivo,
            "val": json.dumps(validacion),
            "cumple": cumple_hard
        })
        await session.commit()
        new_id = result.scalar()

        return {
            "id": new_id,
            "cumple_reglas": cumple_hard,
            "cumple_todas": cumple_todas,
            "validacion_reglas": validacion
        }


# ─── GET /api/guardias/intercambios ──────────────────────────
@app.get("/api/guardias/intercambios", tags=["Guardias"])
async def guardias_listar_intercambios(estado: str = None, farmaceutico_id: int = None):
    async with async_session() as session:
        where = ["1=1"]
        params = {}
        if estado:
            where.append("i.estado = :estado")
            params["estado"] = estado
        if farmaceutico_id:
            where.append("(i.solicitante_id = :fid OR i.receptor_id = :fid)")
            params["fid"] = farmaceutico_id

        rows = await session.execute(text(f"""
            SELECT i.*,
                   fs.nombre AS solicitante_nombre, fs.codigo AS solicitante_codigo,
                   fr.nombre AS receptor_nombre, fr.codigo AS receptor_codigo,
                   go.fecha AS fecha_ofrecida, go.tipo_dia AS tipo_ofrecida,
                   gp.fecha AS fecha_pedida, gp.tipo_dia AS tipo_pedida
            FROM hgu_guardias_intercambios i
            LEFT JOIN hgu_guardias_farmaceuticos fs ON fs.id = i.solicitante_id
            LEFT JOIN hgu_guardias_farmaceuticos fr ON fr.id = i.receptor_id
            LEFT JOIN hgu_guardias_calendario go ON go.id = i.guardia_ofrecida_id
            LEFT JOIN hgu_guardias_calendario gp ON gp.id = i.guardia_pedida_id
            WHERE {' AND '.join(where)}
            ORDER BY i.fecha_solicitud DESC
        """), params)
        return [dict(r._mapping) for r in rows]


# ─── POST /api/guardias/intercambios/{id}/aceptar ───────────
@app.post("/api/guardias/intercambios/{int_id}/aceptar", tags=["Guardias"])
async def guardias_aceptar_intercambio(int_id: int):
    async with async_session() as session:
        row = await session.execute(text(
            "SELECT * FROM hgu_guardias_intercambios WHERE id = :id"), {"id": int_id})
        inter = row.first()
        if not inter:
            raise HTTPException(404, "Intercambio no encontrado")
        if inter.estado != "PENDIENTE":
            raise HTTPException(400, f"Intercambio en estado {inter.estado}, no se puede aceptar")

        if inter.cumple_reglas:
            # Ejecutar swap
            await session.execute(text("""
                UPDATE hgu_guardias_calendario SET farmaceutico_id = :rec
                WHERE id = :ofr
            """), {"rec": inter.receptor_id, "ofr": inter.guardia_ofrecida_id})
            await session.execute(text("""
                UPDATE hgu_guardias_calendario SET farmaceutico_id = :sol
                WHERE id = :ped
            """), {"sol": inter.solicitante_id, "ped": inter.guardia_pedida_id})
            await session.execute(text("""
                UPDATE hgu_guardias_calendario SET estado = 'INTERCAMBIADA'
                WHERE id IN (:ofr, :ped)
            """), {"ofr": inter.guardia_ofrecida_id, "ped": inter.guardia_pedida_id})
            await session.execute(text("""
                UPDATE hgu_guardias_intercambios
                SET estado = 'ACEPTADA', fecha_respuesta = NOW()
                WHERE id = :id
            """), {"id": int_id})
        else:
            # Reglas HARD violadas: se marca como ACEPTADA pero necesita validación jefa
            await session.execute(text("""
                UPDATE hgu_guardias_intercambios
                SET estado = 'ACEPTADA', fecha_respuesta = NOW()
                WHERE id = :id
            """), {"id": int_id})

        await session.commit()
        return {"ok": True, "estado": "ACEPTADA", "swap_ejecutado": inter.cumple_reglas}


# ─── POST /api/guardias/intercambios/{id}/rechazar ──────────
@app.post("/api/guardias/intercambios/{int_id}/rechazar", tags=["Guardias"])
async def guardias_rechazar_intercambio(int_id: int):
    async with async_session() as session:
        await session.execute(text("""
            UPDATE hgu_guardias_intercambios
            SET estado = 'RECHAZADA', fecha_respuesta = NOW()
            WHERE id = :id AND estado = 'PENDIENTE'
        """), {"id": int_id})
        await session.commit()
        return {"ok": True, "estado": "RECHAZADA"}


# ─── POST /api/guardias/intercambios/{id}/validar ───────────
@app.post("/api/guardias/intercambios/{int_id}/validar", tags=["Guardias"])
async def guardias_validar_intercambio(int_id: int):
    """La jefa valida un intercambio con reglas SOFT violadas."""
    async with async_session() as session:
        row = await session.execute(text(
            "SELECT * FROM hgu_guardias_intercambios WHERE id = :id"), {"id": int_id})
        inter = row.first()
        if not inter:
            raise HTTPException(404, "Intercambio no encontrado")
        if inter.estado != "ACEPTADA":
            raise HTTPException(400, "Solo se pueden validar intercambios ACEPTADOS")

        # Ejecutar swap si aún no se hizo
        await session.execute(text("""
            UPDATE hgu_guardias_calendario SET farmaceutico_id = :rec
            WHERE id = :ofr
        """), {"rec": inter.receptor_id, "ofr": inter.guardia_ofrecida_id})
        await session.execute(text("""
            UPDATE hgu_guardias_calendario SET farmaceutico_id = :sol
            WHERE id = :ped
        """), {"sol": inter.solicitante_id, "ped": inter.guardia_pedida_id})
        await session.execute(text("""
            UPDATE hgu_guardias_calendario SET estado = 'INTERCAMBIADA'
            WHERE id IN (:ofr, :ped)
        """), {"ofr": inter.guardia_ofrecida_id, "ped": inter.guardia_pedida_id})
        await session.execute(text("""
            UPDATE hgu_guardias_intercambios
            SET estado = 'VALIDADA_JEFA'
            WHERE id = :id
        """), {"id": int_id})
        await session.commit()
        return {"ok": True, "estado": "VALIDADA_JEFA"}


# ─── GET /api/guardias/ruedas ────────────────────────────────
@app.get("/api/guardias/ruedas", tags=["Guardias"])
async def guardias_ruedas():
    async with async_session() as session:
        rows = await session.execute(text("SELECT * FROM hgu_guardias_ruedas ORDER BY id"))
        result = []
        for r in rows:
            seq = r.secuencia if isinstance(r.secuencia, list) else json.loads(r.secuencia) if isinstance(r.secuencia, str) else r.secuencia
            idx = (r.orden_actual - 1) % len(seq) if seq else 0
            result.append({
                "id": r.id,
                "tipo_rueda": r.tipo_rueda,
                "orden_actual": r.orden_actual,
                "secuencia": seq,
                "siguiente": seq[idx] if seq else None
            })
        return result


# ─── GET /api/guardias/exportar-ical/{farmaceutico_id} ──────
@app.get("/api/guardias/exportar-ical/{farm_id}", tags=["Guardias"])
async def guardias_exportar_ical(farm_id: int):
    tipo_emoji = {
        "LN": "🌙", "LJ": "🌙", "LV": "🌙", "LS": "🌙", "LD": "🌙", "LF": "🌙", "LFE": "⭐",
        "PN": "🏥", "PJ": "🏥", "PV": "🏥", "PS": "🏥", "PF": "🏥", "PFE": "⭐🏥"
    }
    async with async_session() as session:
        farm = await session.execute(text(
            "SELECT nombre, codigo FROM hgu_guardias_farmaceuticos WHERE id = :id"), {"id": farm_id})
        f = farm.first()
        if not f:
            raise HTTPException(404, "Farmacéutico no encontrado")

        rows = await session.execute(text("""
            SELECT fecha, tipo_dia, es_localizada FROM hgu_guardias_calendario
            WHERE farmaceutico_id = :id ORDER BY fecha
        """), {"id": farm_id})

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SIGFAR Hub//Guardias//ES",
            f"X-WR-CALNAME:Guardias {f.nombre}",
        ]
        for r in rows:
            emoji = tipo_emoji.get(r.tipo_dia, "")
            cat = "Localizada" if r.es_localizada else "Presencial"
            fecha_str = r.fecha.strftime("%Y%m%d")
            lines.extend([
                "BEGIN:VEVENT",
                f"DTSTART;VALUE=DATE:{fecha_str}",
                f"DTEND;VALUE=DATE:{fecha_str}",
                f"SUMMARY:{emoji} {r.tipo_dia} — Guardia {cat}",
                f"DESCRIPTION:Guardia {cat} tipo {r.tipo_dia} — {f.nombre}",
                f"UID:sigfar-guardia-{r.fecha}-{f.codigo}@sigfar-hub",
                "END:VEVENT",
            ])
        lines.append("END:VCALENDAR")

        ical_content = "\r\n".join(lines)
        return Response(
            content=ical_content,
            media_type="text/calendar",
            headers={"Content-Disposition": f'attachment; filename="guardias_{f.codigo}.ics"'}
        )


# ─── POST /api/guardias/ia/sugerir-intercambio ──────────────
@app.post("/api/guardias/ia/sugerir-intercambio", tags=["Guardias"])
async def guardias_ia_sugerir():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-placeholder":
        raise HTTPException(400, "OPENAI_API_KEY no configurada")

    async with async_session() as session:
        # Obtener equidad actual
        eq_rows = await session.execute(text("""
            SELECT f.codigo, f.rol,
                   COUNT(c.id) FILTER (WHERE c.es_localizada) AS loc,
                   COUNT(c.id) FILTER (WHERE c.es_presencial) AS pres,
                   COUNT(c.id) AS total
            FROM hgu_guardias_farmaceuticos f
            JOIN hgu_guardias_calendario c ON c.farmaceutico_id = f.id
            WHERE f.activo = TRUE AND f.rol IN ('ADJUNTO','JEFA')
            GROUP BY f.id, f.codigo, f.rol ORDER BY f.id
        """))
        equidad = [dict(r._mapping) for r in eq_rows]

        # Obtener reglas
        reglas_rows = await session.execute(text(
            "SELECT numero, descripcion, severidad FROM hgu_guardias_reglas WHERE activa = TRUE ORDER BY numero"))
        reglas = [dict(r._mapping) for r in reglas_rows]

        # Próximas guardias (30 días)
        prox = await session.execute(text("""
            SELECT c.fecha, c.tipo_dia, f.codigo AS farm_codigo
            FROM hgu_guardias_calendario c
            JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE c.fecha BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
            ORDER BY c.fecha
        """))
        proximas = [dict(r._mapping) for r in prox]

    prompt_sistema = f"""Eres un planificador de guardias farmacéuticas hospitalarias.
{SIGFAR_CONTEXT_PROMPT}

Te doy la tabla de equidad actual, las 10 reglas del decálogo y las guardias de los próximos 30 días.
Sugiere hasta 5 intercambios concretos para MEJORAR la equidad sin violar reglas HARD.

Para cada sugerencia devuelve JSON:
[
  {{
    "guardia_a": {{"fecha": "YYYY-MM-DD", "tipo": "XX", "farmaceutico": "CODIGO"}},
    "guardia_b": {{"fecha": "YYYY-MM-DD", "tipo": "XX", "farmaceutico": "CODIGO"}},
    "motivo": "explicación breve",
    "mejora_equidad": "qué mejora concretamente"
  }}
]
Responde SOLO con el JSON array, sin markdown."""

    prompt_user = f"""EQUIDAD ACTUAL:
{json.dumps(equidad, ensure_ascii=False)}

REGLAS DEL DECÁLOGO:
{json.dumps(reglas, ensure_ascii=False)}

PRÓXIMAS 30 DÍAS:
{json.dumps(proximas, default=str, ensure_ascii=False)}"""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.4,
                "max_tokens": 2000,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_user}
                ]
            }
        )
    if resp.status_code != 200:
        raise HTTPException(502, f"Error Groq: {resp.status_code} — {resp.text[:300]}")

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```$", "", raw)

    try:
        sugerencias = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(502, f"Groq devolvió JSON inválido: {raw[:500]}")

    return {"sugerencias": sugerencias}


# ─── GET /api/guardias/conflictos ────────────────────────────
@app.get("/api/guardias/conflictos", tags=["Guardias"])
async def guardias_conflictos():
    """Escanea la planilla y detecta violaciones actuales de las 10 reglas."""
    async with async_session() as session:
        conflictos = []

        # Regla 3: PBS sin presenciales
        pbs_pres = await session.execute(text("""
            SELECT c.fecha, c.tipo_dia FROM hgu_guardias_calendario c
            JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE f.codigo = 'PBS' AND c.es_presencial = TRUE
        """))
        for r in pbs_pres:
            conflictos.append({
                "regla": 3, "severidad": "HARD",
                "descripcion": "PBS tiene guardia presencial asignada",
                "farmaceutico": "PBS", "fecha": str(r.fecha), "detalle": r.tipo_dia
            })

        # Regla 6: Adjuntos con >3 guardias en un mes
        sobrecarga = await session.execute(text("""
            SELECT f.codigo, c.mes, COUNT(*) AS cnt
            FROM hgu_guardias_calendario c
            JOIN hgu_guardias_farmaceuticos f ON f.id = c.farmaceutico_id
            WHERE f.rol = 'ADJUNTO'
            GROUP BY f.codigo, c.mes
            HAVING COUNT(*) > 3
        """))
        for r in sobrecarga:
            conflictos.append({
                "regla": 6, "severidad": "HARD",
                "descripcion": f"{r.codigo} tiene {r.cnt} guardias en mes {r.mes} (máx 3)",
                "farmaceutico": r.codigo, "fecha": f"Mes {r.mes}", "detalle": f"{r.cnt} guardias"
            })

        # Regla 6b: Adjuntos con 0 guardias en un mes
        infracarga = await session.execute(text("""
            SELECT f.codigo, m.mes
            FROM hgu_guardias_farmaceuticos f
            CROSS JOIN generate_series(1,12) AS m(mes)
            LEFT JOIN hgu_guardias_calendario c ON c.farmaceutico_id = f.id AND c.mes = m.mes
            WHERE f.rol = 'ADJUNTO' AND f.activo = TRUE
            GROUP BY f.codigo, m.mes
            HAVING COUNT(c.id) = 0
        """))
        for r in infracarga:
            conflictos.append({
                "regla": 6, "severidad": "HARD",
                "descripcion": f"{r.codigo} tiene 0 guardias en mes {r.mes} (mín 1)",
                "farmaceutico": r.codigo, "fecha": f"Mes {r.mes}", "detalle": "0 guardias"
            })

        # Regla 7: GPF+GL consecutivas
        consec = await session.execute(text("""
            SELECT f.codigo, c1.fecha AS f1, c1.tipo_dia AS t1, c2.fecha AS f2, c2.tipo_dia AS t2
            FROM hgu_guardias_calendario c1
            JOIN hgu_guardias_calendario c2 ON c2.farmaceutico_id = c1.farmaceutico_id
                 AND c2.fecha = c1.fecha + 1
            JOIN hgu_guardias_farmaceuticos f ON f.id = c1.farmaceutico_id
            WHERE c1.es_presencial = TRUE AND c2.es_localizada = TRUE
        """))
        for r in consec:
            conflictos.append({
                "regla": 7, "severidad": "SOFT",
                "descripcion": f"{r.codigo}: presencial {r.t1} ({r.f1}) + localizada {r.t2} ({r.f2}) consecutivas",
                "farmaceutico": r.codigo, "fecha": str(r.f1),
                "detalle": f"{r.t1} → {r.t2}"
            })

        # Regla 9: Navidad + Año Nuevo mismo farmacéutico
        navidad_anio = await session.execute(text("""
            SELECT f.codigo
            FROM hgu_guardias_farmaceuticos f
            WHERE EXISTS (
                SELECT 1 FROM hgu_guardias_calendario c
                WHERE c.farmaceutico_id = f.id AND c.fecha IN ('2026-12-24','2026-12-25')
            ) AND EXISTS (
                SELECT 1 FROM hgu_guardias_calendario c
                WHERE c.farmaceutico_id = f.id AND c.fecha IN ('2026-12-31')
            )
        """))
        for r in navidad_anio:
            conflictos.append({
                "regla": 9, "severidad": "HARD",
                "descripcion": f"{r.codigo} tiene Navidad Y Año Nuevo",
                "farmaceutico": r.codigo, "fecha": "Dic 2026",
                "detalle": "Navidad excluyente"
            })

        return {
            "total_conflictos": len(conflictos),
            "hard": len([c for c in conflictos if c["severidad"] == "HARD"]),
            "soft": len([c for c in conflictos if c["severidad"] == "SOFT"]),
            "conflictos": conflictos
        }


# ═══════════════════════════════════════════════════════════════
# MÓDULO H: HERRAMIENTAS IA — 10 endpoints
# ═══════════════════════════════════════════════════════════════

# ── H1. Listar herramientas (con filtros opcionales) ─────────
@app.get("/api/herramientas")
async def listar_herramientas(categoria: str = None, nivel: str = None, buscar: str = None):
    async with async_session() as s:
        where = []
        if categoria:
            where.append(f"categoria = '{categoria}'")
        if nivel:
            where.append(f"nivel_dificultad = '{nivel}'")
        if buscar:
            safe = buscar.replace("'", "''")
            where.append(f"(LOWER(nombre) LIKE LOWER('%{safe}%') OR LOWER(descripcion_corta) LIKE LOWER('%{safe}%') OR tags::text ILIKE '%{safe}%')")
        clause = " AND ".join(where) if where else "TRUE"
        rows = (await s.execute(text(f"""
            SELECT id, nombre, url, logo_emoji, descripcion_corta, categoria, empresa,
                   plan_gratuito, nivel_dificultad, privacidad, requiere_cuenta, tags,
                   favorito, valoracion, orden
            FROM hgu_herramientas_ia
            WHERE {clause}
            ORDER BY categoria, orden, nombre
        """))).fetchall()
        return [{
            "id": r.id, "nombre": r.nombre, "url": r.url, "logo_emoji": r.logo_emoji,
            "descripcion_corta": r.descripcion_corta, "categoria": r.categoria,
            "empresa": r.empresa, "plan_gratuito": r.plan_gratuito,
            "nivel_dificultad": r.nivel_dificultad, "privacidad": r.privacidad,
            "requiere_cuenta": r.requiere_cuenta, "tags": r.tags,
            "favorito": r.favorito, "valoracion": r.valoracion, "orden": r.orden
        } for r in rows]


# ── H2. Detalle de una herramienta ───────────────────────────
@app.get("/api/herramientas/{hid}")
async def detalle_herramienta(hid: int):
    async with async_session() as s:
        r = (await s.execute(text(
            "SELECT * FROM hgu_herramientas_ia WHERE id = :id"
        ), {"id": hid})).fetchone()
        if not r:
            raise HTTPException(404, "Herramienta no encontrada")
        return {
            "id": r.id, "nombre": r.nombre, "url": r.url, "logo_emoji": r.logo_emoji,
            "descripcion_corta": r.descripcion_corta, "descripcion_larga": r.descripcion_larga,
            "categoria": r.categoria, "empresa": r.empresa,
            "plan_gratuito": r.plan_gratuito, "plan_pago": r.plan_pago,
            "ventajas": r.ventajas, "inconvenientes": r.inconvenientes,
            "casos_uso_fh": r.casos_uso_fh,
            "nivel_dificultad": r.nivel_dificultad, "privacidad": r.privacidad,
            "requiere_cuenta": r.requiere_cuenta, "tags": r.tags,
            "favorito": r.favorito, "nota_usuario": r.nota_usuario,
            "valoracion": r.valoracion, "orden": r.orden,
            "created_at": str(r.created_at) if r.created_at else None
        }


# ── H3. Categorías con conteo ────────────────────────────────
@app.get("/api/herramientas/meta/categorias")
async def categorias_herramientas():
    async with async_session() as s:
        rows = (await s.execute(text("""
            SELECT categoria, COUNT(*) as total,
                   COUNT(*) FILTER (WHERE favorito) as favoritas
            FROM hgu_herramientas_ia
            GROUP BY categoria
            ORDER BY total DESC
        """))).fetchall()
        LABELS = {
            "LLM_GENERALISTA": "LLM Generalistas",
            "BUSQUEDA_CIENTIFICA": "Búsqueda Científica",
            "GESTION_DOCUMENTAL": "Gestión Documental",
            "PRESENTACIONES": "Presentaciones",
            "ESCRITURA": "Escritura",
            "DESARROLLO": "Desarrollo",
            "IMAGEN_MULTIMEDIA": "Imagen y Multimedia",
            "SALUD_FARMA": "Salud y Farmacia"
        }
        return [{
            "categoria": r.categoria,
            "label": LABELS.get(r.categoria, r.categoria),
            "total": r.total,
            "favoritas": r.favoritas
        } for r in rows]


# ── H4. Toggle favorito ──────────────────────────────────────
@app.post("/api/herramientas/{hid}/toggle-favorito")
async def toggle_favorito_herramienta(hid: int):
    async with async_session() as s:
        r = (await s.execute(text(
            "UPDATE hgu_herramientas_ia SET favorito = NOT favorito WHERE id = :id RETURNING id, nombre, favorito"
        ), {"id": hid})).fetchone()
        await s.commit()
        if not r:
            raise HTTPException(404, "Herramienta no encontrada")
        return {"id": r.id, "nombre": r.nombre, "favorito": r.favorito}


# ── H5. Guardar nota de usuario ──────────────────────────────
@app.post("/api/herramientas/{hid}/nota")
async def set_nota_herramienta(hid: int, body: dict):
    nota = body.get("nota", "")
    async with async_session() as s:
        r = (await s.execute(text(
            "UPDATE hgu_herramientas_ia SET nota_usuario = :nota WHERE id = :id RETURNING id, nombre"
        ), {"id": hid, "nota": nota})).fetchone()
        await s.commit()
        if not r:
            raise HTTPException(404, "Herramienta no encontrada")
        return {"id": r.id, "nombre": r.nombre, "nota": nota}


# ── H6. Guardar valoración ───────────────────────────────────
@app.post("/api/herramientas/{hid}/valoracion")
async def set_valoracion_herramienta(hid: int, body: dict):
    val = body.get("valoracion")
    if not val or not (1 <= int(val) <= 5):
        raise HTTPException(400, "Valoración debe ser 1-5")
    async with async_session() as s:
        r = (await s.execute(text(
            "UPDATE hgu_herramientas_ia SET valoracion = :val WHERE id = :id RETURNING id, nombre, valoracion"
        ), {"id": hid, "val": int(val)})).fetchone()
        await s.commit()
        if not r:
            raise HTTPException(404, "Herramienta no encontrada")
        return {"id": r.id, "nombre": r.nombre, "valoracion": r.valoracion}


# ── H7. Listar favoritas ─────────────────────────────────────
@app.get("/api/herramientas/mis/favoritos")
async def favoritos_herramientas():
    async with async_session() as s:
        rows = (await s.execute(text("""
            SELECT id, nombre, url, logo_emoji, descripcion_corta, categoria, empresa,
                   nivel_dificultad, privacidad, tags, favorito, valoracion, nota_usuario
            FROM hgu_herramientas_ia
            WHERE favorito = TRUE
            ORDER BY categoria, nombre
        """))).fetchall()
        return [{
            "id": r.id, "nombre": r.nombre, "url": r.url, "logo_emoji": r.logo_emoji,
            "descripcion_corta": r.descripcion_corta, "categoria": r.categoria,
            "empresa": r.empresa, "nivel_dificultad": r.nivel_dificultad,
            "privacidad": r.privacidad, "tags": r.tags,
            "favorito": r.favorito, "valoracion": r.valoracion,
            "nota_usuario": r.nota_usuario
        } for r in rows]


# ── H8. Estadísticas generales ────────────────────────────────
@app.get("/api/herramientas/meta/stats")
async def stats_herramientas():
    async with async_session() as s:
        totals = (await s.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE favorito) as favoritas,
                COUNT(*) FILTER (WHERE valoracion IS NOT NULL) as valoradas,
                ROUND(AVG(valoracion) FILTER (WHERE valoracion IS NOT NULL), 1) as media_valoracion,
                COUNT(DISTINCT categoria) as categorias,
                COUNT(*) FILTER (WHERE plan_gratuito IS NOT NULL AND plan_gratuito != '') as con_plan_gratuito,
                COUNT(*) FILTER (WHERE nivel_dificultad = 'FACIL') as facil,
                COUNT(*) FILTER (WHERE nivel_dificultad = 'MEDIO') as medio,
                COUNT(*) FILTER (WHERE nivel_dificultad = 'AVANZADO') as avanzado,
                COUNT(*) FILTER (WHERE privacidad = 'LOCAL') as privacidad_local
            FROM hgu_herramientas_ia
        """))).fetchone()
        top = (await s.execute(text("""
            SELECT nombre, logo_emoji, valoracion, categoria
            FROM hgu_herramientas_ia
            WHERE valoracion IS NOT NULL
            ORDER BY valoracion DESC, nombre
            LIMIT 5
        """))).fetchall()
        return {
            "total": totals.total,
            "favoritas": totals.favoritas,
            "valoradas": totals.valoradas,
            "media_valoracion": float(totals.media_valoracion) if totals.media_valoracion else None,
            "categorias": totals.categorias,
            "con_plan_gratuito": totals.con_plan_gratuito,
            "por_nivel": {"facil": totals.facil, "medio": totals.medio, "avanzado": totals.avanzado},
            "privacidad_local": totals.privacidad_local,
            "top_valoradas": [{"nombre": t.nombre, "logo_emoji": t.logo_emoji,
                               "valoracion": t.valoracion, "categoria": t.categoria} for t in top]
        }


# ── H9. IA — Recomendar herramientas ─────────────────────────
@app.post("/api/herramientas/ia/recomendar")
async def ia_recomendar_herramienta(body: dict):
    necesidad = body.get("necesidad", "")
    if not necesidad:
        raise HTTPException(400, "Describe tu necesidad")
    async with async_session() as s:
        rows = (await s.execute(text("""
            SELECT nombre, categoria, descripcion_corta, casos_uso_fh, nivel_dificultad,
                   plan_gratuito, privacidad, tags
            FROM hgu_herramientas_ia
            ORDER BY categoria, nombre
        """))).fetchall()
        catalogo = "\n".join([
            f"- {r.nombre} ({r.categoria}): {r.descripcion_corta} | Nivel: {r.nivel_dificultad} | "
            f"Privacidad: {r.privacidad} | Gratuito: {r.plan_gratuito or 'No'} | "
            f"Casos FH: {json.dumps(r.casos_uso_fh, ensure_ascii=False) if r.casos_uso_fh else 'N/A'}"
            for r in rows
        ])
    prompt = f"""{SIGFAR_CONTEXT_PROMPT}

Eres un consultor experto en IA aplicada a farmacia hospitalaria.
El farmacéutico tiene esta necesidad:
"{necesidad}"

Catálogo disponible de herramientas IA:
{catalogo}

Recomienda las 3-5 mejores herramientas para esta necesidad. Para cada una:
1. Nombre de la herramienta
2. Por qué es la mejor opción para esta necesidad concreta
3. Caso de uso específico en farmacia hospitalaria
4. Nivel de dificultad y si tiene plan gratuito
5. Consejo práctico para empezar

Responde en español, formato estructurado con encabezados markdown.
Al final añade una sección "Flujo de trabajo recomendado" combinando las herramientas."""

    api_key = os.getenv("OPENAI_API_KEY", "")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "llama-3.3-70b-versatile", "temperature": 0.4,
                  "messages": [{"role": "user", "content": prompt}]}
        )
        data = resp.json()
    return {
        "necesidad": necesidad,
        "recomendacion": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
        "modelo": "llama-3.3-70b-versatile"
    }


# ── H10. IA — Generar prompt optimizado ──────────────────────
@app.post("/api/herramientas/ia/generar-prompt")
async def ia_generar_prompt(body: dict):
    herramienta = body.get("herramienta", "")
    tarea = body.get("tarea", "")
    contexto = body.get("contexto", "")
    if not herramienta or not tarea:
        raise HTTPException(400, "Indica herramienta y tarea")

    prompt = f"""{SIGFAR_CONTEXT_PROMPT}

Eres un experto en prompt engineering para farmacia hospitalaria.
El farmacéutico quiere usar la herramienta "{herramienta}" para la tarea: "{tarea}".
{f'Contexto adicional: {contexto}' if contexto else ''}

Genera 3 prompts optimizados para esta herramienta y tarea:

1. **Prompt básico**: Directo y funcional
2. **Prompt avanzado**: Con técnicas de prompt engineering (chain-of-thought, few-shot, etc.)
3. **Prompt experto**: Máxima calidad, con role-play, formato estructurado y validaciones

Para cada prompt incluye:
- El prompt completo listo para copiar/pegar
- Técnica de prompt engineering utilizada
- Tips para mejorar el resultado

Responde en español. Los prompts deben ser específicos para farmacia hospitalaria."""

    api_key = os.getenv("OPENAI_API_KEY", "")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "llama-3.3-70b-versatile", "temperature": 0.5,
                  "messages": [{"role": "user", "content": prompt}]}
        )
        data = resp.json()
    return {
        "herramienta": herramienta,
        "tarea": tarea,
        "prompts": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
        "modelo": "llama-3.3-70b-versatile"
    }
