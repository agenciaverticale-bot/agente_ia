import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
import requests

# Carrega as variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="CRM Chatbot Admin", page_icon="🤖", layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ As variáveis SUPABASE_URL ou SUPABASE_KEY não foram encontradas. Verifique se o seu arquivo .env está na mesma pasta e preenchido corretamente!")
    st.stop()

if not SUPABASE_URL.startswith("http"):
    st.error(f"⚠️ A sua SUPABASE_URL parece estar no formato errado. Ela deve ser a URL da API (começando com 'https://'), mas atualmente é: `{SUPABASE_URL}`")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÃO PARA ENVIAR MENSAGEM (WHATSAPP) ---
def send_whatsapp_message(to: str, text: str):
    if not META_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        st.error("Credenciais da Meta não configuradas no .env")
        return False
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200

st.title("🎛️ Painel do Chatbot Multicanal")

aba1, aba2, aba3, aba4 = st.tabs(["💬 Atendimento Direto", "📊 Kanban & Funil", "🗄️ Histórico Bruto", "🧠 Base de Conhecimento"])

with aba1:
    st.header("Atendimento Direto")
    st.write("Assuma o controle da conversa e fale diretamente com o cliente.")
    
    try:
        # Busca telefones únicos para o seletor
        res_phones = supabase.table("chat_history").select("phone").execute()
        if res_phones.data:
            unique_phones = list(set([item["phone"] for item in res_phones.data]))
            selected_phone = st.selectbox("Selecione o Cliente para Atendimento:", unique_phones)
            
            # Exibe o histórico de chat usando os componentes nativos do Streamlit
            if selected_phone:
                st.divider()
                chat_res = supabase.table("chat_history").select("role, content").eq("phone", selected_phone).order("created_at", asc=True).execute()
                
                # Container para o chat
                chat_container = st.container(height=400)
                with chat_container:
                    for msg in chat_res.data:
                        # Define o avatar visual baseado em quem mandou a mensagem
                        avatar = "🧑‍💻" if msg["role"] in ["assistant", "admin"] else "👤"
                        with st.chat_message(msg["role"], avatar=avatar):
                            st.markdown(msg["content"])
                
                # Caixa de input para o administrador enviar mensagem
                if admin_text := st.chat_input("Digite sua mensagem para o cliente..."):
                    # Salva no banco de dados como 'admin'
                    supabase.table("chat_history").insert({"phone": selected_phone, "role": "admin", "content": admin_text}).execute()
                    # Envia para a API do WhatsApp
                    send_whatsapp_message(selected_phone, admin_text)
                    st.rerun() # Atualiza a tela para mostrar a nova mensagem
        else:
            st.info("Nenhum cliente registrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar o chat: {e}")

with aba2:
    st.header("Kanban / Jornada do Cliente")
    st.write("Visualize a etapa de cada cliente no seu CRM.")
    
    # Estrutura visual base de colunas para o Kanban
    # Para alimentar com dados reais do HubSpot, faremos consultas à API do HubSpot aqui.
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔵 Novos Leads")
        with st.container(border=True):
            st.write("**João Silva**\n\n+55 11 9999-9999")
            st.button("Ver detalhes", key="btn1")
            
    with col2:
        st.subheader("🟡 Em Negociação")
        with st.container(border=True):
            st.write("**Maria Souza**\n\n+55 11 8888-8888")
            st.button("Ver detalhes", key="btn2")
            
    with col3:
        st.subheader("🟢 Fechado / Ganho")
        with st.container(border=True):
            st.write("**Empresa XYZ**\n\n+55 11 7777-7777")
            st.button("Ver detalhes", key="btn3")

with aba3:
    st.header("Conversas Recentes")
    if st.button("🔄 Atualizar Conversas"):
        st.rerun()
        
    try:
        # Busca dados no Supabase
        res = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(50).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
            # Mostra uma tabela interativa bonita
            st.dataframe(df[['created_at', 'phone', 'role', 'content']], use_container_width=True)
        else:
            st.info("Nenhuma conversa registrada ainda.")
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")

with aba4:
    st.header("Documentos na Memória da IA")
    
    try:
        res_kb = supabase.table("knowledge_base").select("id, content").limit(100).execute()
        if res_kb.data:
            df_kb = pd.DataFrame(res_kb.data)
            st.dataframe(df_kb, use_container_width=True)
        else:
            st.info("Sua base de conhecimento está vazia. Rode o script de inserir_conhecimento.py")
    except Exception as e:
        st.error(f"Erro ao buscar base de conhecimento: {e}")