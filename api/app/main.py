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
