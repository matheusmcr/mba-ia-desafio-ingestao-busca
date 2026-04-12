# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")

embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=GOOGLE_API_KEY,
    model=GOOGLE_EMBEDDING_MODEL
)
vectorstore = PGVector(
    connection=DATABASE_URL,
    embeddings=embeddings,
    collection_name=PG_VECTOR_COLLECTION_NAME
)


def search_query(query, k=10):
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results


if __name__ == "__main__":
    user_query = input("Digite sua pergunta: ")
    results = search_query(user_query)
    for i, (doc, score) in enumerate(results, 1):
        print(f"[{i}] Score: {score:.4f}\n{doc.page_content}\n---")
