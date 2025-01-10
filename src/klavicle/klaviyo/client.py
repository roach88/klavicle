from typing import Any, Optional, cast

from klaviyo_api import KlaviyoAPI


class KlaviyoClient:
    """Main interface for Klaviyo operations using the official SDK."""

    def __init__(self, api_key: str):
        """Initialize the Klaviyo client with API key."""
        self.client = KlaviyoAPI(api_key)

    # Profile Operations
    async def get_profiles(
        self, page_cursor: Optional[str] = None, filter_string: Optional[str] = None
    ) -> Any:
        """Get all profiles with optional pagination and filtering."""
        kwargs = {}
        if filter_string:
            kwargs["filter"] = filter_string
        if page_cursor:
            kwargs["page_cursor"] = page_cursor
        return self.client.Profiles.get_profiles(**kwargs)

    async def get_profile(self, profile_id: str) -> Any:
        """Get a profile by ID."""
        return self.client.Profiles.get_profile(profile_id)

    async def create_profile(self, profile_data: dict) -> Any:
        """Create a new profile."""
        data = {"data": {"type": "profile", **profile_data}}
        return self.client.Profiles.create_profile(cast(Any, data))

    async def update_profile(self, profile_id: str, profile_data: dict) -> Any:
        """Update an existing profile."""
        data = {"data": {"type": "profile", **profile_data}}
        return self.client.Profiles.update_profile(profile_id, cast(Any, data))

    # List Operations
    async def get_lists(
        self, page_cursor: Optional[str] = None, filter_string: Optional[str] = None
    ) -> Any:
        """Get all lists with optional pagination and filtering."""
        kwargs = {}
        if filter_string:
            kwargs["filter"] = filter_string
        if page_cursor:
            kwargs["page_cursor"] = page_cursor
        return self.client.Lists.get_lists(**kwargs)

    async def create_list(self, name: str, description: Optional[str] = None) -> Any:
        """Create a new list."""
        data = {
            "data": {
                "type": "list",
                "attributes": {"name": name, "description": description},
            }
        }
        return self.client.Lists.create_list(cast(Any, data))

    async def add_profiles_to_list(self, list_id: str, profile_ids: list[str]) -> Any:
        """Add profiles to a list."""
        data = {
            "data": [
                {"type": "profile", "id": profile_id} for profile_id in profile_ids
            ]
        }
        return self.client.Lists.create_list_relationships(list_id, cast(Any, data))

    async def remove_profiles_from_list(
        self, list_id: str, profile_ids: list[str]
    ) -> Any:
        """Remove profiles from a list."""
        data = {
            "data": [
                {"type": "profile", "id": profile_id} for profile_id in profile_ids
            ]
        }
        return self.client.Lists.delete_list_relationships(list_id, cast(Any, data))

    # Segment Operations
    async def get_segments(
        self, page_cursor: Optional[str] = None, filter_string: Optional[str] = None
    ) -> Any:
        """Get all segments with optional pagination and filtering."""
        kwargs = {}
        if filter_string:
            kwargs["filter"] = filter_string
        if page_cursor:
            kwargs["page_cursor"] = page_cursor
        return self.client.Segments.get_segments(**kwargs)

    async def create_segment(self, name: str, definition: dict) -> Any:
        """Create a new segment with conditions."""
        data = {
            "data": {
                "type": "segment",
                "attributes": {"name": name, "definition": definition},
            }
        }
        return self.client.Segments.create_segment(cast(Any, data))  # type: ignore

    # Tag Operations
    async def add_tags(
        self, resource_type: str, resource_id: str, tags: list[str]
    ) -> Any:
        """Add tags to a resource."""
        tag_data = {
            "data": [{"type": "tag", "attributes": {"name": tag}} for tag in tags]
        }
        if resource_type == "list":
            return self.client.Tags.tag_lists(resource_id, cast(Any, tag_data))  # type: ignore
        elif resource_type == "segment":
            return self.client.Tags.tag_segments(resource_id, cast(Any, tag_data))  # type: ignore
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    async def remove_tags(
        self, resource_type: str, resource_id: str, tags: list[str]
    ) -> Any:
        """Remove tags from a resource."""
        tag_data = {
            "data": [{"type": "tag", "attributes": {"name": tag}} for tag in tags]
        }
        if resource_type == "list":
            return self.client.Tags.remove_tag_from_lists(  # type: ignore
                resource_id, cast(Any, tag_data)
            )
        elif resource_type == "segment":
            return self.client.Tags.remove_tag_from_segments(  # type: ignore
                resource_id, cast(Any, tag_data)
            )
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    async def get_tags(
        self, page_cursor: Optional[str] = None, filter_string: Optional[str] = None
    ) -> Any:
        """Get all tags with optional pagination and filtering."""
        kwargs = {}
        if filter_string:
            kwargs["filter"] = filter_string
        if page_cursor:
            kwargs["page_cursor"] = page_cursor
        return self.client.Tags.get_tags(**kwargs)
