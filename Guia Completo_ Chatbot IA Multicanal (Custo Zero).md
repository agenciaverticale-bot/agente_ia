# Guia Completo: Chatbot IA Multicanal (Custo Zero)

Este guia detalha como configurar e implantar um chatbot de Inteligência Artificial que opera em múltiplas plataformas (WhatsApp, Instagram, Facebook e TikTok) utilizando APIs oficiais para garantir custo zero e evitar banimentos. O projeto utiliza Python com FastAPI, Groq para IA, e plataformas de hospedagem gratuitas.

## 1. Visão Geral da Arquitetura

O chatbot é construído sobre uma arquitetura de microsserviços leve, onde um servidor FastAPI atua como um hub central. Ele recebe mensagens via webhooks das plataformas, as processa com a IA da Groq e envia as respostas de volta através das APIs oficiais de cada canal.

| Componente | Função | Tecnologia/Serviço | Custo | Risco de Banimento |
| :--- | :--- | :--- | :--- | :--- |
| **Servidor** | Recebe/Envia mensagens, integra IA | Python (FastAPI) | Grátis (Hospedagem) | Baixo (APIs Oficiais) |
| **IA (Cérebro)** | Gera respostas inteligentes | Groq Cloud (Llama 3) | Grátis (Camada Free) | N/A |
| **WhatsApp** | Comunicação com usuários | Meta Cloud API | 1.000 conversas/mês grátis | Baixo (API Oficial) |
| **Instagram/Facebook** | Comunicação com usuários | Meta Messenger API | Grátis | Baixo (API Oficial) |
| **TikTok** | Comunicação com usuários | TikTok Business Messaging API | Grátis (Requer Conta Business) | Baixo (API Oficial) |
| **Hospedagem** | Execução do servidor 24/7 | Render.com / Railway.app | Grátis (Planos Free) | N/A |

## 2. Pré-requisitos

Antes de começar, certifique-se de ter:

