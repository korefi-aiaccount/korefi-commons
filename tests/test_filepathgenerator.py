import pytest
from korefi_commons.filepath_generator import filepath_generator

def test_filepath_generator():
    assert filepath_generator(
        file_uuid="abc123",
        file_category="images", 
        uc_uuid="xyz789"
    ) == "xyz789/images/abc123"

    assert filepath_generator(
        file_uuid="def456",
        file_category="docs",
        uc_uuid="xyz789"
    ) == "xyz789/docs/def456"

def test_filepath_generator_empty_values():
    with pytest.raises(ValueError):
        filepath_generator(file_uuid="", file_category="images", uc_uuid="xyz789")
    
    with pytest.raises(ValueError):
        filepath_generator(file_uuid="abc123", file_category="", uc_uuid="xyz789")
        
    with pytest.raises(ValueError):
        filepath_generator(file_uuid="abc123", file_category="images", uc_uuid="")