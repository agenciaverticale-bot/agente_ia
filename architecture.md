# Arquitetura do Chatbot Multicanal IA (Custo Zero)

## 1. Componentes Principais
- **Linguagem:** Python 3.11+
- **Framework Web:** FastAPI (rápido, assíncrono e leve para webhooks)
- **IA (Cérebro):** Groq Cloud API (Modelo Llama 3 70B ou 8B) - Grátis e extremamente rápido.
- **Banco de Dados (Opcional):** SQLite (local) ou Supabase (camada gratuita) para histórico de conversas.

## 2. Integrações (Webhooks)
- **WhatsApp:** Meta Cloud API (Webhook para receber, POST para enviar).
- **Instagram/Facebook:** Meta Messenger API (Webhook compartilhado).
- **TikTok:** TikTok Business Messaging API (Webhook para eventos de mensagem).

## 3. Fluxo de Dados
1. O usuário envia mensagem em qualquer rede social.
2. A plataforma envia um **Webhook (POST)** para o nosso servidor (FastAPI).
3. O servidor extrai o texto e o ID do usuário.
4. O servidor consulta o histórico (opcional) e envia para a **Groq API**.
5. A Groq retorna a resposta da IA.
6. O servidor envia a resposta de volta para a API oficial da plataforma correspondente.

## 4. Hospedagem (Deploy)
- **Render.com:** Plano gratuito (Web Service).
- **Ngrok (Local):** Para testes iniciais de webhook.

## 5. Segurança
- Uso de `Environment Variables` (.env) para chaves de API.
- Verificação de assinatura de webhook (X-Hub-Signature) para garantir que as mensagens vêm da Meta/TikTok.
