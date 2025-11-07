"""
Layer 2: RAG (Retrieval-Augmented Generation) System with LangChain
Integrates Pinecone vector database with OpenAI embeddings using LangChain
"""

import os
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, TextLoader
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from pinecone import Pinecone, ServerlessSpec
import time

load_dotenv()


class RAGSystem:
    """Handles vector storage and retrieval using LangChain"""
    
    def __init__(self):
        # Initialize OpenAI embeddings via LangChain
        # Using dimensions=512 to match Pinecone index dimension
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small",
            dimensions=512  # Match Pinecone index dimension
        )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "hedge-fund-knowledge")
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Vector store (will be initialized after index creation)
        self.vectorstore: Optional[PineconeVectorStore] = None
        
        # Try to connect to existing index
        try:
            self.vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            print(f"✅ Connected to existing Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"⚠️  Could not connect to index: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing unwanted characters and formatting
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove page numbers (e.g., "Page 1", "Page 12", "- 1 -", etc.)
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'-\s*\d+\s*-', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove any remaining excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def create_index(self):
        """Create a new Pinecone index if it doesn't exist"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                print(f"✅ Index '{self.index_name}' already exists")
            else:
                print(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=512,  # text-embedding-3-small with dimensions=512
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
                print(f"✅ Index '{self.index_name}' created successfully")
            
            # Initialize vector store
            self.vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            
        except Exception as e:
            print(f"❌ Error creating index: {str(e)}")
            raise
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load document using LangChain loaders
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of LangChain Document objects
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.docx':
                print(f"📄 Loading DOCX file with LangChain: {file_path}")
                loader = Docx2txtLoader(file_path)
            elif file_extension == '.txt':
                print(f"📄 Loading text file with LangChain: {file_path}")
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            documents = loader.load()
            print(f"✅ Loaded {len(documents)} document(s)")
            
            # Clean the text in each document
            print("🧹 Cleaning text (removing newlines, tabs, page numbers)...")
            for doc in documents:
                doc.page_content = self.clean_text(doc.page_content)
            
            return documents
            
        except Exception as e:
            print(f"❌ Error loading document: {str(e)}")
            raise
    
    def index_knowledge_base(self, file_path: str):
        """
        Load knowledge base from file and index using LangChain
        
        Args:
            file_path: Path to the knowledge base file (.txt or .docx)
        """
        if not self.vectorstore:
            raise Exception("Vector store not initialized. Call create_index() first.")
        
        print(f"📚 Loading and indexing knowledge base from {file_path}...")
        
        # Load documents
        documents = self.load_document(file_path)
        
        if not documents:
            raise ValueError("No documents loaded from file")
        
        # Calculate total characters
        total_chars = sum(len(doc.page_content) for doc in documents)
        print(f"✅ Loaded {total_chars} characters from {len(documents)} document(s)")
        
        # Split documents into chunks
        print("✂️  Chunking documents with LangChain RecursiveCharacterTextSplitter...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        # Add to vector store
        print("🔢 Creating embeddings and uploading to Pinecone via LangChain...")
        
        # Process in batches for progress tracking
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            self.vectorstore.add_documents(batch)
            print(f"  Uploaded {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
        
        print(f"✅ Successfully indexed {len(chunks)} chunks using LangChain")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant context from knowledge base
        
        Args:
            query: User's query
            top_k: Number of most relevant chunks to retrieve
            
        Returns:
            List of relevant text chunks with scores
        """
        if not self.vectorstore:
            print("⚠️  Vector store not initialized. Returning empty context.")
            return []
        
        try:
            # Use LangChain's similarity search with scores
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            # Format results
            contexts = []
            for i, (doc, score) in enumerate(results):
                contexts.append({
                    'text': doc.page_content,
                    'score': float(score),
                    'chunk_id': i,
                    'metadata': doc.metadata
                })
            
            return contexts
            
        except Exception as e:
            print(f"❌ Error retrieving context: {str(e)}")
            return []
    
    def get_augmented_context(self, query: str, top_k: int = 3) -> str:
        """
        Get formatted context string to augment the chatbot's knowledge
        
        Args:
            query: User's query
            top_k: Number of contexts to retrieve
            
        Returns:
            Formatted context string
        """
        contexts = self.retrieve_context(query, top_k)
        
        if not contexts:
            return ""
        
        # Format contexts into a single string
        context_str = "Relevant information from knowledge base:\n\n"
        for i, ctx in enumerate(contexts, 1):
            context_str += f"[Context {i}]:\n{ctx['text']}\n\n"
        
        return context_str
    
    def create_qa_chain(self) -> RetrievalQA:
        """
        Create a LangChain RetrievalQA chain
        
        Returns:
            RetrievalQA chain for question answering
        """
        if not self.vectorstore:
            raise Exception("Vector store not initialized")
        
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        return qa_chain
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the Pinecone index"""
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            return {
                'total_vector_count': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'index_fullness': stats.get('index_fullness', 0)
            }
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the RAG system
    rag = RAGSystem()
    
    # Get index stats
    print("\nIndex Stats:")
    print(rag.get_index_stats())
    
    # Test retrieval
    test_query = "What are some good trading strategies for momentum trading?"
    print(f"\nTest Query: {test_query}")
    print("\nRetrieved Context:")
    context = rag.get_augmented_context(test_query, top_k=2)
    print(context)
