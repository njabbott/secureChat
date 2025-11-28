"""Confluence API integration service"""

import logging
from typing import List, Optional
from atlassian import Confluence
from bs4 import BeautifulSoup

from ..config import settings
from ..models.confluence import ConfluenceSpace, ConfluenceDocument

logger = logging.getLogger(__name__)


class ConfluenceService:
    """Service for interacting with Confluence API"""

    def __init__(self):
        """Initialize Confluence client"""
        # For Atlassian Cloud, use email as username with API token
        self.confluence = Confluence(
            url=settings.confluence_base_url,
            username=settings.confluence_email,
            password=settings.confluence_api_key,
        )
        logger.info(f"Initialized Confluence service for {settings.confluence_base_url} with user {settings.confluence_email}")

    def get_all_spaces(self) -> List[ConfluenceSpace]:
        """
        Fetch all Confluence spaces

        Returns:
            List of ConfluenceSpace objects
        """
        try:
            spaces_data = self.confluence.get_all_spaces(start=0, limit=100)
            spaces = []

            for space_data in spaces_data.get("results", []):
                space = ConfluenceSpace(
                    key=space_data.get("key"),
                    name=space_data.get("name"),
                    type=space_data.get("type"),
                    url=f"{settings.confluence_base_url}/wiki/spaces/{space_data.get('key')}",
                    document_count=0,  # Will be updated when we count documents
                )
                spaces.append(space)

            logger.info(f"Retrieved {len(spaces)} Confluence spaces")
            return spaces

        except Exception as e:
            logger.error(f"Error fetching Confluence spaces: {e}")
            raise

    def get_space_content_count(self, space_key: str) -> int:
        """
        Get the count of pages/documents in a space

        Args:
            space_key: The space key

        Returns:
            Number of pages in the space
        """
        try:
            # Get all content in the space
            content = self.confluence.get_all_pages_from_space(
                space=space_key, start=0, limit=1, expand="version"
            )
            return content.get("size", 0)

        except Exception as e:
            logger.error(f"Error counting documents in space {space_key}: {e}")
            return 0

    def get_space_documents(self, space_key: str, limit: int = 1000) -> List[ConfluenceDocument]:
        """
        Fetch all documents/pages from a Confluence space

        Args:
            space_key: The space key
            limit: Maximum number of documents to fetch

        Returns:
            List of ConfluenceDocument objects
        """
        try:
            documents = []
            start = 0
            batch_size = 50

            while start < limit:
                pages = self.confluence.get_all_pages_from_space(
                    space=space_key,
                    start=start,
                    limit=batch_size,
                    expand="body.storage,version,space",
                )

                if not pages:
                    break

                for page in pages:
                    # Extract text content from HTML
                    content_html = page.get("body", {}).get("storage", {}).get("value", "")
                    content_text = self._extract_text_from_html(content_html)

                    # Get space info
                    space_info = page.get("space", {})
                    space_name = space_info.get("name", space_key)

                    # Create document object
                    doc = ConfluenceDocument(
                        id=page.get("id"),
                        title=page.get("title"),
                        space_key=space_key,
                        space_name=space_name,
                        content=content_text,
                        url=f"{settings.confluence_base_url}/wiki{page.get('_links', {}).get('webui', '')}",
                        author=page.get("version", {}).get("by", {}).get("displayName"),
                    )
                    documents.append(doc)

                # Check if we've retrieved all pages
                if len(pages) < batch_size:
                    break

                start += batch_size

            logger.info(f"Retrieved {len(documents)} documents from space {space_key}")
            return documents

        except Exception as e:
            logger.error(f"Error fetching documents from space {space_key}: {e}")
            return []

    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content

        Args:
            html_content: HTML string

        Returns:
            Plain text content
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return html_content  # Return raw HTML if parsing fails

    def search_confluence(self, query: str, limit: int = 10) -> List[ConfluenceDocument]:
        """
        Search Confluence for documents matching a query

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching ConfluenceDocument objects
        """
        try:
            results = self.confluence.cql(
                cql=f'type=page AND text ~ "{query}"', limit=limit, expand="body.storage,space"
            )

            documents = []
            for result in results.get("results", []):
                content_html = result.get("body", {}).get("storage", {}).get("value", "")
                content_text = self._extract_text_from_html(content_html)

                space_info = result.get("space", {})
                space_key = space_info.get("key", "")
                space_name = space_info.get("name", space_key)

                doc = ConfluenceDocument(
                    id=result.get("id"),
                    title=result.get("title"),
                    space_key=space_key,
                    space_name=space_name,
                    content=content_text,
                    url=f"{settings.confluence_base_url}/wiki{result.get('_links', {}).get('webui', '')}",
                )
                documents.append(doc)

            logger.info(f"Found {len(documents)} documents matching query: {query}")
            return documents

        except Exception as e:
            logger.error(f"Error searching Confluence: {e}")
            return []
