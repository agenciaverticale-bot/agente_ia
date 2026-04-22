# Guia Avançado: Agente de Vendas IA Multicanal Robusto (Custo Zero)

Este guia detalha a configuração e implantação de um Agente de Vendas de Inteligência Artificial multicanal, integrado com CRM (HubSpot), Base de Conhecimento (Supabase RAG) e Checkout de Pagamentos (Mercado Pago/Stripe), tudo com foco em custo zero e utilizando APIs oficiais para evitar banimentos.

## 1. Visão Geral da Arquitetura Robusta

Nosso Agente de Vendas é um sistema sofisticado que orquestra diversas ferramentas gratuitas para automatizar o processo de vendas do início ao fim.

| Componente | Função | Tecnologia/Serviço | Custo | Risco de Banimento |
| :--- | :--- | :--- | :--- | :--- |
| **Servidor Central** | Orquestra mensagens, IA, CRM, RAG, Pagamentos | Python (FastAPI) | Grátis (Hospedagem) | Baixo (APIs Oficiais) |
| **IA (Cérebro de Vendas)** | Gera respostas persuasivas, segue diretrizes de vendas | Groq Cloud (Llama 3) | Grátis (Camada Free) | N/A |
| **Base de Conhecimento (RAG)** | Armazena produtos, preços, FAQs; busca contextual | Supabase (pgvector) | Grátis (500MB DB, 1GB Storage) | N/A |
| **CRM & Funil de Vendas** | Gerencia leads, contatos, tags, etapas do funil | HubSpot (Plano Free) | Grátis (1M contatos, 100 reqs/10s) | N/A |
| **WhatsApp** | Comunicação com clientes | Meta Cloud API | 1.000 conversas/mês grátis | Baixo (API Oficial) |
| **Instagram/Facebook** | Comunicação com clientes | Meta Messenger API | Grátis | Baixo (API Oficial) |
| **TikTok** | Comunicação com clientes | TikTok Business Messaging API | Grátis (Requer Conta Business) | Baixo (API Oficial) |
| **Pagamentos** | Gera links de checkout, confirma vendas | Mercado Pago / Stripe | Grátis (Taxas por transação) | N/A |
| **Hospedagem** | Execução do servidor 24/7 | Render.com / Railway.app | Grátis (Planos Free) | N/A |

## 2. Pré-requisitos

Certifique-se de ter:

