import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from rich.console import Console
from rich.table import Table


@dataclass
class FlowStats:
    """Statistics for a flow."""

    id: str
    name: str
    status: str
    archived: bool
    created: datetime
    updated: datetime
    trigger_type: str
    action_count: int
    email_count: int
    sms_count: int
    time_delay_count: int
    tags: List[str]
    last_activity: Optional[datetime] = None


class FlowAnalyzer:
    """Analyzes Klaviyo flows to provide insights and recommendations."""

    def __init__(self, klaviyo_client):
        """Initialize with a KlaviyoClient instance."""
        self.client = klaviyo_client
        self.console = Console()

    async def get_flow_stats(self, flow_id: str) -> FlowStats:
        """Get comprehensive statistics for a single flow."""
        # Get flow details
        flow = await self.client._make_request(f"flows/{flow_id}")
        flow_data = flow["data"]

        # Get flow actions
        actions = await self.client._make_request(f"flows/{flow_id}/flow-actions")
        action_data = actions.get("data", [])

        # Get flow tags
        tags = await self.client._make_request(f"flows/{flow_id}/tags")
        tag_names = [tag["attributes"]["name"] for tag in tags.get("data", [])]

        # Count different action types
        email_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "SEND_EMAIL"
        )
        sms_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "SEND_SMS"
        )
        time_delay_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "TIME_DELAY"
        )

        return FlowStats(
            id=flow_data["id"],
            name=flow_data["attributes"]["name"],
            status=flow_data["attributes"]["status"],
            archived=flow_data["attributes"]["archived"],
            created=datetime.fromisoformat(
                flow_data["attributes"]["created"].replace("Z", "+00:00")
            ),
            updated=datetime.fromisoformat(
                flow_data["attributes"]["updated"].replace("Z", "+00:00")
            ),
            trigger_type=flow_data["attributes"]["trigger_type"],
            action_count=len(action_data),
            email_count=email_count,
            sms_count=sms_count,
            time_delay_count=time_delay_count,
            tags=tag_names,
        )

    async def analyze_all_flows(self) -> List[FlowStats]:
        """Get statistics for all flows."""
        flow_stats = []
        next_page = None

        with self.console.status("[bold green]Fetching flows...") as status:
            while True:
                # If we have a next_page URL, use it directly
                if next_page and next_page.startswith("http"):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            next_page, headers=self.client._headers
                        ) as response:
                            flows_response = await response.json()
                else:
                    flows_response = await self.client._make_request("flows")

                if not flows_response or "data" not in flows_response:
                    break

                current_flows = flows_response["data"]

                # Process each flow in the current page
                for flow in current_flows:
                    flow_id = flow["id"]
                    flow_stats.append(await self.get_flow_stats(flow_id))
                    status.update(
                        f"[bold green]Processing flows... ({len(flow_stats)} found)"
                    )

                # Check for next page
                links = flows_response.get("links", {})
                next_page = links.get("next")

                if not next_page:
                    break

                await asyncio.sleep(0.1)  # Small delay between requests

        return flow_stats

    def print_flow_analysis(self, flow_stats: List[FlowStats]) -> None:
        """Print a detailed analysis of flows to the console."""
        # Create summary table
        table = Table(title="Flow Analysis Summary")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Trigger Type", style="magenta")
        table.add_column("Actions", justify="right")
        table.add_column("Emails", justify="right")
        table.add_column("SMS", justify="right")
        table.add_column("Delays", justify="right")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Tags")

        for stat in sorted(flow_stats, key=lambda x: x.updated, reverse=True):
            table.add_row(
                stat.name,
                stat.status,
                stat.trigger_type,
                str(stat.action_count),
                str(stat.email_count),
                str(stat.sms_count),
                str(stat.time_delay_count),
                stat.updated.strftime("%Y-%m-%d"),
                ", ".join(stat.tags) if stat.tags else "-",
            )

        self.console.print(table)

        # Print insights
        self.console.print("\n[bold]Flow Insights:[/bold]")

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Identify inactive flows
        inactive_flows = [s for s in flow_stats if s.status != "live"]
        if inactive_flows:
            self.console.print(
                f"\n🔸 Found {len(inactive_flows)} inactive flows that could be reviewed:"
            )
            for flow in inactive_flows:
                self.console.print(f"  - {flow.name} (Status: {flow.status})")

        # Identify potentially abandoned flows
        old_flows = [s for s in flow_stats if (now - s.updated).days > 180]
        if old_flows:
            self.console.print(
                f"\n🔸 Found {len(old_flows)} flows not updated in over 6 months:"
            )
            for flow in old_flows:
                self.console.print(
                    f"  - {flow.name} (Last updated: {flow.updated.strftime('%Y-%m-%d')})"
                )

        # Identify flows without tags
        untagged_flows = [s for s in flow_stats if not s.tags]
        if untagged_flows:
            self.console.print(f"\n🔸 Found {len(untagged_flows)} flows without tags:")
            for flow in untagged_flows:
                self.console.print(f"  - {flow.name}")

    async def get_flow_performance(
        self, flow_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get performance metrics for a specific flow."""
        try:
            response = await self.client._make_request(
                "flow-values-reports",
                method="POST",
                data={
                    "data": {
                        "type": "flow-values-report",
                        "attributes": {
                            "statistics": ["opens", "clicks", "conversions", "revenue"],
                            "timeframe": f"last_{days}_days",
                        },
                    }
                },
            )
            return response
        except Exception as e:
            self.console.print(
                f"[red]Error getting performance data for flow {flow_id}: {str(e)}[/red]"
            )
            return {}

    def get_cleanup_recommendations(self, flow_stats: List[FlowStats]) -> List[str]:
        """Generate recommendations for flows that could potentially be cleaned up."""
        recommendations = []

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Check for draft flows older than 30 days
        old_drafts = [
            s for s in flow_stats if s.status == "draft" and (now - s.created).days > 30
        ]
        if old_drafts:
            recommendations.append(
                f"Consider deleting {len(old_drafts)} draft flows that are over 30 days old:"
            )
            for flow in old_drafts:
                recommendations.append(
                    f"  - {flow.name} (Created: {flow.created.strftime('%Y-%m-%d')})"
                )

        # Check for archived flows
        archived = [s for s in flow_stats if s.archived]
        if archived:
            recommendations.append(
                f"\nFound {len(archived)} archived flows that could be deleted if no longer needed:"
            )
            for flow in archived:
                recommendations.append(f"  - {flow.name}")

        # Check for duplicate trigger types
        trigger_counts = {}
        for stat in flow_stats:
            if stat.trigger_type not in trigger_counts:
                trigger_counts[stat.trigger_type] = []
            trigger_counts[stat.trigger_type].append(stat.name)

        for trigger_type, flows in trigger_counts.items():
            if len(flows) > 1:
                recommendations.append(
                    f"\nFound {len(flows)} flows with '{trigger_type}' trigger - consider consolidating:"
                )
                for flow in flows:
                    recommendations.append(f"  - {flow}")

        return recommendations
