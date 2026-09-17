import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

print("⏳ Slicing and indexing your text file...")

# 1. Load the raw text file
loader = TextLoader("knowledge.txt")
documents = loader.load()

# 2. Split it into readable paragraph chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = text_splitter.split_documents(documents)

# 3. Download a free, tiny model to generate text embedding vectors locally
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Save everything into a local database directory
db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")

print("✅ Success! Your 'chroma_db/' folder is ready.")
