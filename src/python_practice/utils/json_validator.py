import json
from typing import Any, Dict, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

class JsonValidator:
    """
    A utility class for validating JSON data against Pydantic models.
    """

    @staticmethod
    def validate(model_class: Type[T], data: Union[Dict[str, Any], str]) -> T:
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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")

        return model_class.model_validate(data)

    @staticmethod
    def is_valid(model_class: Type[BaseModel], data: Union[Dict[str, Any], str]) -> bool:
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
