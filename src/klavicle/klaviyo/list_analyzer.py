"""Analyzer for Klaviyo lists."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import aiohttp
from rich.console import Console
from rich.table import Table


@dataclass
class ListStats:
    """Statistics for a list."""

    id: str
    name: str
    created: datetime
    updated: datetime
    profile_count: int
    tags: List[str]
    is_dynamic: bool
    folder_name: Optional[str] = None


class ListAnalyzer:
    """Analyzes Klaviyo lists to provide insights and recommendations."""

    def __init__(self, klaviyo_client):
        """Initialize with a KlaviyoClient instance."""
        self.client = klaviyo_client
        self.console = Console()

    async def get_list_stats(self, list_id: str) -> ListStats:
        """Get comprehensive statistics for a single list."""
        # Get list details
        list_response = await self.client._make_request(f"lists/{list_id}")
        list_data = list_response["data"]

        # Get list tags
        tags = await self.client._make_request(f"lists/{list_id}/tags")
        tag_names = [tag["attributes"]["name"] for tag in tags.get("data", [])]

        # Get list profile count
        profiles = await self.client._make_request(f"lists/{list_id}/profiles")
        profile_count = profiles.get("meta", {}).get("total", 0)

        return ListStats(
            id=list_data["id"],
            name=list_data["attributes"]["name"],
            created=datetime.fromisoformat(
                list_data["attributes"]["created"].replace("Z", "+00:00")
            ),
            updated=datetime.fromisoformat(
                list_data["attributes"]["updated"].replace("Z", "+00:00")
            ),
            profile_count=profile_count,
            tags=tag_names,
            is_dynamic=list_data["attributes"].get("is_dynamic", False),
            folder_name=list_data["attributes"].get("folder_name"),
        )

    async def analyze_all_lists(self) -> List[ListStats]:
        """Get statistics for all lists."""
        list_stats = []
        next_page = None

        with self.console.status("[bold green]Fetching lists...") as status:
            while True:
                # If we have a next_page URL, use it directly
                if next_page and next_page.startswith("http"):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            next_page, headers=self.client._headers
                        ) as response:
                            lists_response = await response.json()
                else:
                    lists_response = await self.client._make_request("lists")

                if not lists_response or "data" not in lists_response:
                    break

                current_lists = lists_response["data"]

                # Process each list in the current page
                for list_item in current_lists:
                    list_id = list_item["id"]
                    list_stats.append(await self.get_list_stats(list_id))
                    status.update(
                        f"[bold green]Processing lists... ({len(list_stats)} found)"
                    )

                # Check for next page
                links = lists_response.get("links", {})
                next_page = links.get("next")

                if not next_page:
                    break

                await asyncio.sleep(0.1)  # Small delay between requests

        return list_stats

    def print_list_analysis(self, list_stats: List[ListStats]) -> None:
        """Print a detailed analysis of lists to the console."""
        # Create summary table
        table = Table(title="List Analysis Summary")
        table.add_column("Name", style="cyan")
        table.add_column("Profiles", justify="right")
        table.add_column("Type", style="magenta")
        table.add_column("Folder", style="yellow")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Tags")

        for stat in sorted(list_stats, key=lambda x: x.updated, reverse=True):
            table.add_row(
                stat.name,
                str(stat.profile_count),
                "Dynamic" if stat.is_dynamic else "Static",
                stat.folder_name or "-",
                stat.updated.strftime("%Y-%m-%d"),
                ", ".join(stat.tags) if stat.tags else "-",
            )

        self.console.print(table)

        # Print insights
        self.console.print("\n[bold]List Insights:[/bold]")

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Identify empty lists
        empty_lists = [s for s in list_stats if s.profile_count == 0]
        if empty_lists:
            self.console.print(f"\n🔸 Found {len(empty_lists)} lists with no profiles:")
            for list_item in empty_lists:
                self.console.print(f"  - {list_item.name}")

        # Identify potentially stale lists
        stale_lists = [s for s in list_stats if (now - s.updated).days > 180]
        if stale_lists:
            self.console.print(
                f"\n🔸 Found {len(stale_lists)} lists not updated in over 6 months:"
            )
            for list_item in stale_lists:
                self.console.print(
                    f"  - {list_item.name} (Last updated: {list_item.updated.strftime('%Y-%m-%d')})"
                )

        # Identify lists without tags
        untagged_lists = [s for s in list_stats if not s.tags]
        if untagged_lists:
            self.console.print(f"\n🔸 Found {len(untagged_lists)} lists without tags:")
            for list_item in untagged_lists:
                self.console.print(f"  - {list_item.name}")

    def get_cleanup_recommendations(self, list_stats: List[ListStats]) -> List[str]:
        """Generate recommendations for lists that could potentially be cleaned up."""
        recommendations = []

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Check for empty lists
        empty_lists = [s for s in list_stats if s.profile_count == 0]
        if empty_lists:
            recommendations.append(
                f"Consider deleting {len(empty_lists)} lists with no profiles:"
            )
            for list_item in empty_lists:
                recommendations.append(f"  - {list_item.name}")

        # Check for stale lists
        stale_lists = [s for s in list_stats if (now - s.updated).days > 180]
        if stale_lists:
            recommendations.append(
                f"\nReview {len(stale_lists)} lists that haven't been updated in over 6 months:"
            )
            for list_item in stale_lists:
                recommendations.append(
                    f"  - {list_item.name} (Last updated: {list_item.updated.strftime('%Y-%m-%d')})"
                )

        # Check for duplicate list names
        name_counts = {}
        for stat in list_stats:
            if stat.name not in name_counts:
                name_counts[stat.name] = []
            name_counts[stat.name].append(stat.id)

        duplicates = {name: ids for name, ids in name_counts.items() if len(ids) > 1}
        if duplicates:
            recommendations.append("\nFound lists with duplicate names:")
            for name, ids in duplicates.items():
                recommendations.append(f"  - {name} ({len(ids)} lists)")

        return recommendations
