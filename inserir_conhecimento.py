import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

# 1. Carrega as chaves do seu arquivo .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: Chaves do Supabase não encontradas no .env")
    exit()

# 2. Conecta ao Supabase e baixa o modelo de IA Local (Totalmente Grátis)
print("🔄 Inicializando sistemas...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer('all-MiniLM-L6-v2') # Gera vetores de tamanho 384

# 3. Função para ler o arquivo de texto e dividir em blocos
def processar_documento(caminho_arquivo: str, tamanho_bloco: int = 600):
    print(f"📖 Lendo o arquivo: {caminho_arquivo}")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        texto_completo = f.read()
        
    # Divide o texto grande em pequenos "chunks" (blocos) para a IA pesquisar melhor
    blocos = [texto_completo[i:i + tamanho_bloco] for i in range(0, len(texto_completo), tamanho_bloco)]
    return blocos

# 4. Função para inserir os blocos no Supabase
def inserir_na_base(caminho_arquivo: str):
    blocos = processar_documento(caminho_arquivo)
    print(f"🧠 Gerando embeddings para {len(blocos)} blocos. Isso pode levar alguns segundos...")
    
    for i, bloco in enumerate(blocos):
        if len(bloco.strip()) < 20: 
            continue # Ignora blocos vazios ou muito curtos
            
        embedding = model.encode(bloco).tolist()
        
        supabase.table("knowledge_base").insert({
            "content": bloco.strip(),
            "embedding": embedding
        }).execute()
        print(f"✅ Bloco {i+1}/{len(blocos)} salvo na nuvem!")

if __name__ == "__main__":
    # Nome do seu arquivo de contexto em texto
    arquivo_alvo = "contexto de conhecimento do bot.txt"
    
    if os.path.exists(arquivo_alvo):
        inserir_na_base(arquivo_alvo)
        print("🎉 SUCESSO! Arquivo lido e inserido no Supabase.")
    else:
        print(f"❌ Arquivo '{arquivo_alvo}' não encontrado na pasta do projeto!")