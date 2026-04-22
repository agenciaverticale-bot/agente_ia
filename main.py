import os
import json
import requests
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configurações de API (Devem ser preenchidas no arquivo .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# --- FUNÇÕES DE IA (GROQ) ---
def get_ai_response(user_message: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Você é um assistente prestativo e amigável que responde mensagens em redes sociais."},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro na Groq: {e}")
        return "Desculpe, estou com um probleminha técnico agora."

# --- FUNÇÕES DE ENVIO ---
def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

def send_meta_message(recipient_id: str, text: str, platform: str):
    # Funciona para Instagram e Facebook Messenger
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={META_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=data)

def send_tiktok_message(open_id: str, text: str):
    url = "https://business-api.tiktok.com/open_api/v1.3/message/send/"
    headers = {"Access-Token": TIKTOK_ACCESS_TOKEN, "Content-Type": "application/json"}
    data = {
        "event_type": "MESSAGE_SEND",
        "message_data": {"text": text},
        "recipient_open_id": open_id
    }
    requests.post(url, headers=headers, json=data)

# --- WEBHOOKS ---

# Verificação do Webhook da Meta (WhatsApp/Insta/FB)
@app.get("/webhook/meta")
async def verify_meta(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == META_VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"))
    return HTTPException(status_code=403)

# Recebimento de mensagens da Meta
@app.post("/webhook/meta")
async def handle_meta(request: Request):
    body = await request.json()
    
    # Lógica para WhatsApp
    if "messages" in body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
        change = body["entry"][0]["changes"][0]["value"]
        message = change["messages"][0]
        sender_id = message["from"]
        text = message.get("text", {}).get("body", "")
        
        if text:
            ai_reply = get_ai_response(text)
            send_whatsapp_message(sender_id, ai_reply)

    # Lógica para Instagram/Messenger
    elif "messaging" in body.get("entry", [{}])[0]:
        messaging_event = body["entry"][0]["messaging"][0]
        sender_id = messaging_event["sender"]["id"]
        text = messaging_event.get("message", {}).get("text", "")
        
        if text:
            ai_reply = get_ai_response(text)
            send_meta_message(sender_id, ai_reply, "meta")

    return {"status": "ok"}

# Webhook do TikTok
@app.post("/webhook/tiktok")
async def handle_tiktok(request: Request):
    body = await request.json()
    # O TikTok envia eventos de mensagem
    if body.get("event") == "message":
        sender_id = body["data"]["sender_open_id"]
        text = body["data"]["content"]
        ai_reply = get_ai_response(text)
        send_tiktok_message(sender_id, ai_reply)
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Chatbot Multicanal IA Ativo!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
