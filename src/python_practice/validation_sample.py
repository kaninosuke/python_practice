from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError
from .utils import JsonValidator

# Note: EmailStr requires the 'email-validator' package. 
# For this sample, we'll use a regular str with a regex if email-validator is not installed.
# But since Pydantic is already installed, let's just use regular field constraints for simplicity 
# or assume the user might install it later. Let's use a regex for robustness in this environment.

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., gt=0)
    tags: List[str] = Field(default_factory=list)

class Order(BaseModel):
    order_id: str = Field(..., pattern=r"^[A-Z]{2}-\d{4}$")  # e.g., AB-1234
    customer_email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    items: List[Product]
    order_date: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=1, ge=1, le=5)
    discount_code: Optional[str] = None

    @field_validator("items")
    @classmethod
    def must_have_items(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v

    @field_validator("discount_code")
    @classmethod
    def check_discount_code(cls, v):
        if v and not v.isalnum():
            raise ValueError("Discount code must be alphanumeric")
        return v

class PartialRequiredModel(BaseModel):
    item1: str = Field(..., description="Required item 1")
    item2: str = Field(..., description="Required item 2")
    item3: str = Field(..., description="Required item 3")
    item4: Optional[str] = Field(None, description="Optional item 4")
    item5: Optional[str] = Field(None, description="Optional item 5")
    item6: Optional[str] = Field(None, description="Optional item 6")
    item7: Optional[str] = Field(None, description="Optional item 7")

class ComprehensiveModel(BaseModel):
    required_str: str = Field(..., description="必須チェック (Required)")
    length_str: str = Field(..., min_length=3, max_length=10, description="文字数チェック (Length: 3-10)")
    text_data: str = Field(..., description="text型 (String)")
    number_data: int = Field(..., ge=0, le=100, description="数字型 (Integer: 0-100)")
    date_data: datetime = Field(..., description="datetime型 (Datetime)")
    regex_str: str = Field(..., pattern=r"^[A-Z]{3}-\d{3}$", description="正規表現チェック (Regex: AAA-111)")

def run_validation_samples():
    print("=== Pydantic Validation Samples ===\n")

    # 1. Valid Data
    valid_data = {
        "order_id": "OR-2024",
        "customer_email": "alice@example.com",
        "items": [
            {"name": "Laptop", "price": 1200.50, "tags": ["electronics", "work"]},
            {"name": "Mouse", "price": 25.0}
        ],
        "priority": 3,
        "discount_code": "SUMMER24"
    }

    print("--- Sample 1: Valid Data ---")
    try:
        order = JsonValidator.validate(Order, valid_data)
        print(f"Successfully validated order: {order.order_id}")
        print(f"Total items: {len(order.items)}")
        for item in order.items:
            print(f"  - {item.name}: ${item.price}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # 2. Invalid Data (Multiple errors)
    invalid_data = {
        "order_id": "invalid-id",          # Regex mismatch
        "customer_email": "bad-email",     # Regex mismatch
        "items": [],                       # Custom validator fails (empty list)
        "priority": 10,                    # Range error (max 5)
        "discount_code": "!!!ERROR!!!"     # Custom validator fails (not alphanumeric)
    }

    print("\n--- Sample 2: Invalid Data (Multiple Errors) ---")
    try:
        JsonValidator.validate(Order, invalid_data)
    except ValidationError as e:
        print("Validation failed as expected with the following errors:")
        for error in e.errors():
            loc = " -> ".join(map(str, error['loc']))
            print(f"  [{loc}]: {error['msg']}")

    # 3. Invalid Price in Nested Object
    nested_invalid_data = {
        "order_id": "OR-9999",
        "customer_email": "bob@example.com",
        "items": [
            {"name": "Freebie", "price": -10.0}  # Price must be > 0
        ]
    }

    print("\n--- Sample 3: Invalid Nested Data ---")
    try:
        JsonValidator.validate(Order, nested_invalid_data)
    except ValidationError as e:
        print("Validation failed for nested item:")
        for error in e.errors():
            loc = " -> ".join(map(str, error['loc']))
            print(f"  [{loc}]: {error['msg']}")

    # 4. Partially Required Model (3 out of 7 required)
    print("\n--- Sample 4: Partially Required Model (3/7 required) ---")
    
    # Valid: Only 3 required items
    valid_partial = {
        "item1": "Required A",
        "item2": "Required B",
        "item3": "Required C"
    }
    
    # Valid: All 7 items
    valid_full = {
        "item1": "A", "item2": "B", "item3": "C",
        "item4": "D", "item5": "E", "item6": "F", "item7": "G"
    }
    
    # Invalid: Missing one required item
    invalid_partial = {
        "item1": "Only A",
        "item2": "Only B"
        # item3 is missing
    }

    try:
        obj1 = JsonValidator.validate(PartialRequiredModel, valid_partial)
        print("Successfully validated with only 3 required fields.")
        
        obj2 = JsonValidator.validate(PartialRequiredModel, valid_full)
        print("Successfully validated with all 7 fields.")
        
        print("Attempting to validate with missing required field (item3)...")
        JsonValidator.validate(PartialRequiredModel, invalid_partial)
    except ValidationError as e:
        print("Validation failed as expected for Sample 4:")
        for error in e.errors():
            loc = " -> ".join(map(str, error['loc']))
            print(f"  [{loc}]: {error['msg']}")

    # 5. Comprehensive Validation (Required, Length, Type, Regex)
    print("\n--- Sample 5: Comprehensive Validation ---")
    
    valid_comprehensive = {
        "required_str": "I am here",
        "length_str": "12345",
        "text_data": "Some long text content here",
        "number_data": 42,
        "date_data": "2024-04-20T10:00:00",
        "regex_str": "ABC-123"
    }
    
    invalid_comprehensive = {
        # "required_str" is missing
        "length_str": "a",                # Too short (min 3)
        "text_data": 123,                 # Wrong type (should be str, though Pydantic might coerce)
        "number_data": 150,               # Out of range (max 100)
        "date_data": "invalid-date",      # Not a datetime
        "regex_str": "abc-123"            # Case mismatch (pattern expects upper)
    }

    try:
        print("Validating comprehensive data...")
        obj = JsonValidator.validate(ComprehensiveModel, valid_comprehensive)
        print("Successfully validated comprehensive data:")
        print(f"  - Date: {obj.date_data}")
        print(f"  - Number: {obj.number_data}")
        
        print("\nValidating invalid comprehensive data...")
        JsonValidator.validate(ComprehensiveModel, invalid_comprehensive)
    except ValidationError as e:
        print("Validation failed as expected for Sample 5 with multiple errors:")
        for error in e.errors():
            loc = " -> ".join(map(str, error['loc']))
            print(f"  [{loc}]: {error['msg']}")

if __name__ == "__main__":
    run_validation_samples()
