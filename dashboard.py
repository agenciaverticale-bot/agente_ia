import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
import requests
import time

# Carrega as variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="CRM Chatbot Admin", page_icon="🤖", layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
MESSENGER_ACCESS_TOKEN = os.getenv("MESSENGER_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Configurações do Supabase não encontradas!")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÕES DE ENVIO ---
def send_message(to: str, text: str, platform: str):
    if platform == "whatsapp":
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    else:
        access_token = INSTAGRAM_ACCESS_TOKEN if platform == "instagram" else MESSENGER_ACCESS_TOKEN
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
        data = {"recipient": {"id": to}, "message": {"text": text}}
        headers = {"Content-Type": "application/json"}
    
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200

st.title("🎛️ Painel do Chatbot Multicanal")

# --- LOGIN SIMULADO (PREPARAÇÃO PARA OAUTH) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login Administrativo")
    
    # Verifica se o usuário já está logado via URL (retorno do Supabase)
    query_params = st.query_params
    if "access_token" in query_params or "id_token" in query_params:
        st.session_state.logged_in = True
        st.rerun()

    if st.button("Entrar com Facebook"):
        try:
            # Gera a URL de login do Facebook via Supabase
            res = supabase.auth.sign_in_with_oauth({
                "provider": "facebook",
                "options": {
                    "redirect_to": "https://crm.agenciaverticale.com.br" # Seu domínio profissional
                }
            })
            if res.url:
                st.link_button("Clique aqui para autorizar no Facebook", res.url)
                st.info("Após autorizar, você será redirecionado de volta para cá.")
        except Exception as e:
            st.error(f"Erro ao iniciar login: {e}")
    st.stop()

aba1, aba2, aba3, aba4 = st.tabs(["💬 Atendimento Direto", "📊 Kanban & Funil", "🗄️ Histórico Bruto", "🧠 Base de Conhecimento"])

with aba1:
    st.header("Atendimento Direto")
    
    try:
        # Busca telefones/IDs únicos
        res_phones = supabase.table("chat_history").select("phone, platform").execute()
        if res_phones.data:
            df_contacts = pd.DataFrame(res_phones.data).drop_duplicates()
            contact_list = [f"{row['phone']} ({row['platform']})" for _, row in df_contacts.iterrows()]
            selected_contact_str = st.selectbox("Selecione o Cliente:", contact_list)
            
            if selected_contact_str:
                selected_phone = selected_contact_str.split(" (")[0]
                selected_platform = selected_contact_str.split(" (")[1].replace(")", "")
                
                st.divider()
                chat_res = supabase.table("chat_history").select("role, content, created_at").eq("phone", selected_phone).order("created_at", asc=True).execute()
                
                chat_container = st.container(height=500)
                with chat_container:
                    for msg in chat_res.data:
                        avatar = "🧑‍💻" if msg["role"] in ["assistant", "admin"] else "👤"
                        with st.chat_message(msg["role"], avatar=avatar):
                            st.markdown(msg["content"])
                            st.caption(f"{msg['created_at']}")
                
                if admin_text := st.chat_input("Digite sua resposta..."):
                    # Salva no banco
                    supabase.table("chat_history").insert({
                        "phone": selected_phone, 
                        "role": "admin", 
                        "content": admin_text,
                        "platform": selected_platform
                    }).execute()
                    # Envia para a API correspondente
                    if send_message(selected_phone, admin_text, selected_platform):
                        st.success("Mensagem enviada!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erro ao enviar mensagem. Verifique os tokens.")
        else:
            st.info("Nenhum cliente registrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar o chat: {e}")

with aba2:
    st.header("Kanban / Jornada do Cliente")
    st.info("Integração com HubSpot ativa. Os leads abaixo são sincronizados automaticamente.")
    col1, col2, col3 = st.columns(3)
    # Exemplo estático que pode ser expandido com API do HubSpot
    with col1: st.subheader("🔵 Novos Leads"); st.write("Aguardando contato...")
    with col2: st.subheader("🟡 Em Negociação"); st.write("Propostas enviadas...")
    with col3: st.subheader("🟢 Fechado / Ganho"); st.write("Vendas concluídas!")

with aba3:
    st.header("Histórico Geral")
    if st.button("🔄 Atualizar"): st.rerun()
    res = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(100).execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

with aba4:
    st.header("Base de Conhecimento (RAG)")
    st.write("Estes são os documentos que a IA usa para responder.")
    res_kb = supabase.table("knowledge_base").select("id, content").execute()
    if res_kb.data:
        st.dataframe(pd.DataFrame(res_kb.data), use_container_width=True)
