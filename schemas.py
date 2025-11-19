"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal, List

# Example schemas (keep as references):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Houseplant comparison app schema
# --------------------------------------------------

LightLevel = Literal['low', 'medium', 'bright']
CareLevel = Literal['easy', 'moderate', 'advanced']
WaterNeed = Literal['low', 'moderate', 'high']
SizeClass = Literal['small', 'medium', 'large']

class Plant(BaseModel):
    """
    Houseplants collection schema
    Collection name: "plant"
    """
    name: str = Field(..., description="Common name")
    scientific_name: Optional[str] = Field(None, description="Botanical name")
    description: Optional[str] = Field(None, description="Short description and care notes")
    image_url: Optional[HttpUrl] = Field(None, description="Image URL")

    light: LightLevel = Field(..., description="Preferred light level")
    water: WaterNeed = Field(..., description="Watering needs")
    care_level: CareLevel = Field(..., description="Overall difficulty")

    pet_friendly: bool = Field(False, description="Safe for pets")
    size: SizeClass = Field('medium', description="Typical mature size indoors")

    humidity: Optional[str] = Field(None, description="Humidity preference")
    placement: Optional[str] = Field(None, description="Best placement e.g., north window")
    growth_rate: Optional[str] = Field(None, description="Slow / Moderate / Fast")
    ideal_temp_min_c: Optional[float] = Field(None, description="Min ideal temp in °C")
    ideal_temp_max_c: Optional[float] = Field(None, description="Max ideal temp in °C")

    price: Optional[float] = Field(None, ge=0, description="Typical price in dollars")
    tags: Optional[List[str]] = Field(default=None, description="Extra labels for filtering")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
