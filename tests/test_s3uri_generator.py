import pytest
from korefi_commons.s3uri_generator import generate_s3uri

def test_generate_s3uri():
    bucket_name = "test-bucket"
    uc_uuid = "123e4567-e89b-12d3-a456-426614174000"
    file_category = "documents"
    file_uuid = "987fcdeb-51a2-43d7-9876-543210987654"
    
    expected_uri = f"s3://{bucket_name}/{uc_uuid}/{file_category}/{file_uuid}"
    result = generate_s3uri(bucket_name, uc_uuid, file_category, file_uuid)
    
    assert result == expected_uri

def test_generate_s3uri_with_empty_category():
    bucket_name = "test-bucket"
    uc_uuid = "123e4567-e89b-12d3-a456-426614174000"
    file_category = ""
    file_uuid = "987fcdeb-51a2-43d7-9876-543210987654"
    
    with pytest.raises(ValueError):
        generate_s3uri(bucket_name, uc_uuid, file_category, file_uuid)

def test_generate_s3uri_with_invalid_bucket():
    bucket_name = ""
    uc_uuid = "123e4567-e89b-12d3-a456-426614174000"
    file_category = "documents"
    file_uuid = "987fcdeb-51a2-43d7-9876-543210987654"
    
    with pytest.raises(ValueError):
        generate_s3uri(bucket_name, uc_uuid, file_category, file_uuid)

def test_generate_s3uri_with_invalid_uuid():
    bucket_name = "test-bucket"
    uc_uuid = "invalid-uuid"
    file_category = "documents"
    file_uuid = "987fcdeb-51a2-43d7-9876-543210987654"
    
    with pytest.raises(ValueError):
        generate_s3uri(bucket_name, uc_uuid, file_category, file_uuid) 