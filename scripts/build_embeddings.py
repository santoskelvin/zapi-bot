"""Gera vetor FAISS a partir dos docs em ./docs."""
import pathlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

docs_path = pathlib.Path('docs')
chunks, metadata = [], []
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
for p in docs_path.glob('*.md'):
    text = p.read_text(encoding='utf-8')
    for c in splitter.split_text(text):
        chunks.append(c)
        metadata.append({'source': p.name})

db = FAISS.from_texts(chunks, OpenAIEmbeddings())
db.save_local('app/embeddings')
print('Embeddings gerados em app/embeddings')
