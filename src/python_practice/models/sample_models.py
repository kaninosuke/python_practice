from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., gt=0)
    tags: list[str] = Field(default_factory=list)

class Order(BaseModel):
    order_id: str = Field(..., pattern=r"^[A-Z]{2}-\d{4}$")  # e.g., AB-1234
    customer_email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    items: list[Product] = Field(..., min_length=1)
    order_date: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=1, ge=1, le=5)
    discount_code: str | None = None

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
    item4: str | None = Field(None, description="Optional item 4")
    item5: str | None = Field(None, description="Optional item 5")
    item6: str | None = Field(None, description="Optional item 6")
    item7: str | None = Field(None, description="Optional item 7")

class ComprehensiveModel(BaseModel):
    required_str: str = Field(..., description="必須チェック (Required)")
    length_str: str = Field(..., min_length=3, max_length=10, description="文字数チェック (Length: 3-10)")
    text_data: str = Field(..., description="text型 (String)")
    number_data: int = Field(..., ge=0, le=100, description="数字型 (Integer: 0-100)")
    date_data: datetime = Field(..., description="datetime型 (Datetime)")
    regex_str: str = Field(..., pattern=r"^[A-Z]{3}-\d{3}$", description="正規表現チェック (Regex: AAA-111)")
