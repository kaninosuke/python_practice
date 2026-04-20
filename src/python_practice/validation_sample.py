from datetime import datetime
from pydantic import ValidationError
from .utils import JsonValidator
from .models import Product, Order, PartialRequiredModel, ComprehensiveModel

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

    # 6. Result Tuple Validation (validate_get_errors)
    print("\n--- Sample 6: Result Tuple Validation (true, None / false, errors) ---")
    
    data_missing = {"item1": "A"} # Missing item2, item3
    
    is_valid, errors = JsonValidator.validate_get_errors(PartialRequiredModel, data_missing)
    
    if not is_valid:
        print(f"Validation failed (is_valid={is_valid}). Errors count: {len(errors)}")
        for error in errors:
            print(f"  - Field: {'.'.join(map(str, error['loc']))}, Error: {error['msg']}")
    else:
        print("Validation unexpectedly succeeded.")

    is_valid, errors = JsonValidator.validate_get_errors(PartialRequiredModel, valid_partial)
    if is_valid:
        print(f"Validation succeeded (is_valid={is_valid}, errors={errors})")

if __name__ == "__main__":
    run_validation_samples()