*   Uma conta no [GitHub](https://github.com/) (para versionamento e deploy).
*   Python 3.11+ instalado em sua máquina local.
*   `pip` (gerenciador de pacotes Python).
*   Um editor de código (VS Code, Sublime Text, etc.).

## 3. Configuração do Ambiente Local

1.  **Obtenha os Arquivos:**
    Os arquivos `agente_vendas_robusto.py`, `requirements_v2.txt` e `.env.v2.example` foram fornecidos. Salve-os em uma pasta local.

2.  **Instale as Dependências:**
    Abra o terminal na pasta do projeto e execute:
    ```bash
    pip install -r requirements_v2.txt
    ```

3.  **Crie o Arquivo `.env`:**
    Copie o conteúdo de `.env.v2.example` para um novo arquivo chamado `.env` na raiz do projeto. Este arquivo armazenará suas chaves de API e tokens de forma segura.

    ```dotenv
    # IA (GROQ)
    GROQ_API_KEY=sua_chave_da_groq_aqui

    # META (WhatsApp, Instagram, Facebook)
    META_ACCESS_TOKEN=seu_token_de_acesso_permanente_aqui
    META_VERIFY_TOKEN=um_nome_que_voce_inventar_ex_meu_bot_123
    WHATSAPP_PHONE_NUMBER_ID=id_do_seu_numero_no_painel_da_meta

    # TIKTOK
    TIKTOK_ACCESS_TOKEN=seu_token_do_tiktok_business_aqui

    # CRM (HUBSPOT)
    HUBSPOT_ACCESS_TOKEN=seu_token_de_acesso_privado_do_hubspot

    # BASE DE CONHECIMENTO (SUPABASE)
    SUPABASE_URL=sua_url_do_supabase
    SUPABASE_KEY=sua_chave_anon_do_supabase

    # PAGAMENTOS (MERCADO PAGO)
    MERCADO_PAGO_TOKEN=seu_access_token_do_mercado_pago
    ```

## 4. Obtenção das Chaves de API e Tokens

### 4.1. Groq Cloud (IA)

1.  Acesse [Groq Cloud](https://groq.com/).
2.  Crie uma conta ou faça login.
3.  Navegue até `API Keys`.
4.  Gere uma nova chave e copie-a para `GROQ_API_KEY` no seu `.env`.

### 4.2. Meta (WhatsApp, Instagram, Facebook)

Para WhatsApp, Instagram e Facebook, você precisará de um aplicativo no [Meta for Developers](https://developers.facebook.com/).

1.  **Crie um Aplicativo:**
    *   Acesse [Meta for Developers](https://developers.facebook.com/) e faça login.
    *   Clique em `Meus Aplicativos` > `Criar Aplicativo` > `Negócios`.
    *   Associe-o ao seu Gerenciador de Negócios da Meta.

2.  **Configure o WhatsApp Business Platform:**
    *   No painel do aplicativo, adicione o produto `WhatsApp`.
    *   Siga as etapas para configurar a API, verificando seu número de telefone.
    *   Anote o `ID do Número de Telefone` (Phone Number ID) para `WHATSAPP_PHONE_NUMBER_ID`.
    *   **Token de Acesso Permanente:** Na seção `Configuração` do WhatsApp, você encontrará um `Token de Acesso Temporário`. Para produção, você precisará de um `Token de Acesso Permanente`. Siga a documentação da Meta para gerar um `Token de Acesso de Sistema` ou `Token de Acesso de Usuário de Longa Duração`.
    *   Copie o `Token de Acesso Permanente` para `META_ACCESS_TOKEN`.
    *   Defina um `Token de Verificação` de sua escolha (ex: `meu_bot_123`) para `META_VERIFY_TOKEN`.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/meta` (o domínio será obtido após o deploy).

3.  **Configure Instagram e Facebook Messenger:**
    *   No painel do aplicativo, adicione o produto `Messenger`.
    *   Associe sua conta profissional do Instagram e sua página do Facebook ao aplicativo.
    *   O `META_ACCESS_TOKEN` e `META_VERIFY_TOKEN` já configurados servirão para essas plataformas.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/meta` também para o Messenger.

### 4.3. TikTok Business Messaging API

1.  **Converta para Conta Business:**
    *   No app TikTok: `Configurações e privacidade` > `Gerenciar conta` > `Mudar para Conta Business`.

2.  **Crie um Aplicativo no TikTok for Developers:**
    *   Acesse [TikTok for Developers](https://developers.tiktok.com/) e faça login.
    *   Clique em `Meus Aplicativos` > `Criar Novo Aplicativo`.
    *   Solicite as permissões necessárias para mensagens.
    *   Após aprovação, você terá `Client Key` e `Client Secret`.
    *   **Access Token:** O processo para obter o `TIKTOK_ACCESS_TOKEN` envolve autenticação OAuth 2.0. Consulte a documentação do TikTok for Developers para obter um `Access Token` de longa duração.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/tiktok`.

### 4.4. HubSpot CRM (Plano Free)

1.  **Crie uma Conta HubSpot:**
    *   Acesse [HubSpot](https://www.hubspot.com/) e crie uma conta gratuita.

2.  **Gere um Token de Acesso Privado:**
    *   No HubSpot, vá em `Configurações` (ícone de engrenagem) > `Integrações` > `Tokens de acesso privado`.
    *   Crie um novo token e conceda as permissões necessárias para `CRM` (Contatos, Empresas, Negócios).
    *   Copie o token e cole-o em `HUBSPOT_ACCESS_TOKEN` no seu `.env`.

### 4.5. Supabase (Base de Conhecimento RAG)

1.  **Crie um Projeto Supabase:**
    *   Acesse [Supabase](https://supabase.com/) e crie uma conta gratuita.
    *   Crie um novo projeto.

2.  **Obtenha Credenciais:**
    *   No painel do seu projeto, vá em `Project Settings` > `API`.
    *   Copie a `URL` e a `anon public key`.
    *   Cole-as em `SUPABASE_URL` e `SUPABASE_KEY` no seu `.env`.

3.  **Configure o Banco de Dados Vetorial (pgvector):**
    *   No Supabase, vá em `Database` > `Extensions`.
    *   Ative a extensão `pgvector`.
    *   Vá em `SQL Editor` e execute o seguinte comando para criar a tabela da sua base de conhecimento:
        ```sql
        CREATE TABLE knowledge_base (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content TEXT,
            embedding VECTOR(1536) -- Tamanho do embedding do modelo que você usar (ex: OpenAI text-embedding-ada-002)
        );
        ```
    *   **Importe seus Dados:** Para popular a `knowledge_base`, você precisará de um script Python separado que leia seus documentos (PDFs, TXT), divida-os em chunks, gere embeddings (usando OpenAI, Cohere, etc. - a Groq não gera embeddings diretamente) e os insira nesta tabela. Este script não está incluído no `agente_vendas_robusto.py` para manter o foco no chatbot, mas é um passo crucial para o RAG.

### 4.6. Mercado Pago ou Stripe (Pagamentos)

#### Mercado Pago

1.  **Crie uma Conta Mercado Pago:**
    *   Acesse [Mercado Pago](https://www.mercadopago.com.br/) e crie uma conta.

2.  **Obtenha Credenciais:**
    *   No painel, vá em `Seu Negócio` > `Configurações` > `Credenciais`.
    *   Copie seu `Access Token` para `MERCADO_PAGO_TOKEN` no seu `.env`.

3.  **Configure Webhooks:**
    *   Vá em `Seu Negócio` > `Configurações` > `Notificações`.
    *   Adicione um `URL de Webhook` para `https://SEU_DOMINIO/webhook/payments`.
    *   Selecione os eventos de `Pagamentos`.

#### Stripe (Alternativa)

1.  **Crie uma Conta Stripe:**
    *   Acesse [Stripe](https://stripe.com/) e crie uma conta.

2.  **Obtenha Credenciais:**
    *   No painel, vá em `Developers` > `API keys`.
    *   Copie sua `Secret key` para `STRIPE_SECRET_KEY` (você precisaria adicionar esta variável ao `.env` e adaptar o código).

3.  **Configure Webhooks:**
    *   Vá em `Developers` > `Webhooks`.
    *   Adicione um endpoint para `https://SEU_DOMINIO/webhook/payments`.
    *   Selecione os eventos de `checkout.session.completed` e `payment_intent.succeeded`.

## 5. Hospedagem Gratuita (Render.com)

Vamos usar o Render.com para hospedar seu Agente de Vendas gratuitamente.

1.  **Crie uma Conta no Render:**
    *   Acesse [Render.com](https://render.com/) e crie uma conta (use seu GitHub).

2.  **Crie um Novo Web Service:**
    *   No painel do Render, clique em `New` > `Web Service`.
    *   Conecte seu repositório GitHub onde você salvou o código do chatbot.
    *   **Nome:** `agente-vendas-ia`.
    *   **Região:** Escolha a mais próxima.
    *   **Branch:** `main`.
    *   **Root Directory:** `/`.
    *   **Runtime:** `Python 3`.
    *   **Build Command:** `pip install -r requirements_v2.txt`.
    *   **Start Command:** `uvicorn agente_vendas_robusto:app --host 0.0.0.0 --port $PORT`.
    *   **Plano:** Selecione o plano `Free`.

3.  **Adicione as Variáveis de Ambiente:**
    *   Na seção `Environment` do seu serviço no Render, adicione todas as variáveis do seu arquivo `.env` (`GROQ_API_KEY`, `META_ACCESS_TOKEN`, `META_VERIFY_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `TIKTOK_ACCESS_TOKEN`, `HUBSPOT_ACCESS_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `MERCADO_PAGO_TOKEN`).

4.  **Deploy:**
    *   Clique em `Create Web Service`. O Render irá construir e implantar seu aplicativo.
    *   Após o deploy, o Render fornecerá um `URL público` (ex: `https://agente-vendas-ia.onrender.com`). Este será o `SEU_DOMINIO` que você usará para configurar os webhooks na Meta, TikTok, HubSpot (se aplicável) e Mercado Pago/Stripe.

## 6. Testando o Agente de Vendas

Após configurar todos os webhooks com o URL público do Render, seu Agente de Vendas estará ativo. Envie mensagens para suas contas para testar:

*   **Interação com a IA:** Pergunte sobre produtos da sua base de conhecimento.
*   **CRM:** Verifique se novos contatos são criados no HubSpot.
*   **Pagamentos:** Peça um link de pagamento e simule uma compra para ver a confirmação.

## 7. Considerações Finais

*   **Persistência de Conversa:** O código inclui um esqueleto para histórico, mas a implementação completa da persistência de conversa (salvar e recuperar no Supabase) é um próximo passo importante.
*   **Embeddings:** Para o RAG funcionar plenamente, você precisará de um serviço de embeddings (ex: OpenAI, Cohere) para converter seus documentos em vetores e inseri-los no Supabase.
*   **Monitoramento:** Monitore os logs do seu serviço no Render e os painéis das APIs para garantir o bom funcionamento.

---

**Autor:** Manus AI
**Data:** 22 de Abril de 2026
