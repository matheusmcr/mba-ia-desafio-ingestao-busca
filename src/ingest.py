# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def ingest_pdf():
    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"PDF carregado com {len(documents)} paginas.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    docs = splitter.split_documents(documents)
    print(f"Documento dividido em {len(docs)} chunks.")

    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=GOOGLE_API_KEY,
        model=GOOGLE_EMBEDDING_MODEL
    )

    vectorstore = PGVector(
        connection=DATABASE_URL,
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME
    )

    vectorstore.add_documents(docs)
    print(f"Ingestao concluida: {len(docs)} chunks salvos no banco de dados.")


if __name__ == "__main__":
    ingest_pdf()
