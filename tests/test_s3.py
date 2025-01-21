import pytest
import json
from unittest.mock import patch
from botocore.exceptions import ClientError
from korefi_commons.s3 import S3Service, S3UploadError, S3DownloadError


@pytest.fixture
def s3_service():
    with patch("korefi_commons.s3.boto3.client") as mock_client:
        config = {"bucket_name": "test-bucket", "region_name": "us-east-1"}
        service = S3Service(config)
        service.s3_client = mock_client.return_value
        return service


def test_upload_json_success(s3_service):
    data = {"test": "data"}
    file_key = "test/file.json"

    assert s3_service.upload_json(data, file_key) is True
    s3_service.s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=file_key,
        Body=json.dumps(data),
        Metadata={"ContentType": "application/json", "NumberOfRetries": "0"},
    )


def test_upload_json_client_error(s3_service):
    error_response = {"Error": {"Code": "500", "Message": "Test error"}}
    s3_service.s3_client.put_object.side_effect = ClientError(
        error_response, "PutObject"
    )

    with pytest.raises(S3UploadError):
        s3_service.upload_json({"test": "data"}, "test/file.json")


def test_download_file_success(s3_service):
    file_key = "test/file.pdf"
    local_path = "/tmp/test.pdf"
    s3_service.s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": file_key}]
    }

    assert s3_service.download_file(file_key, local_path) is True
    s3_service.s3_client.download_file.assert_called_once_with(
        "test-bucket", file_key, local_path
    )


def test_download_file_not_found(s3_service):
    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    s3_service.s3_client.download_file.side_effect = ClientError(
        error_response, "GetObject"
    )

    with pytest.raises(S3DownloadError):
        s3_service.download_file("test/nonexistent.pdf", "/tmp/test.pdf")


def test_check_file_exists(s3_service):
    s3_service.s3_client.head_object.return_value = {}
    assert s3_service.check_file_exists("test/file.pdf") is True

    s3_service.s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
    )
    assert s3_service.check_file_exists("test/nonexistent.pdf") is False
