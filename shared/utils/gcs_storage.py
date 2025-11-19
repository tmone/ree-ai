"""
Google Cloud Storage Utility for Image Upload

Handles image upload to Google Cloud Storage bucket for property images.
Supports multiple image formats and generates unique filenames.
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account

from shared.utils.logger import get_logger

logger = get_logger(__name__)


class GCSStorageClient:
    """
    Google Cloud Storage client for property image uploads.

    Usage:
        client = GCSStorageClient()
        urls = await client.upload_images(property_id, image_files)
    """

    # Supported image formats
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGES_PER_PROPERTY = 10

    def __init__(self):
        """Initialize GCS client with credentials"""
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'ree-ai-property-images')
        self.project_id = os.getenv('GCS_PROJECT_ID', '')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')

        # Initialize client
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = storage.Client(
                project=self.project_id,
                credentials=credentials
            )
            logger.info(f"GCS client initialized with credentials from {credentials_path}")
        else:
            # Try default credentials (for GKE, Cloud Run, etc.)
            try:
                self.client = storage.Client(project=self.project_id)
                logger.info("GCS client initialized with default credentials")
            except Exception as e:
                logger.warning(f"GCS client not initialized: {e}")
                self.client = None

        self._bucket = None

    @property
    def bucket(self):
        """Get or create bucket reference"""
        if self._bucket is None and self.client:
            try:
                self._bucket = self.client.bucket(self.bucket_name)
            except Exception as e:
                logger.error(f"Failed to get bucket {self.bucket_name}: {e}")
        return self._bucket

    def _validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate file before upload.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type: {ext}. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"

        # Check size
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large: {file_size / 1024 / 1024:.1f}MB. Max: {self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"

        return True, ""

    def _generate_blob_name(self, property_id: str, filename: str) -> str:
        """
        Generate unique blob name for file.

        Format: properties/{property_id}/{timestamp}_{uuid}_{filename}
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]

        # Sanitize filename
        safe_filename = ''.join(c for c in filename if c.isalnum() or c in '._-')[:50]

        return f"properties/{property_id}/{timestamp}_{unique_id}_{safe_filename}"

    async def upload_image(
        self,
        property_id: str,
        file_content: bytes,
        filename: str,
        content_type: str = None
    ) -> Optional[str]:
        """
        Upload single image to GCS.

        Args:
            property_id: Property ID for organizing storage
            file_content: Image bytes
            filename: Original filename
            content_type: MIME type (auto-detected if not provided)

        Returns:
            Public URL of uploaded image, or None if failed
        """
        if not self.bucket:
            logger.error("GCS bucket not available")
            return None

        # Validate
        is_valid, error = self._validate_file(filename, len(file_content))
        if not is_valid:
            logger.warning(f"File validation failed: {error}")
            return None

        # Auto-detect content type
        if not content_type:
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            content_type = content_type_map.get(ext, 'image/jpeg')

        # Generate blob name
        blob_name = self._generate_blob_name(property_id, filename)

        try:
            # Upload to GCS
            blob = self.bucket.blob(blob_name)

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: blob.upload_from_string(
                    file_content,
                    content_type=content_type
                )
            )

            # Make publicly accessible
            await loop.run_in_executor(None, blob.make_public)

            public_url = blob.public_url
            logger.info(f"Uploaded image to GCS: {blob_name}")

            return public_url

        except Exception as e:
            logger.error(f"Failed to upload image to GCS: {e}")
            return None

    async def upload_images(
        self,
        property_id: str,
        files: List[Tuple[bytes, str, str]]
    ) -> List[str]:
        """
        Upload multiple images to GCS.

        Args:
            property_id: Property ID
            files: List of (content, filename, content_type) tuples

        Returns:
            List of public URLs for successfully uploaded images
        """
        if len(files) > self.MAX_IMAGES_PER_PROPERTY:
            logger.warning(f"Too many images: {len(files)}. Max: {self.MAX_IMAGES_PER_PROPERTY}")
            files = files[:self.MAX_IMAGES_PER_PROPERTY]

        urls = []
        for content, filename, content_type in files:
            url = await self.upload_image(property_id, content, filename, content_type)
            if url:
                urls.append(url)

        logger.info(f"Uploaded {len(urls)}/{len(files)} images for property {property_id}")
        return urls

    async def delete_image(self, blob_name: str) -> bool:
        """
        Delete image from GCS.

        Args:
            blob_name: Full blob name (e.g., properties/{id}/filename.jpg)

        Returns:
            True if deleted successfully
        """
        if not self.bucket:
            return False

        try:
            blob = self.bucket.blob(blob_name)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.delete)
            logger.info(f"Deleted image from GCS: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete image from GCS: {e}")
            return False

    async def delete_property_images(self, property_id: str) -> int:
        """
        Delete all images for a property.

        Args:
            property_id: Property ID

        Returns:
            Number of deleted images
        """
        if not self.bucket:
            return 0

        try:
            prefix = f"properties/{property_id}/"
            loop = asyncio.get_event_loop()

            # List blobs with prefix
            blobs = await loop.run_in_executor(
                None,
                lambda: list(self.client.list_blobs(self.bucket_name, prefix=prefix))
            )

            # Delete all
            deleted = 0
            for blob in blobs:
                await loop.run_in_executor(None, blob.delete)
                deleted += 1

            logger.info(f"Deleted {deleted} images for property {property_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete property images: {e}")
            return 0

    def get_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60
    ) -> Optional[str]:
        """
        Generate signed URL for private access.

        Args:
            blob_name: Full blob name
            expiration_minutes: URL expiration time

        Returns:
            Signed URL or None
        """
        if not self.bucket:
            return None

        try:
            blob = self.bucket.blob(blob_name)
            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes),
                method='GET'
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None


# Singleton instance
_gcs_client: Optional[GCSStorageClient] = None


def get_gcs_client() -> GCSStorageClient:
    """Get singleton GCS client instance"""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSStorageClient()
    return _gcs_client
