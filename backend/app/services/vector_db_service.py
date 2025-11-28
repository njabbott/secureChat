"""ChromaDB vector database service"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

from ..config import settings
from ..models.confluence import ConfluenceDocument

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for managing ChromaDB vector database"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "Confluence documents for Chat Magic RAG"},
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

        logger.info(
            f"Initialized ChromaDB service with collection: {settings.chroma_collection_name}"
        )

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def add_documents(self, documents: List[ConfluenceDocument]) -> int:
        """
        Add documents to the vector database

        Args:
            documents: List of Confluence documents

        Returns:
            Number of chunks added
        """
        try:
            total_chunks = 0

            for doc in documents:
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc.content)

                # Prepare data for ChromaDB
                ids = []
                embeddings = []
                metadatas = []
                documents_text = []

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc.id}_chunk_{i}"
                    ids.append(chunk_id)

                    # Generate embedding
                    embedding = self.get_embedding(chunk)
                    embeddings.append(embedding)

                    # Metadata
                    metadata = {
                        "document_id": doc.id,
                        "title": doc.title,
                        "space_key": doc.space_key,
                        "space_name": doc.space_name,
                        "url": doc.url,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                    if doc.author:
                        metadata["author"] = doc.author

                    metadatas.append(metadata)
                    documents_text.append(chunk)

                # Add to ChromaDB
                if ids:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        documents=documents_text,
                    )
                    total_chunks += len(ids)

            logger.info(f"Added {total_chunks} chunks from {len(documents)} documents to vector DB")
            return total_chunks

        except Exception as e:
            logger.error(f"Error adding documents to vector DB: {e}")
            raise

    def query(
        self, query_text: str, n_results: int = 5, space_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector database

        Args:
            query_text: Query text
            n_results: Number of results to return
            space_key: Optional space key to filter results

        Returns:
            List of matching documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query_text)

            # Build where clause for filtering
            where = None
            if space_key:
                where = {"space_key": space_key}

            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    result = {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                    formatted_results.append(result)

            logger.info(f"Query returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error querying vector DB: {e}")
            raise

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection
            self.client.delete_collection(name=settings.chroma_collection_name)

            # Recreate empty collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "Confluence documents for Chat Magic RAG"},
            )

            logger.info("Cleared vector database collection")

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def get_document_count(self) -> int:
        """
        Get total count of chunks in the database

        Returns:
            Number of chunks
        """
        try:
            count = self.collection.count()
            return count

        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0

    def get_spaces_summary(self) -> Dict[str, int]:
        """
        Get summary of documents per space

        Returns:
            Dictionary mapping space_key to document count
        """
        try:
            # Get all metadata
            all_docs = self.collection.get(include=["metadatas"])

            spaces = {}
            for metadata in all_docs.get("metadatas", []):
                space_key = metadata.get("space_key")
                if space_key:
                    spaces[space_key] = spaces.get(space_key, 0) + 1

            return spaces

        except Exception as e:
            logger.error(f"Error getting spaces summary: {e}")
            return {}
