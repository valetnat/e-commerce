from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field


class DetailsBaseModel(BaseModel):
    name: str = Field(max_length=512)
    value: str = Field(max_length=128)


class CategoryBaseModel(BaseModel):
    category: str = Field(max_length=128)
    cat_slug: str = Field(max_length=128)
    subcategory: Optional[str] = Field(default=None, max_length=128)
    sub_slug: Optional[str] = Field(default=None, max_length=128)


class ManufacturerBaseModel(BaseModel):
    name: str = Field(max_length=128)
    slug: str = Field(max_length=128)


class OfferBaseModel(BaseModel):
    price: Decimal = Field(ge=0.01, max_digits=10, decimal_places=2)
    quantity: int = Field(gt=0)


class ProductBaseModel(BaseModel):
    name: str = Field(max_length=512)
    manufacturer: ManufacturerBaseModel
    about: str = Field(max_length=512)
    description: str = Field(max_length=1024)
    category: CategoryBaseModel
    shop: str = Field(max_length=512)
    preview: str
    tags: Optional[List[str]] = Field(max_length=64)
    offer: OfferBaseModel
    details: List[DetailsBaseModel]
