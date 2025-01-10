from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class ValidationError(Exception):
    """Custom validation error."""

    pass


class ProfileData(BaseModel):
    """Profile data validation model."""

    email: Optional[str] = None
    phone_number: Optional[str] = None
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    title: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    @validator("email")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @validator("phone_number")
    def validate_phone(cls, v):
        if v and not v.replace("+", "").replace("-", "").isdigit():
            raise ValueError("Invalid phone number format")
        return v


class ListData(BaseModel):
    """List data validation model."""

    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class SegmentData(BaseModel):
    """Segment data validation model."""

    name: str = Field(..., min_length=1)
    conditions: Dict[str, Any]


def validate_sql_query(query: str) -> str:
    """Validate SQL query."""
    if not query.strip():
        raise ValidationError("Query cannot be empty")
    return query.strip()


def validate_saved_query(
    name: str, query_text: str, description: Optional[str] = None
) -> None:
    """Validate saved query data."""
    if not name.strip():
        raise ValidationError("Query name cannot be empty")
    validate_sql_query(query_text)


def validate_profile_data(data: Dict[str, Any]) -> None:
    """Validate profile data."""
    try:
        ProfileData(**data)
    except Exception as e:
        raise ValidationError(str(e))


def validate_list_data(data: Dict[str, Any]) -> None:
    """Validate list data."""
    try:
        ListData(**data)
    except Exception as e:
        raise ValidationError(str(e))


def validate_segment_data(data: Dict[str, Any]) -> None:
    """Validate segment data."""
    try:
        SegmentData(**data)
    except Exception as e:
        raise ValidationError(str(e))
