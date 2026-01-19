import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from modules import evidence

PERSIST_DIRECTORY = "chroma_db"

class AIEngine:
    def __init__(self):
        # Initialize Embeddings (Local, Free)
        # using all-MiniLM-L6-v2 which is standard for CPU
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        
        # Initialize/Load Vector Store
        if os.path.exists(PERSIST_DIRECTORY):
            self.vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embeddings)
        else:
            self.vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embeddings)
            
    def ingest_file(self, filename, framework_tag="NIST"):
        """Reads file from evidence/, chunks it, and adds to ChromaDB with framework metadata"""
        file_path = os.path.join(evidence.EVIDENCE_DIR, filename)
        text = evidence.extract_text(file_path)
        
        if not text:
            return False, "Empty or unreadable file"
            
        # Split Text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(text)
        
        # Create Metadata
        metadatas = [{"source": filename, "framework": framework_tag} for _ in chunks]
        
        # Add to Vector Store
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
        # self.vector_store.persist() # Chroma 0.4+ persists automatically usually
        
        return True, f"Indexed {len(chunks)} chunks."

    def reset_db(self):
        """Clears the Vector Store"""
        if os.path.exists(PERSIST_DIRECTORY):
            # shutil.rmtree(PERSIST_DIRECTORY) # Risky on Windows if open
            self.vector_store.delete_collection()
            self.vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embeddings)
            return True
        return False

    def assess_control(self, control_text, control_spec, api_key, provider="OpenAI", model_name=None):
        """
        Queries VectorDB and asks LLM for assessment.
        Returns: {score: int, justification: str, sources: list}
        """
        if not self.vector_store:
            return {"error": "Vector Store not initialized"}
            
        # 1. Retrieve Context
        query = f"{control_text} {control_spec}"
        docs = self.vector_store.similarity_search(query, k=3)
        
        if not docs:
            return {"score": 0, "justification": "No evidence found in uploaded documents (Local Vector Store).", "sources": []}
            
        context_str = "\n\n".join([f"SOURCE ({d.metadata['source']} | Framework: {d.metadata.get('framework', 'NIST')}): {d.page_content}" for d in docs])
        sources = list(set([f"{d.metadata['source']} [{d.metadata.get('framework', 'NIST')}]" for d in docs]))
        
        # 2. Call LLM
        try:
            llm = None
            
            if provider == "OpenAI":
                llm = ChatOpenAI(
                    api_key=api_key, 
                    model=model_name if model_name else "gpt-3.5-turbo",
                    temperature=0
                )
            elif provider == "Gemini":
                llm = ChatGoogleGenerativeAI(
                    google_api_key=api_key,
                    model=model_name if model_name else "gemini-pro",
                    temperature=0,
                    convert_system_message_to_human=True
                )
            elif provider == "Perplexity":
                # Perplexity uses OpenAI-compatible endpoint
                llm = ChatOpenAI(
                    api_key=api_key,
                    base_url="https://api.perplexity.ai",
                    model=model_name if model_name else "sonar", 
                    temperature=0
                )
            elif provider == "Ollama":
                # Ollama runs locally
                # api_key here is actually the host URL (e.g. http://localhost:11434)
                llm = ChatOllama(
                    base_url=api_key if api_key else "http://localhost:11434",
                    model=model_name if model_name else "deepseek-r1",
                    temperature=0
                )
            
            if not llm:
                return {"error": f"Unsupported provider: {provider}"}
            
            prompt = f"""
            You are an expert AI Security Auditor.
            Evaluate the following control based ONLY on the provided evidence context.
            
            CONTROL: {control_text}
            SPECIFICATION: {control_spec}
            
            EVIDENCE CONTEXT:
            {context_str}
            
            TASK:
            1. Assign a Score (0 = No evidence, 1-2 = Partial, 3-4 = Good, 5 = Perfect).
            2. Provide a Justification citing the specific source file AND the framework tag identified in the context (e.g., "Found in Policy.pdf under the NIST AI RMF context...").
            
            OUTPUT FORMAT (JSON ONLY, NO MARKDOWN, NO CODE BLOCKS):
            {{
                "score": <int>,
                "justification": "<string>"
            }}
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Simple parsing (assuming model follows instruction)
            # Remove Markdown block if present
            content = content.replace("```json", "").replace("```", "").strip()
            
            import json
            result = json.loads(content)
            result['sources'] = sources
            return result
        except Exception as e:
            return {"error": str(e), "score": 0, "justification": f"LLM Error ({provider}): {str(e)}"}

    def validate_api_key(self, api_key, provider, model_name=None):
        """Attempts a very simple call to validate the API key/connection"""
        try:
            if not api_key and provider != "Ollama":
                return False, "API Key is required"
                
            if provider == "OpenAI":
                llm = ChatOpenAI(api_key=api_key, model=model_name if model_name else "gpt-3.5-turbo", max_tokens=5)
                llm.invoke([HumanMessage(content="hi")])
            elif provider == "Gemini":
                llm = ChatGoogleGenerativeAI(google_api_key=api_key, model=model_name if model_name else "gemini-pro", max_output_tokens=5)
                llm.invoke([HumanMessage(content="hi")])
            elif provider == "Perplexity":
                llm = ChatOpenAI(api_key=api_key, base_url="https://api.perplexity.ai", model=model_name if model_name else "sonar", max_tokens=5)
                llm.invoke([HumanMessage(content="hi")])
            elif provider == "Ollama":
                import urllib.request
                url = f"{api_key.rstrip('/')}/api/tags"
                with urllib.request.urlopen(url, timeout=2) as response:
                    return True, "Ollama connection successful"
            else:
                return False, f"Unsupported provider: {provider}"
                
            return True, "Key validated successfully"
        except Exception as e:
            return False, f"Validation failed: {str(e)}"

    def chat(self, user_input, context_data, api_key, provider="OpenAI", model_name=None):
        """
        General chat interface with assessment context.
        """
        # 1. Retrieve Context from docs
        docs = self.vector_store.similarity_search(user_input, k=3)
        context_str = "\n\n".join([f"SOURCE ({d.metadata['source']}): {d.page_content}" for d in docs])
        
        # 2. Build Prompt
        prompt = f"""
        You are the 'AI Security Precision Assistant'. 
        Your goal is to help the user navigate AI Security Maturity according to NIST AI RMF and CSA AICM.
        
        ASSESSMENT CONTEXT:
        {context_data}
        
        RELEVANT DOCUMENTS:
        {context_str}
        
        USER QUESTION:
        {user_input}
        
        Provide professional, concise, and technically accurate advice. 
        If specific gaps are mentioned in the context, help the user understand how to remediate them.
        """
        
        try:
            llm = None
            if provider == "OpenAI":
                llm = ChatOpenAI(api_key=api_key, model=model_name if model_name else "gpt-3.5-turbo", temperature=0.7)
            elif provider == "Gemini":
                llm = ChatGoogleGenerativeAI(google_api_key=api_key, model=model_name if model_name else "gemini-pro", temperature=0.7, convert_system_message_to_human=True)
            elif provider == "Perplexity":
                llm = ChatOpenAI(api_key=api_key, base_url="https://api.perplexity.ai", model=model_name if model_name else "sonar", temperature=0.7)
            elif provider == "Ollama":
                llm = ChatOllama(base_url=api_key, model=model_name if model_name else "deepseek-r1", temperature=0.7)
            
            if not llm:
                return "Error: Unsupported provider"
                
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"

    def list_local_models(self, base_url="http://localhost:11434"):
        """Fetches list of available models from local Ollama instance"""
        import urllib.request
        import json
        try:
            url = f"{base_url.rstrip('/')}/api/tags"
            with urllib.request.urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode())
                return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            print(f"Ollama connection error: {e}")
            return []

# Global Instance
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = AIEngine()
    return engine
