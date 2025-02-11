from typing import Any, Optional, cast

import aiohttp
from klaviyo_api import KlaviyoAPI
from rich.console import Console

console = Console()


class KlaviyoClient:
    """Main interface for Klaviyo operations using the official SDK."""

    def __init__(self, api_key: str):
        """Initialize the Klaviyo client with API key."""
        self.api_key = api_key
        self.client = KlaviyoAPI(api_key)
        self.base_url = "https://a.klaviyo.com/api"
        self._headers = {
            "accept": "application/vnd.api+json",
            "revision": "2025-01-15",
            "Authorization": f"Klaviyo-API-Key {api_key}",
        }

    async def _make_request(self, endpoint: str) -> dict:
        """Make an async request to the Klaviyo API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/{endpoint}", headers=self._headers
            ) as response:
                if response.status == 429:  # Rate limit hit
                    import asyncio

                    await asyncio.sleep(1)  # Wait 1 second before retrying
                    return await self._make_request(endpoint)
                return await response.json()

    async def get_tag_relationships(self, tag_id: str) -> dict:
        """Get all relationships for a specific tag."""
        lists = await self._make_request(f"tags/{tag_id}/relationships/lists")
        segments = await self._make_request(f"tags/{tag_id}/relationships/segments")
        flows = await self._make_request(f"tags/{tag_id}/relationships/flows")
        return {"lists": lists, "segments": segments, "flows": flows}

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
        # For first request, construct base endpoint
        if page_cursor and page_cursor.startswith("http"):
            # Use the full next URL if provided
            async with aiohttp.ClientSession() as session:
                async with session.get(page_cursor, headers=self._headers) as response:
                    return await response.json()
        else:
            endpoint = "tags"
            params = []

            if filter_string:
                params.append(f"filter={filter_string}")

            if params:
                endpoint = f"{endpoint}?{'&'.join(params)}"

        # Debug the full URL being requested
        console.print(f"[blue]Making request to: {endpoint}[/blue]")

        response = await self._make_request(endpoint)

        if not response.get("data"):
            console.print("[yellow]Warning: No tags found in response[/yellow]")
            console.print(f"Response: {response}")

        # Debug: Print pagination info
        if response.get("links"):
            console.print("[yellow]Pagination info:[/yellow]")
            console.print(response["links"])
        elif response.get("errors"):
            console.print("[red]Error in response:[/red]")
            console.print(response["errors"])

        return response

    async def analyze_tag_usage(self) -> dict[str, Any]:
        """
        Analyze tag usage across the account.
        Returns a dictionary containing:
        - all_tags: List of all tags
        - usage_analysis: Dictionary with tag usage statistics
        - unused_tags: List of tags with no relationships
        - active_tags: List of tags with active relationships
        - detailed_stats: Additional usage statistics
        """
        import asyncio

        all_tags = []
        usage_analysis = {}
        page_cursor = None

        with console.status("[bold green]Analyzing tags...") as status:
            # Fetch all tags
            while True:
                tags_response = await self.get_tags(page_cursor=page_cursor)
                current_tags = tags_response.get("data", [])

                if not current_tags:
                    console.print("[yellow]Warning: No tags found in response[/yellow]")
                    console.print(f"Response: {tags_response}")
                    break

                all_tags.extend(current_tags)
                status.update(f"[bold green]Fetching tags... ({len(all_tags)} found)")

                # Get next page cursor from the "next" URL
                links = tags_response.get("links", {})
                next_url = links.get("next")

                if not next_url:
                    break

                # Use the full next URL for pagination
                page_cursor = next_url

                await asyncio.sleep(0.1)  # Small delay between requests

            # Initialize statistics
            unused_tags = []
            active_tags = []
            detailed_stats = {
                "total_list_relationships": 0,
                "total_segment_relationships": 0,
                "total_flow_relationships": 0,
                "tags_by_usage_count": {},
                "most_used_tags": [],
            }

            # Process tags in chunks to avoid overwhelming the API
            chunk_size = 10
            for i in range(0, len(all_tags), chunk_size):
                chunk = all_tags[i : i + chunk_size]
                status.update(
                    f"[bold green]Processing tags {i+1}-{min(i+chunk_size, len(all_tags))} of {len(all_tags)}..."
                )

                # Process tags in parallel
                tasks = []
                for tag in chunk:
                    tasks.append(self.get_tag_relationships(tag["id"]))
                relationships_list = await asyncio.gather(*tasks)

                for tag, relationships in zip(chunk, relationships_list):
                    tag_id = tag["id"]
                    tag_name = tag["attributes"]["name"]

                    list_count = len(relationships["lists"].get("data", []))
                    segment_count = len(relationships["segments"].get("data", []))
                    flow_count = len(relationships["flows"].get("data", []))
                    total_usage = list_count + segment_count + flow_count

                    # Update detailed statistics
                    detailed_stats["total_list_relationships"] += list_count
                    detailed_stats["total_segment_relationships"] += segment_count
                    detailed_stats["total_flow_relationships"] += flow_count

                    # Group by usage count
                    usage_range = (
                        "0"
                        if total_usage == 0
                        else "1"
                        if total_usage == 1
                        else "2-5"
                        if total_usage <= 5
                        else "6-10"
                        if total_usage <= 10
                        else "11+"
                    )
                    detailed_stats["tags_by_usage_count"][usage_range] = (
                        detailed_stats["tags_by_usage_count"].get(usage_range, 0) + 1
                    )

                    usage_info = {
                        "id": tag_id,
                        "name": tag_name,
                        "list_count": list_count,
                        "segment_count": segment_count,
                        "flow_count": flow_count,
                        "total_usage": total_usage,
                        "relationships": {
                            "lists": [
                                r["id"] for r in relationships["lists"].get("data", [])
                            ],
                            "segments": [
                                r["id"]
                                for r in relationships["segments"].get("data", [])
                            ],
                            "flows": [
                                r["id"] for r in relationships["flows"].get("data", [])
                            ],
                        },
                    }

                    if total_usage == 0:
                        unused_tags.append(usage_info)
                    else:
                        active_tags.append(usage_info)

                    usage_analysis[tag_name] = usage_info

                await asyncio.sleep(0.1)  # Small delay between chunks

            # Sort and limit most used tags
            detailed_stats["most_used_tags"] = sorted(
                [t for t in active_tags], key=lambda x: x["total_usage"], reverse=True
            )[:10]

            return {
                "all_tags": all_tags,
                "usage_analysis": usage_analysis,
                "unused_tags": sorted(unused_tags, key=lambda x: x["name"]),
                "active_tags": sorted(
                    active_tags, key=lambda x: (-x["total_usage"], x["name"])
                ),
                "detailed_stats": detailed_stats,
                "summary": {
                    "total_tags": len(all_tags),
                    "unused_tags": len(unused_tags),
                    "active_tags": len(active_tags),
                    "total_relationships": (
                        detailed_stats["total_list_relationships"]
                        + detailed_stats["total_segment_relationships"]
                        + detailed_stats["total_flow_relationships"]
                    ),
                },
            }

    async def delete_unused_tags(self, dry_run: bool = True) -> dict[str, Any]:
        """
        Delete tags that have no relationships to any resources.

        Args:
            dry_run: If True, only returns what would be deleted without actually deleting

        Returns:
            Dictionary containing results of the operation
        """
        analysis = await self.analyze_tag_usage()
        unused_tags = analysis["unused_tags"]

        results = {
            "tags_to_delete": [tag["name"] for tag in unused_tags],
            "count": len(unused_tags),
            "dry_run": dry_run,
            "deleted": [],
        }

        if not dry_run:
            for tag in unused_tags:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(
                            f"{self.base_url}/tags/{tag['id']}", headers=self._headers
                        ) as response:
                            if response.status == 204:
                                results["deleted"].append(tag["name"])
                            else:
                                results["errors"] = results.get("errors", [])
                                results["errors"].append(
                                    {
                                        "tag": tag["name"],
                                        "error": f"Failed to delete: {response.status}",
                                    }
                                )
                except Exception as e:
                    results["errors"] = results.get("errors", [])
                    results["errors"].append({"tag": tag["name"], "error": str(e)})

        return results
