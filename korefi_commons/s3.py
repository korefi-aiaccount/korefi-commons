from typing import Any
import boto3
from botocore.exceptions import ClientError
import logging
from contextlib import contextmanager
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log,
)

logger = logging.getLogger(__name__)


class S3UploadError(Exception):
    """Custom exception for S3 upload failures"""

    pass


class S3DownloadError(Exception):
    """Custom exception for S3 download failures"""

    pass


class S3Service:
    def __init__(self, config: dict):
        """
        Initialize S3 service with configuration

        Args:
            config (dict): Configuration containing:
                - bucket_name: S3 bucket name
                - aws_access_key_id: AWS access key (optional if using IAM roles)
                - aws_secret_access_key: AWS secret key (optional if using IAM roles)
                - region_name: AWS region name
                - max_retries: Maximum number of retry attempts (default: 3)
                - initial_wait_seconds: Initial wait time between retries (default: 1)
                - max_wait_seconds: Maximum wait time between retries (default: 10)
        """
        self.bucket_name = config.get("bucket_name")
        self.max_retries = config.get("max_retries", 3)
        self.initial_wait = config.get("initial_wait_seconds", 1)
        self.max_wait = config.get("max_wait_seconds", 10)

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.get("aws_access_key_id"),
            aws_secret_access_key=config.get("aws_secret_access_key"),
            region_name=config.get("region_name"),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ClientError, ConnectionError)),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG),
        reraise=True,
    )
    def upload_json(self, data: Any, file_key: str) -> bool:
        """
        Upload JSON data to S3 with retry mechanism

        Args:
            data: Data to upload (will be converted to JSON)
            file_key: S3 object key (path)

        Returns:
            bool: True if upload successful

        Raises:
            S3UploadError: If upload fails after all retries
        """
        try:
            import json

            json_data = json.dumps(data)

            # Add metadata for tracking
            metadata = {
                "ContentType": "application/json",
                "NumberOfRetries": "0",
            }

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=json_data,
                Metadata=metadata,
            )

            logger.info(f"Successfully uploaded data to {self.bucket_name}/{file_key}")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                f"S3 Client Error - Code: {error_code}, Message: {error_message}"
            )
            raise S3UploadError(f"Failed to upload to S3: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise S3UploadError(f"Unexpected error during upload: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ClientError, ConnectionError)),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG),
        reraise=True,
    )
    def download_file(self, file_key: str, local_path: str) -> bool:
        """
        Download file from S3 with retry mechanism

        Args:
            file_key: S3 object key (path)
            local_path: Local path to save file

        Returns:
            bool: True if download successful

        Raises:
            S3DownloadError: If download fails after all retries
        """
        try:
            logger.info(f"Start download {self.bucket_name} {file_key} {local_path}")
            self.s3_client.download_file(self.bucket_name, file_key, local_path)
            logger.info(f"Successfully downloaded {file_key} to {local_path}")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                f"S3 Client Error - Code: {error_code}, Message: {error_message}"
            )
            raise S3DownloadError(f"Failed to download from S3: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during S3 download: {str(e)}")
            raise S3DownloadError(f"Unexpected error during download: {str(e)}")

    def check_file_exists(self, file_key: str) -> bool:
        """Check if a file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise


@contextmanager
def s3_service(config: dict):
    """Context manager for S3 service"""
    service = S3Service(config)
    try:
        yield service
    finally:
        # Cleanup if needed
        pass
