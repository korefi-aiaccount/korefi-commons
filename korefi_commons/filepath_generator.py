def filepath_generator(file_uuid: str, file_category: str, uc_uuid: str) -> str:
    # Validate inputs
    if not file_uuid:
        raise ValueError("file_uuid cannot be empty")
    if not file_category:
        raise ValueError("file_category cannot be empty")
    if not uc_uuid:
        raise ValueError("uc_uuid cannot be empty")

    # Generate path
    return f"{uc_uuid}/{file_category}/{file_uuid}"
