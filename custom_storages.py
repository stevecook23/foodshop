from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    

import logging
logger = logging.getLogger(__name__)

class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    
def __init__(self, *args, **kwargs):
    logger.info(f"Initializing StaticStorage with location: {self.location}")
    super().__init__(*args, **kwargs)

def save(self, name, content, max_length=None):
    logger.info(f"Attempting to save {name} to S3")
    return super().save(name, content, max_length)