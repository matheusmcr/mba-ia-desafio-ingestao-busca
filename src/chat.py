# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from search import search_query

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informacao nao estiver explicitamente no CONTEXTO, responda:
  "Nao tenho informacoes necessarias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opinioes ou interpretacoes alem do que esta escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual e a capital da Franca?"
Resposta: "Nao tenho informacoes necessarias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Nao tenho informacoes necessarias para responder sua pergunta."

Pergunta: "Voce acha isso bom ou ruim?"
Resposta: "Nao tenho informacoes necessarias para responder sua pergunta."

PERGUNTA DO USUARIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUARIO"
"""

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model="gemini-2.5-flash-lite")


def montar_prompt(contexto, pergunta):
    return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)


def main():
    print("Faca sua pergunta:")
    while True:
        pergunta = input("PERGUNTA: ")
        if not pergunta.strip():
            break
        resultados = search_query(pergunta)
        contexto = "\n\n".join([doc.page_content for doc, _ in resultados])
        prompt = montar_prompt(contexto, pergunta)
        resposta = llm.invoke(prompt).content.strip()
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
