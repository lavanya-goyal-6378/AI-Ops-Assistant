from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCS_PATH   = 'data/knowledge_base'
CHROMA_PATH = 'chroma_db'

def build_knowledge_base():
    print('Loading documents...')

    #loads all .txt files
    loader = DirectoryLoader(DOCS_PATH, glob='**/*.txt', loader_cls=TextLoader)
    documents = loader.load()
    print(f'Loaded {len(documents)} documents')

    #splitting into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f'Split into {len(chunks)} chunks')

    #embedding and storing in chroma DB
    embeddings = HuggingFaceEmbeddings(
        model_name='all-MiniLM-L6-v2'
    )
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f'Done! Stored {len(chunks)} chunks in chroma_db/')
    return db

def load_knowledge_base():
    embeddings = HuggingFaceEmbeddings(
        model_name='all-MiniLM-L6-v2'
    )
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

if __name__ == '__main__':
    build_knowledge_base()