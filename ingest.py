import os
import warnings
# Suppress the PyTorch torchvision warning messages cleanly
warnings.filterwarnings("ignore", category=UserWarning)

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

print("⏳ Scanning folder and indexing multiple files...")

# 1. Load ALL text files inside the 'source_documents' directory
# glob="**/*.txt" tells it to look for any file ending in .txt inside the folder
loader = DirectoryLoader("source_documents", glob="**/*.txt", loader_cls=TextLoader)
documents = loader.load()

print(f"📄 Found and loaded {len(documents)} file(s).")

# 2. Split the accumulated text into searchable paragraph chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
chunks = text_splitter.split_documents(documents)

# 3. Initialize the free local embeddings framework
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Clear out the old database directory if it exists to avoid duplicate data pollution
if os.path.exists("chroma_db"):
    import shutil
    shutil.rmtree("chroma_db")

# 5. Save chunks to the persistent local vector database folder
db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")

print("✅ Success! Your multi-file database is rebuilt inside 'chroma_db/'.")
