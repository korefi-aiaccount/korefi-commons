import uuid


def generate_s3uri(
    bucket_name: str, uc_uuid: str, file_category: str, file_uuid: str
) -> str:
    """Generate an S3 URI from the given components.

    Args:
        bucket_name: Name of the S3 bucket
        uc_uuid: UUID of the use case
        file_category: Category of the file
        file_uuid: UUID of the file

    Returns:
        str: Generated S3 URI

    Raises:
        ValueError: If any of the inputs are invalid
    """
    if not bucket_name:
        raise ValueError("Bucket name cannot be empty")
    if not file_category:
        raise ValueError("File category cannot be empty")

    try:
        uuid.UUID(uc_uuid)
        uuid.UUID(file_uuid)
    except ValueError:
        raise ValueError("Invalid UUID format")

    return f"s3://{bucket_name}/{uc_uuid}/{file_category}/{file_uuid}"
