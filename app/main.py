from fastapi import FastAPI, Request, BackgroundTasks
import os, httpx, asyncio, json
from .bot import handle_message

app = FastAPI()

INSTANCE_ID = os.getenv("INSTANCE_ID")
INSTANCE_TOKEN = os.getenv("INSTANCE_TOKEN")

ZAPI_BASE = "https://api.z-api.io/instances"

async def zapi_send_text(phone: str, text: str):
    """Envia texto simples pelo Z‑API."""
    url = f"{ZAPI_BASE}/{INSTANCE_ID}/token/{INSTANCE_TOKEN}/send-message-text"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"phone": phone, "message": text})

@app.post('/webhook')
async def webhook(req: Request, bg: BackgroundTasks):
    """Rota que recebe eventos do Z‑API (precisa ser HTTPS)."""
    payload = await req.json()
    # processa apenas as mensagens recebidas
    if payload.get("type") == "ReceivedCallback":
        phone = payload.get("phone") or payload.get("from")
        text = payload.get("message", {}).get("text") or payload.get("text") or ""
        bg.add_task(flow, phone, text)
    return {"status": "received"}

async def flow(phone: str, text: str):
    """Desacopla processamento da thread do webhook."""
    async def send(to, msg):
        await zapi_send_text(to, msg)
    reply = await handle_message(phone, text, send)
    if reply:
        await send(phone, reply)

@app.get('/')
def health():
    return {"ok": True}
