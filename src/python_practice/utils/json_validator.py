import json
from typing import Any, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

type ValidationResult = tuple[bool, list[dict[str, Any]] | None]

class JsonValidator:
    """
    A utility class for validating JSON data against Pydantic models.
    """

    @staticmethod
    def validate(model_class: type[T], data: dict[str, Any] | str) -> T:
        """
        Validates the given data against the specified Pydantic model.

        Args:
            model_class: The Pydantic model class to validate against.
            data: The data to validate. Can be a dictionary or a JSON string.

        Returns:
            An instance of the model_class with the validated data.

        Raises:
            ValidationError: If the data does not match the model.
            ValueError: If the data is a string but not valid JSON.
        """
        match data:
            case str() as json_str:
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON string: {e}")
            case _:
                # Already a dict or other compatible type
                pass

        return model_class.model_validate(data)

    @staticmethod
    def validate_get_errors(
        model_class: type[BaseModel], 
        data: dict[str, Any] | str
    ) -> ValidationResult:
        """
        Validates the given data and returns the result as a tuple.

        Args:
            model_class: The Pydantic model class to validate against.
            data: The data to validate.

        Returns:
            A tuple of (is_valid, errors). 
            If valid, (True, None). 
            If invalid, (False, list_of_errors).
        """
        try:
            JsonValidator.validate(model_class, data)
            return True, None
        except ValidationError as e:
            return False, e.errors()
        except ValueError:
            # Handle JSON decode errors if data was a string
            return False, [{"loc": ["json"], "msg": "Invalid JSON string", "type": "value_error"}]

    @staticmethod
    def is_valid(model_class: type[BaseModel], data: dict[str, Any] | str) -> bool:
        """
        Checks if the given data is valid against the specified Pydantic model without raising an exception.

        Args:
            model_class: The Pydantic model class to validate against.
            data: The data to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            JsonValidator.validate(model_class, data)
            return True
        except (ValidationError, ValueError):
            return False