*   Uma conta no [GitHub](https://github.com/) (para versionamento e deploy).
*   Python 3.11+ instalado em sua máquina local.
*   `pip` (gerenciador de pacotes Python).
*   Um editor de código (VS Code, Sublime Text, etc.).

## 3. Configuração do Ambiente Local

1.  **Clone o Repositório (ou crie os arquivos):**
    Crie uma pasta para o seu projeto e salve os arquivos `main.py`, `requirements.txt` e `.env.example` fornecidos.

2.  **Instale as Dependências:**
    Abra o terminal na pasta do projeto e execute:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Crie o Arquivo `.env`:**
    Copie o conteúdo de `.env.example` para um novo arquivo chamado `.env` na raiz do projeto. Este arquivo armazenará suas chaves de API e tokens de forma segura.

    ```dotenv
    # IA
    GROQ_API_KEY=sua_chave_da_groq_aqui

    # META (WhatsApp, Instagram, Facebook)
    META_ACCESS_TOKEN=seu_token_de_acesso_permanente_aqui
    META_VERIFY_TOKEN=um_nome_que_voce_inventar_ex_meu_bot_123
    WHATSAPP_PHONE_NUMBER_ID=id_do_seu_numero_no_painel_da_meta

    # TIKTOK
    TIKTOK_ACCESS_TOKEN=seu_token_do_tiktok_business_aqui
    ```

## 4. Obtenção das Chaves de API e Tokens

### 4.1. Groq Cloud (IA)

1.  Acesse o site da [Groq Cloud](https://groq.com/).
2.  Crie uma conta ou faça login.
3.  Navegue até a seção de 
chaves de API (`API Keys`).
4.  Gere uma nova chave de API e copie-a. Cole-a no seu arquivo `.env` na variável `GROQ_API_KEY`.

### 4.2. Meta (WhatsApp, Instagram, Facebook)

Para integrar com WhatsApp, Instagram e Facebook, você precisará de uma conta no [Meta for Developers](https://developers.facebook.com/) e um aplicativo de negócios.

1.  **Crie um Aplicativo no Meta for Developers:**
    *   Acesse [Meta for Developers](https://developers.facebook.com/) e faça login.
    *   Clique em `Meus Aplicativos` e depois em `Criar Aplicativo`.
    *   Selecione o tipo de aplicativo `Negócios`.
    *   Siga as instruções para criar o aplicativo, associando-o à sua conta do Gerenciador de Negócios da Meta (se você não tiver uma, o Meta irá guiá-lo para criar).

2.  **Configure o WhatsApp Business Platform:**
    *   No painel do seu aplicativo, adicione o produto `WhatsApp`.
    *   Siga as etapas para configurar a API do WhatsApp Business, incluindo a verificação do seu número de telefone.
    *   Anote o `ID do Número de Telefone` (Phone Number ID) que será gerado. Este será o `WHATSAPP_PHONE_NUMBER_ID` no seu `.env`.
    *   Na seção `Configuração` do WhatsApp, você encontrará o `Token de Acesso Temporário`. **Este token é temporário e expira em 24 horas.** Você precisará gerar um `Token de Acesso Permanente` para produção. Para isso, siga a documentação da Meta sobre como gerar tokens de acesso de sistema ou de usuário de longa duração.
    *   Copie o `Token de Acesso Permanente` e cole-o no seu arquivo `.env` na variável `META_ACCESS_TOKEN`.
    *   Defina um `Token de Verificação` (Verify Token) de sua escolha (ex: `meu_bot_123`). Este será o `META_VERIFY_TOKEN` no seu `.env`.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/meta` (substitua `SEU_DOMINIO` pelo domínio da sua hospedagem, que será configurado mais tarde).

3.  **Configure o Instagram e Facebook Messenger:**
    *   No painel do seu aplicativo, adicione o produto `Messenger`.
    *   Para Instagram, associe sua conta profissional do Instagram ao seu aplicativo.
    *   Para Facebook, associe sua página do Facebook ao seu aplicativo.
    *   O `META_ACCESS_TOKEN` e o `META_VERIFY_TOKEN` configurados para o WhatsApp geralmente funcionam para Instagram e Facebook Messenger também, pois fazem parte do mesmo ecossistema da Meta.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/meta` também para o Messenger.

### 4.3. TikTok Business Messaging API

O TikTok exige uma conta Business e a criação de um aplicativo no portal de desenvolvedores.

1.  **Converta sua Conta TikTok para Business:**
    *   No aplicativo TikTok, vá em `Configurações e privacidade` > `Gerenciar conta` > `Mudar para Conta Business`.

2.  **Crie um Aplicativo no TikTok for Developers:**
    *   Acesse [TikTok for Developers](https://developers.tiktok.com/) e faça login.
    *   Clique em `Meus Aplicativos` e depois em `Criar Novo Aplicativo`.
    *   Siga as instruções para criar o aplicativo, selecionando as permissões necessárias para mensagens.
    *   Após a criação e aprovação do aplicativo (pode levar alguns dias), você terá acesso às credenciais do aplicativo, incluindo o `Client Key` e `Client Secret`.
    *   Você precisará gerar um `Access Token` para a API de Mensagens. O processo envolve autenticação OAuth 2.0. A documentação do TikTok for Developers detalha como obter este token. Este será o `TIKTOK_ACCESS_TOKEN` no seu `.env`.
    *   Configure o `URL do Webhook` para `https://SEU_DOMINIO/webhook/tiktok`.

## 5. Hospedagem Gratuita (Render.com)

Vamos usar o Render.com para hospedar seu chatbot gratuitamente.

1.  **Crie uma Conta no Render:**
    *   Acesse [Render.com](https://render.com/) e crie uma conta (você pode usar seu GitHub).

2.  **Crie um Novo Web Service:**
    *   No painel do Render, clique em `New` > `Web Service`.
    *   Conecte seu repositório GitHub onde você salvou o código do chatbot.
    *   **Nome:** Dê um nome ao seu serviço (ex: `meu-chatbot-ia`).
    *   **Região:** Escolha a região mais próxima de você.
    *   **Branch:** `main` (ou a branch que você estiver usando).
    *   **Root Directory:** `/` (se o seu código estiver na raiz do repositório).
    *   **Runtime:** `Python 3`.
    *   **Build Command:** `pip install -r requirements.txt`.
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`.
    *   **Plano:** Selecione o plano `Free`.

3.  **Adicione as Variáveis de Ambiente:**
    *   Na seção `Environment` do seu serviço no Render, adicione as variáveis de ambiente (`GROQ_API_KEY`, `META_ACCESS_TOKEN`, `META_VERIFY_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `TIKTOK_ACCESS_TOKEN`) com os valores que você obteve nas etapas anteriores.

4.  **Deploy:**
    *   Clique em `Create Web Service`. O Render irá construir e implantar seu aplicativo.
    *   Após o deploy, o Render fornecerá um `URL público` para o seu serviço (ex: `https://meu-chatbot-ia.onrender.com`). Este será o `SEU_DOMINIO` que você usará para configurar os webhooks na Meta e no TikTok.

## 6. Testando o Chatbot

Após configurar os webhooks nas plataformas com o URL público do Render, seu chatbot estará ativo. Envie mensagens para suas contas de WhatsApp, Instagram, Facebook e TikTok para testar as respostas da IA.

## 7. Considerações Finais

*   **Persistência de Conversa:** O código fornecido não inclui persistência de conversa. Para que a IA se lembre do contexto, você precisaria integrar um banco de dados (como SQLite ou Supabase) para armazenar o histórico de mensagens.
*   **Limites:** Fique atento aos limites da camada gratuita de cada serviço. Se o volume de mensagens for muito alto, você pode precisar fazer upgrade dos planos.
*   **Manutenção:** Monitore os logs do seu serviço no Render para identificar e corrigir possíveis erros.

---

**Autor:** Manus AI
**Data:** 22 de Abril de 2026
