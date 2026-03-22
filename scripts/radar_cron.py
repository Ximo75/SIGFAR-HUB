"""
Ejecutar escaneo Radar IA — para usar con cron del host o manualmente.

Uso manual:
    docker exec sigfar-hub-api python /app/scripts/radar_cron.py

Desde cron del host (cada lunes a las 07:00):
    0 7 * * 1 docker exec sigfar-hub-api python /app/scripts/radar_cron.py >> /var/log/radar_ia.log 2>&1
"""
import httpx
import asyncio
import sys
from datetime import datetime


async def main():
    print(f"[{datetime.now().isoformat()}] Iniciando escaneo Radar IA...")
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            r = await client.post("http://localhost:8000/api/radar/scan", json={})
            if r.status_code == 200:
                d = r.json()
                print(f"[OK] Nuevos: {d['items_nuevos']}, Duplicados: {d['items_duplicados']}, "
                      f"Enriquecidos: {d['items_enriquecidos']}, Duración: {d['duracion_seg']}s")
                if d.get('errors'):
                    print(f"[WARN] Errores: {d['errors']}")
            else:
                print(f"[ERROR] HTTP {r.status_code}: {r.text[:200]}")
                sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
