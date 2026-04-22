# Arquitetura Avançada: Agente de Vendas IA Multicanal (Custo Zero)

## 1. Fluxo de Inteligência (RAG)
- **Base de Conhecimento:** Documentos (PDF/TXT) são convertidos em vetores e armazenados no **Supabase Vector (pgvector)**.
- **Busca Semântica:** Quando o cliente pergunta algo, o sistema busca os trechos mais relevantes no Supabase.
- **Prompt de Vendas:** A IA recebe a pergunta + trechos da base + histórico + instruções de tom de voz para gerar a resposta.

## 2. Integração com CRM (HubSpot)
- **Identificação:** Ao receber uma mensagem, o sistema verifica se o `phone_number` ou `social_id` já existe no HubSpot.
- **Cadastro:** Se for novo, cria um `Contact` com a tag "Novo Lead".
- **Funil:** Conforme a conversa avança (ex: pediu preço), o sistema move o lead para a etapa "Interessado" no funil de vendas via API.

## 3. Sistema de Pagamentos (Mercado Pago/Stripe)
- **Geração de Link:** Quando o cliente decide comprar, o bot gera um link de checkout via API.
- **Confirmação:** O sistema recebe um **Webhook** do processador de pagamento quando o status muda para "approved".
- **Pós-Venda:** O bot envia uma mensagem automática de confirmação e instruções de entrega.

## 4. Tecnologias Utilizadas (Camadas Gratuitas)
- **Backend:** FastAPI (Hospedado no Render Free).
- **IA:** Groq (Llama 3 70B) - Grátis.
- **Banco de Dados & Vetores:** Supabase - Grátis (500MB).
- **CRM:** HubSpot - Grátis (1.000.000 contatos).
- **Mensageria:** Meta Cloud API & TikTok Business API - Grátis.
