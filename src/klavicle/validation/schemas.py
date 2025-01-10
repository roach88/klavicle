from datetime import datetime
from typing import Annotated
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class SavedQuerySchema(BaseModel):
    """Schema for saved queries."""

    name: Annotated[str, Field(min_length=1, max_length=100)]
    query_text: Annotated[str, Field(min_length=1)]
    description: Optional[str] = None
    parameters: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfileSchema(BaseModel):
    """Schema for Klaviyo profile data."""

    email: Optional[EmailStr] = None
    phone_number: Optional[
        Annotated[str, Field(pattern=r"^\+[1-9]\d{1,14}$")]
    ] = None  # E.164 format
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    location: Optional[dict] = None
    properties: Optional[dict] = None

    class Config:
        extra = "allow"  # Allow additional fields


class ListSchema(BaseModel):
    """Schema for Klaviyo list data."""

    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Optional[str] = None


class SegmentSchema(BaseModel):
    """Schema for Klaviyo segment data."""

    name: Annotated[str, Field(min_length=1, max_length=100)]
    definition: dict


class TagSchema(BaseModel):
    """Schema for tag operations."""

    resource_type: Annotated[str, Field(pattern=r"^(list|segment)$")]
    resource_id: Annotated[str, Field(min_length=1)]
    tags: list[str]  # We'll validate min_items in the handler
