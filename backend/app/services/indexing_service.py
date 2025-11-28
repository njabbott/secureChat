"""Indexing service for syncing Confluence to ChromaDB"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict

from .confluence_service import ConfluenceService
from .vector_db_service import VectorDBService
from .pii_service import PIIService
from ..models.indexing import IndexingStatus, IndexingProgress, IndexingStatusEnum
from ..models.confluence import ConfluenceSpace, ConfluenceDocument

logger = logging.getLogger(__name__)


class IndexingService:
    """Service for managing Confluence indexing with progress tracking"""

    def __init__(
        self,
        confluence_service: ConfluenceService,
        vector_db_service: VectorDBService,
        pii_service: PIIService = None,
    ):
        """
        Initialize indexing service

        Args:
            confluence_service: Confluence service instance
            vector_db_service: Vector DB service instance
            pii_service: PII service instance (optional)
        """
        self.confluence = confluence_service
        self.vector_db = vector_db_service
        self.pii_service = pii_service

        # Progress tracking
        self.current_progress: Optional[IndexingProgress] = None
        self.last_indexed: Optional[datetime] = None
        self.is_indexing: bool = False

        # PII statistics
        self.last_pii_filtered: int = 0
        self.last_pii_by_type: Dict[str, int] = {}

        logger.info("Initialized indexing service")

    async def start_indexing(self) -> bool:
        """
        Start the indexing process

        Returns:
            True if indexing started successfully, False if already in progress
        """
        if self.is_indexing:
            logger.warning("Indexing already in progress")
            return False

        self.is_indexing = True
        self.current_progress = IndexingProgress(
            status=IndexingStatusEnum.IN_PROGRESS,
            current_space=None,
            total_spaces=0,
            processed_spaces=0,
            total_documents=0,
            processed_documents=0,
            current_message="Starting indexing process...",
        )

        # Run indexing in background
        asyncio.create_task(self._run_indexing())

        return True

    async def _run_indexing(self):
        """Run the actual indexing process"""
        try:
            logger.info("Starting Confluence indexing...")

            # Step 1: Fetch all spaces
            self._update_progress(current_message="Fetching Confluence spaces...")
            spaces = self.confluence.get_all_spaces()

            self.current_progress.total_spaces = len(spaces)
            self.current_progress.current_message = f"Found {len(spaces)} spaces to index"
            logger.info(f"Found {len(spaces)} Confluence spaces")

            # Step 2: Clear existing data (optional - could be made configurable)
            self._update_progress(current_message="Clearing existing index...")
            self.vector_db.clear_collection()

            # Step 3: Index each space
            total_documents_indexed = 0
            total_pii_filtered = 0
            pii_by_type: Dict[str, int] = {}

            for space in spaces:
                if not self.is_indexing:
                    # Indexing was cancelled
                    self._update_progress(
                        status=IndexingStatusEnum.FAILED,
                        current_message="Indexing cancelled",
                        error_message="Indexing was cancelled by user",
                    )
                    return

                self._update_progress(
                    current_space=space.name,
                    current_message=f"Indexing space: {space.name}...",
                )

                # Fetch documents from this space
                documents = self.confluence.get_space_documents(space.key)
                logger.info(f"Retrieved {len(documents)} documents from space {space.key}")

                if documents:
                    # Filter PII from documents if PII service is available
                    if self.pii_service:
                        self._update_progress(
                            current_message=f"Filtering PII from {len(documents)} documents in {space.name}..."
                        )

                        filtered_documents = []
                        for doc in documents:
                            anonymized_content, pii_info = self.pii_service.detect_and_anonymize(
                                doc.content,
                                replacement_text="[PII redacted]"
                            )

                            # Track PII statistics
                            if pii_info.total_count > 0:
                                total_pii_filtered += pii_info.total_count
                                for entity_type, count in pii_info.entities.items():
                                    pii_by_type[entity_type] = pii_by_type.get(entity_type, 0) + count

                            # Create new document with filtered content
                            filtered_doc = ConfluenceDocument(
                                id=doc.id,
                                title=doc.title,
                                space_key=doc.space_key,
                                space_name=doc.space_name,
                                content=anonymized_content,
                                url=doc.url,
                                author=doc.author
                            )
                            filtered_documents.append(filtered_doc)

                        documents = filtered_documents

                        # Update progress with PII stats
                        self.current_progress.total_pii_filtered = total_pii_filtered
                        self.current_progress.pii_by_type = pii_by_type

                        logger.info(f"Filtered {total_pii_filtered} PII items from documents")

                    # Add documents to vector DB
                    self._update_progress(
                        current_message=f"Adding {len(documents)} documents from {space.name} to vector database..."
                    )

                    chunks_added = self.vector_db.add_documents(documents)
                    total_documents_indexed += len(documents)

                    logger.info(
                        f"Added {chunks_added} chunks from {len(documents)} documents"
                    )

                # Update progress
                self.current_progress.processed_spaces += 1
                self.current_progress.processed_documents = total_documents_indexed

            # Indexing completed successfully
            self.last_indexed = datetime.utcnow()
            self.last_pii_filtered = total_pii_filtered
            self.last_pii_by_type = pii_by_type

            completion_message = f"Indexing completed! Indexed {total_documents_indexed} documents from {len(spaces)} spaces."
            if total_pii_filtered > 0:
                completion_message += f" Filtered {total_pii_filtered} PII items."

            self._update_progress(
                status=IndexingStatusEnum.COMPLETED,
                current_message=completion_message,
            )

            logger.info(
                f"Indexing completed successfully. Total documents: {total_documents_indexed}, PII filtered: {total_pii_filtered}"
            )

        except Exception as e:
            logger.error(f"Error during indexing: {e}", exc_info=True)
            self._update_progress(
                status=IndexingStatusEnum.FAILED,
                current_message="Indexing failed",
                error_message=str(e),
            )

        finally:
            self.is_indexing = False

    def _update_progress(
        self,
        status: Optional[IndexingStatusEnum] = None,
        current_space: Optional[str] = None,
        current_message: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Update indexing progress"""
        if not self.current_progress:
            return

        if status:
            self.current_progress.status = status
        if current_space is not None:
            self.current_progress.current_space = current_space
        if current_message:
            self.current_progress.current_message = current_message
        if error_message:
            self.current_progress.error_message = error_message

    def get_progress(self) -> Optional[IndexingProgress]:
        """Get current indexing progress"""
        return self.current_progress

    def get_status(self) -> IndexingStatus:
        """Get indexing status and metadata"""
        # Get document count from vector DB
        total_documents = self.vector_db.get_document_count()

        # Get spaces summary
        spaces_summary = self.vector_db.get_spaces_summary()
        total_spaces = len(spaces_summary)

        status = IndexingStatus(
            last_indexed=self.last_indexed,
            is_indexing=self.is_indexing,
            total_documents=total_documents,
            total_spaces=total_spaces,
            progress=self.current_progress if self.is_indexing else None,
            last_pii_filtered=self.last_pii_filtered,
            last_pii_by_type=self.last_pii_by_type,
        )

        return status

    def stop_indexing(self):
        """Stop the indexing process"""
        if self.is_indexing:
            logger.info("Stopping indexing process...")
            self.is_indexing = False
            self._update_progress(
                status=IndexingStatusEnum.FAILED,
                current_message="Indexing stopped by user",
            )
