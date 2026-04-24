import os
import json
import requests
import re
import hashlib
import hmac
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

load_dotenv()

app = FastAPI()

# --- CONFIGURAÇÕES ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
MESSENGER_ACCESS_TOKEN = os.getenv("MESSENGER_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MERCADO_PAGO_TOKEN = os.getenv("MERCADO_PAGO_TOKEN")
MERCADO_PAGO_WEBHOOK_SECRET = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET")

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializar Modelo de IA para Busca Vetorial (RAG)
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- MEMÓRIA DA IA (SUPABASE) ---
def get_chat_history(phone: str, limit: int = 10):
    try:
        # Busca as últimas 'limit' mensagens, ordenadas da mais recente para a mais antiga
        res = supabase.table("chat_history").select("role, content").eq("phone", phone).order("created_at", desc=True).limit(limit).execute()
        if res.data:
            # Inverte a lista para que a mais antiga fique primeiro (ordem cronológica para a IA entender o contexto)
            return [{"role": row["role"], "content": row["content"]} for row in reversed(res.data)]
    except Exception as e:
        print(f"Erro ao buscar histórico no Supabase: {e}")
    return []

def save_chat_message(phone: str, role: str, content: str):
    try:
        supabase.table("chat_history").insert({
            "phone": phone,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        print(f"Erro ao salvar mensagem no Supabase: {e}")

# --- CAMADA DE CRM (HUBSPOT) ---
def sync_to_hubspot(phone: str, name: str = "Lead Novo", tag: str = "chatbot_lead"):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    # 1. Verificar se contato existe
    search_url = f"{url}/search"
    search_data = {
        "filterGroups": [{"filters": [{"propertyName": "phone", "operator": "EQ", "value": phone}]}]
    }
    search_res = requests.post(search_url, headers=headers, json=search_data).json()
    
    if search_res.get("total", 0) > 0:
        contact_id = search_res["results"][0]["id"]
        # Atualizar tag/propriedade se necessário
        return contact_id
    
    # 2. Criar novo contato
    data = {
        "properties": {
            "phone": phone,
            "firstname": name,
            "lifecyclestage": "lead",
            "hs_lead_status": "NEW"
        }
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("id")

# --- CAMADA DE CONHECIMENTO (RAG + SUPABASE) ---
def get_knowledge_base(query: str):
    try:
        query_embedding = model.encode(query).tolist()
        res = supabase.rpc('match_documents', {'query_embedding': query_embedding, 'match_threshold': 0.3, 'match_count': 3}).execute()
        if res.data:
            return "\n".join([item['content'] for item in res.data])
    except Exception as e:
        print(f"Erro RAG: {e}")
    return ""

# --- CAMADA DE IA (GROQ) ---
def get_ai_sales_response(user_message: str, history: List[dict], knowledge: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    Você é um Agente de Vendas de Alta Performance. Seu tom de voz é profissional, persuasivo e amigável.
    BASE DE CONHECIMENTO: {knowledge}
    DIRETRIZES:
    1. Use apenas as informações da Base de Conhecimento para responder sobre produtos/preços.
    2. Se o cliente quiser comprar e já souber o produto, GERE O LINK DE PAGAMENTO.
    3. Para gerar o link, você DEVE incluir na sua resposta a tag exata: [GERAR_PAGAMENTO: Nome do Produto : 99.90] (use ponto para centavos).
    4. Exemplo de resposta: "Excelente escolha! Segue o link de pagamento: [GERAR_PAGAMENTO: Plano Premium : 199.90]"
    5. Seja conciso e nunca invente preços ou prazos.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-5:]) # Últimas 5 mensagens para contexto
    messages.append({"role": "user", "content": user_message})
    
    data = {"model": "llama3-70b-8192", "messages": messages}
    response = requests.post(url, headers=headers, json=data).json()
    return response['choices'][0]['message']['content']

# --- FUNÇÃO DE ENVIO DE MENSAGEM (WHATSAPP) ---
def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

# --- CAMADA DE PAGAMENTOS (MERCADO PAGO) ---
def create_payment_link(title: str, price: float, phone: str = ""):
    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {"Authorization": f"Bearer {MERCADO_PAGO_TOKEN}", "Content-Type": "application/json"}
    data = {
        "items": [{"title": title, "quantity": 1, "unit_price": price, "currency_id": "BRL"}],
        "back_urls": {
            "success": "https://crm.agenciaverticale.com.br/sucesso",
            "failure": "https://crm.agenciaverticale.com.br/falha",
            "pending": "https://crm.agenciaverticale.com.br/pendente"
        },
        "auto_return": "approved",
        "external_reference": phone
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res.get("init_point")

# --- WEBHOOKS (META / WHATSAPP / INSTA / FB) ---

# Callback de Login do Instagram / Meta
@app.get("/auth/meta/callback")
async def meta_auth_callback(request: Request):
    # Rota usada como "URL de Redirecionamento" no painel da Meta
    code = request.query_params.get("code")
    if code:
        return {"message": "Autenticacao concluida com sucesso! Voce ja pode fechar esta janela.", "codigo_recebido": code}
    return {"error": "Nenhum codigo de autorizacao recebido."}

# Verificação do Webhook da Meta
@app.get("/webhook/meta")
async def verify_meta(request: Request):
    params = request.query_params
    
    # --- DEBUG PARA DESCOBRIR O ERRO DA META ---
    print("\n--- TENTATIVA DE VALIDAÇÃO DO WEBHOOK ---")
    print(f"1. Parâmetros recebidos da Meta: {params}")
    print(f"2. Token no seu .env: '{META_VERIFY_TOKEN}'")
    print(f"3. Token recebido da Meta: '{params.get('hub.verify_token')}'")
    print("-------------------------------------------\n")

    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == META_VERIFY_TOKEN:
        challenge = params.get("hub.challenge")
        return Response(content=str(challenge), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Token de verificação inválido")

@app.post("/webhook/meta")
async def handle_meta(request: Request):
    body = await request.json()
    # Lógica para extrair mensagem e remetente (WhatsApp, Instagram, Messenger)
    try:
        print(f"DEBUG: Recebido corpo do webhook: {json.dumps(body)}")
        entry = body["entry"][0]
        
        # --- WHATSAPP ---
        if "changes" in entry:
            value = entry["changes"][0]["value"]
            if "messages" in value:
                msg = value["messages"][0]
                sender_id = msg["from"]
                text = msg.get("text", {}).get("body", "")
                platform = "whatsapp"
                
                if not text: return {"status": "no text"}

                # 1. Sincronizar CRM
                sync_to_hubspot(sender_id)
                
                # 2. Buscar Conhecimento
                knowledge = get_knowledge_base(text)
                
                # --- RECUPERAR HISTÓRICO DO SUPABASE ---
                history = get_chat_history(sender_id, limit=10)
                
                # 3. Gerar Resposta IA
                reply = get_ai_sales_response(text, history, knowledge)
                
                # --- INTERCEPTAR COMANDO DE PAGAMENTO DA IA ---
                match = re.search(r'\[GERAR_PAGAMENTO:\s*(.*?)\s*:\s*([\d.]+)\]', reply)
                if match:
                    produto = match.group(1).strip()
                    try:
                        preco = float(match.group(2).strip())
                        link = create_payment_link(produto, preco, sender_id)
                        reply = reply.replace(match.group(0), f"\n👉 *Link Seguro (Mercado Pago):* {link}\n")
                    except Exception as e:
                        print(f"Erro ao gerar link: {e}")
                        reply = reply.replace(match.group(0), "\n⚠️ *(Ops, erro ao gerar link de pagamento. Tente novamente.)*\n")
                
                # --- ATUALIZAR HISTÓRICO NO SUPABASE ---
                save_chat_message(sender_id, "user", text)
                save_chat_message(sender_id, "assistant", reply)
                
                # 4. Enviar Resposta
                send_whatsapp_message(sender_id, reply)

        # --- MESSENGER / INSTAGRAM ---
        elif "messaging" in entry:
            messaging_event = entry["messaging"][0]
            sender_id = messaging_event["sender"]["id"]
            text = messaging_event.get("message", {}).get("text", "")
            
            # Detecta a plataforma correta pelo objeto do webhook
            if body.get("object") == "instagram":
                platform = "instagram"
                access_token = INSTAGRAM_ACCESS_TOKEN
            else:
                platform = "messenger"
                access_token = MESSENGER_ACCESS_TOKEN

            if text:
                knowledge = get_knowledge_base(text)
                history = get_chat_history(sender_id, limit=10)
                reply = get_ai_sales_response(text, history, knowledge)
                
                save_chat_message(sender_id, "user", text)
                save_chat_message(sender_id, "assistant", reply)
                
                # Função de envio para Meta (Insta/Messenger)
                url_meta = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
                data_meta = {"recipient": {"id": sender_id}, "message": {"text": reply}}
                requests.post(url_meta, json=data_meta)
    except: pass
    return {"status": "ok"}

# --- WEBHOOK DE PAGAMENTO (CONFIRMAÇÃO) ---
@app.post("/webhook/payments")
async def handle_payment_notification(request: Request):
    # 1. Extrair os Headers e Query Params da notificação
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")
    
    data_id = request.query_params.get("data.id")
    event_type = request.query_params.get("type")

    if not x_signature or not data_id or not event_type:
        # Retorna 200 para o Mercado Pago parar de enviar tentativas falhas
        return Response(status_code=200)

    # 2. Validar a assinatura da notificação (HMAC SHA256)
    try:
        parts = x_signature.split(",")
        ts, v1_hash = None, None
        for part in parts:
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                if key_value[0].strip() == "ts":
                    ts = key_value[1].strip()
                elif key_value[0].strip() == "v1":
                    v1_hash = key_value[1].strip()

        if ts and v1_hash and MERCADO_PAGO_WEBHOOK_SECRET:
            # Monta o manifesto dinâmico conforme documentação
            manifest = f"id:{data_id};"
            if x_request_id:
                manifest += f"request-id:{x_request_id};"
            manifest += f"ts:{ts};"

            # Gera o hash e compara
            hmac_obj = hmac.new(MERCADO_PAGO_WEBHOOK_SECRET.encode(), msg=manifest.encode(), digestmod=hashlib.sha256)
            if hmac_obj.hexdigest() != v1_hash:
                print("Webhook MP: Assinatura inválida! Possível fraude.")
                return Response(status_code=403)
    except Exception as e:
        print(f"Erro ao validar assinatura do MP: {e}")
        return Response(status_code=500)
        
    return Response(status_code=200)