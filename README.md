# Desafio de Ingestão e Busca com LangChain, PostgreSQL e pgVector

## Visão Geral
Este projeto realiza a ingestão de um arquivo PDF, armazena seus conteúdos em um banco vetorial PostgreSQL com extensão pgVector e permite buscas contextuais via linha de comando (CLI), respondendo apenas com base no conteúdo do PDF.

## Estrutura do Projeto
```
??? docker-compose.yml
??? requirements.txt      # Dependências
??? .env                  # Template da variável OPENAI_API_KEY/GEMINI
??? src/
?   ??? ingest.py         # Script de ingestão do PDF
?   ??? search.py         # Script de busca
?   ??? chat.py           # CLI para interação com usuário
??? document.pdf          # PDF para ingestão
??? README.md             # Instruções de execução
```

## Pré-requisitos
- Python 3.10+
- Docker (Docker Desktop ou Rancher Desktop)
- Chave de API Google Gemini

## Passos para Execução

### 1. Suba o banco de dados

#### Opção A: Docker Desktop
```powershell
docker-compose up -d
```

#### Opção B: Rancher Desktop (usando rdctl shell)
Se você usa Rancher Desktop, o comando `docker` pode não funcionar diretamente no PowerShell. Use `rdctl shell` para executar comandos Docker:

```powershell
# Criar e iniciar o container PostgreSQL com pgVector (porta 5433 para evitar conflitos)
rdctl shell docker run -d --name postgres_rag -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=rag -p 5433:5432 pgvector/pgvector:pg17

# Criar a extensão vector no banco
rdctl shell docker exec postgres_rag psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verificar se está rodando
rdctl shell docker ps --filter "name=postgres_rag"
```

> **Nota**: Se usar a porta 5433, atualize o `DATABASE_URL` no arquivo `.env` para `postgresql+psycopg://postgres:postgres@localhost:5433/rag`

### 2. Instale as dependências Python
```powershell
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:
```
GOOGLE_API_KEY=sua-chave-google
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

> **Importante**: A porta padrão é `5432`, mas se você já tem um PostgreSQL local instalado, use a porta `5433` conforme configurado no passo 1.

### 4. Ingestão do PDF
Execute o script para processar e armazenar os chunks do PDF no banco vetorial:
```powershell
python src/ingest.py
```

### 5. Teste a busca vetorial (opcional)
```powershell
python src/search.py
```
Digite uma pergunta e veja os chunks mais relevantes retornados.

### 6. Use o chat via CLI
```powershell
python src/chat.py
```
Digite sua pergunta. O sistema irá buscar no PDF e responder conforme as regras:
- Só responde com base no conteúdo do PDF.
- Se a resposta não estiver no PDF, retorna: "Não tenho informações necessárias para responder sua pergunta."

## Prompt Utilizado
O prompt enviado à LLM segue o padrão:
```
CONTEXTO:
{resultados do banco}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

## Tecnologias Utilizadas
- **Python**
- **LangChain**
- **PostgreSQL + pgVector**
- **Google Gemini** (Embeddings e LLM)
- **Docker** (Docker Desktop ou Rancher Desktop)

## Modelos Utilizados

| Função | Modelo | Observação |
|--------|--------|------------|
| **Embeddings** | `models/gemini-embedding-001` | Gera vetores para busca semântica |
| **LLM (Respostas)** | `gemini-2.5-flash-lite` | Gera respostas baseadas no contexto |

> **Importante**: Os nomes dos modelos podem mudar com o tempo. Para consultar os modelos disponíveis, execute:
> ```python
> import google.generativeai as genai
> genai.configure(api_key="SUA_CHAVE")
> # Listar modelos de embedding
> print([m.name for m in genai.list_models() if 'embed' in m.name.lower()])
> # Listar modelos de LLM
> print([m.name for m in genai.list_models() if 'gemini' in m.name.lower()])
> ```

## Observações
- O chunking do PDF é feito em blocos de 1000 caracteres com overlap de 150.
- Os embeddings são gerados via Google Gemini (`models/gemini-embedding-001`).
- O banco vetorial utiliza a coleção `pdf_chunks`.
- O sistema não responde perguntas fora do contexto do PDF.
- Se houver conflito de porta (PostgreSQL local já instalado), use a porta `5433`.