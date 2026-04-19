import pytest
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from python_practice.utils.json_validator import JsonValidator

class MockModel(BaseModel):
    id: int
    name: str = Field(..., min_length=2)

def test_validate_dict_success():
    data = {"id": 1, "name": "Test"}
    result = JsonValidator.validate(MockModel, data)
    assert result.id == 1
    assert result.name == "Test"
    assert isinstance(result, MockModel)

def test_validate_json_string_success():
    data = '{"id": 2, "name": "JSON"}'
    result = JsonValidator.validate(MockModel, data)
    assert result.id == 2
    assert result.name == "JSON"

def test_validate_invalid_data_types():
    data = {"id": "not_an_int", "name": "Test"}
    with pytest.raises(ValidationError):
        JsonValidator.validate(MockModel, data)

def test_validate_invalid_constraints():
    data = {"id": 3, "name": "A"}  # Too short
    with pytest.raises(ValidationError):
        JsonValidator.validate(MockModel, data)

def test_validate_invalid_json_string():
    data = '{"id": 4, name: "Missing quotes"}'
    with pytest.raises(ValueError, match="Invalid JSON string"):
        JsonValidator.validate(MockModel, data)

def test_is_valid_true():
    data = {"id": 5, "name": "Valid"}
    assert JsonValidator.is_valid(MockModel, data) is True

def test_is_valid_false():
    data = {"id": "invalid", "name": "Valid"}
    assert JsonValidator.is_valid(MockModel, data) is False

class ComprehensiveModel(BaseModel):
    required_str: str = Field(..., description="必須チェック (Required)")
    length_str: str = Field(..., min_length=3, max_length=10, description="文字数チェック (Length: 3-10)")
    text_data: str = Field(..., description="text型 (String)")
    number_data: int = Field(..., ge=0, le=100, description="数字型 (Integer: 0-100)")
    date_data: datetime = Field(..., description="datetime型 (Datetime)")
    regex_str: str = Field(..., pattern=r"^[A-Z]{3}-\d{3}$", description="正規表現チェック (Regex: AAA-111)")

def test_comprehensive_validation_errors():
    """
    Test various validation errors and document the error messages.
    """
    invalid_data = {
        # "required_str" is missing
        # Expected Error Message: "Field required"
        
        "length_str": "a",
        # Expected Error Message: "String should have at least 3 characters"
        
        "text_data": {"not": "a string"}, 
        # Expected Error Message: "Input should be a valid string"
        
        "number_data": 150,
        # Expected Error Message: "Input should be less than or equal to 100"
        
        "date_data": "invalid-date",
        # Expected Error Message: "Input should be a valid datetime or date, invalid character in year"
        
        "regex_str": "abc-123"
        # Expected Error Message: "String should match pattern '^[A-Z]{3}-\d{3}$'"
    }

    with pytest.raises(ValidationError) as exc_info:
        JsonValidator.validate(ComprehensiveModel, invalid_data)
    
    errors = exc_info.value.errors()
    error_messages = {err['loc'][0]: err['msg'] for err in errors}
    
    # Verify that each field triggered its expected error
    assert "required_str" in error_messages
    assert "Field required" in error_messages["required_str"]
    
    assert "length_str" in error_messages
    assert "at least 3 characters" in error_messages["length_str"]
    
    assert "text_data" in error_messages
    assert "valid string" in error_messages["text_data"]
    
    assert "number_data" in error_messages
    assert "less than or equal to 100" in error_messages["number_data"]
    
    assert "date_data" in error_messages
    assert "valid datetime" in error_messages["date_data"]
    
    assert "regex_str" in error_messages
    assert "match pattern" in error_messages["regex_str"]
