"""Custom storages settings for project"""
import logging
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

    def save(self, name, content, max_length=None):
        try:
            result = super().save(name, content, max_length)
            logger.info(f"Successfully saved {name} to S3")
            return result
        except Exception as e:
            logger.error(f"Error saving {name} to S3: {str(e)}")
            raise


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
