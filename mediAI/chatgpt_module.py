import os
from omegaconf import OmegaConf
import chromadb
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from .prompt_templates import *

class ChatGPT:
    def __init__(self):
        self.config = OmegaConf.load(os.path.join(os.path.dirname(__file__), "config.yaml"))
        self._initialize_model()
        self._initialize_embeddings()
        self._initialize_vector_store()

    def _initialize_model(self):
        self.model = ChatOllama(
            model=self.config.ollama.chat_model_name,
            temperature=0.0,
        )

    def _initialize_embeddings(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'}
        )

    def _initialize_vector_store(self):
        persistent_client = chromadb.PersistentClient(path=self.config.chromadb.persist_directory)
        self.vector_store = Chroma(
            collection_name=self.config.chromadb.collection_name,
            client=persistent_client,
            embedding_function=self.embeddings,
        )
        self.retriever = self.vector_store.as_retriever(
            search_type=self.config.ollama.chat_search_type,
            search_kwargs={"k": self.config.ollama.chat_search_k}
        )

    def _set_templates(self, role):
        templates = {
            "provider": (system_provider_template, human_provider_template),
            "patient": (system_patient_template, human_patient_template),
            "HSW": (system_HSW_template, human_HSW_template),
            "default": (system_default_template, human_default_template)
        }
        self.system_template, self.human_template = templates.get(role, templates["default"])

    def _set_prompt(self, role=None):
        self._set_templates(role)
        self.messages = [
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(self.human_template)
        ]
        self.chat_prompt = ChatPromptTemplate.from_messages(self.messages)

    def _set_chain(self):
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.model,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            reduce_k_below_max_tokens=True,
            max_tokens_limit=8192,
            chain_type_kwargs={"prompt": self.chat_prompt},
            verbose=False,
        )

    def get_response(self, question, role=None):
        self._set_prompt(role)
        self._set_chain()
        response = self.chain.invoke(question)
        return response["answer"], response["source_documents"]
