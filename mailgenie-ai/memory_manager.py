from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os

class MemoryManager:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        if os.path.exists("memory_db/index.faiss"):
            self.db = FAISS.load_local("memory_db", embeddings, allow_dangerous_deserialization=True)
        else:
            dummy_doc = [Document(page_content="Welcome to MailGenie!", metadata={"name": "system"})]
            self.db = FAISS.from_documents(dummy_doc, embeddings)
            self.db.save_local("memory_db")

    def save_interaction(self, name, message):
        doc = Document(page_content=message, metadata={"name": name})
        self.db.add_documents([doc])
        self.db.save_local("memory_db")

    def get_similar(self, query):
        return self.db.similarity_search(query)
