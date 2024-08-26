import logging
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

    def __init__(self, *args, **kwargs):
        logger.info(f"Initializing StaticStorage with location: {self.location}")
        logger.info(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
        logger.info(f"AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
        super().__init__(*args, **kwargs)

    def save(self, name, content, max_length=None):
        logger.info(f"Attempting to save {name} to S3")
        try:
            result = super().save(name, content, max_length)
            logger.info(f"Successfully saved {name} to S3")
            return result
        except Exception as e:
            logger.error(f"Error saving {name} to S3: {str(e)}")
            raise

class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION