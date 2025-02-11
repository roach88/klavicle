"""Analyzer for Klaviyo campaigns."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import aiohttp
from rich.console import Console
from rich.table import Table


@dataclass
class CampaignStats:
    """Statistics for a campaign."""

    id: str
    name: str
    status: str
    created: datetime
    updated: datetime
    send_time: Optional[datetime]
    channel: str
    message_type: str
    subject_line: Optional[str]
    from_email: Optional[str]
    from_name: Optional[str]
    tags: List[str]
    recipient_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    revenue: float = 0.0


class CampaignAnalyzer:
    """Analyzes Klaviyo campaigns to provide insights and recommendations."""

    def __init__(self, klaviyo_client):
        """Initialize with a KlaviyoClient instance."""
        self.client = klaviyo_client
        self.console = Console()

    async def get_campaign_stats(self, campaign_id: str) -> CampaignStats:
        """Get comprehensive statistics for a single campaign."""
        # Get campaign details
        campaign = await self.client._make_request(f"campaigns/{campaign_id}")
        campaign_data = campaign["data"]
        attributes = campaign_data["attributes"]

        # Get campaign tags
        tags = await self.client._make_request(f"campaigns/{campaign_id}/tags")
        tag_names = [tag["attributes"]["name"] for tag in tags.get("data", [])]

        # Get campaign metrics if it has been sent
        metrics = {}
        if attributes["status"] == "sent":
            try:
                metrics_response = await self.client._make_request(
                    f"campaigns/{campaign_id}/metrics"
                )
                metrics = metrics_response.get("data", {}).get("attributes", {})
            except Exception:
                # If metrics aren't available, continue with zeros
                pass

        # Parse send time if available
        send_time = None
        if attributes.get("send_time"):
            send_time = datetime.fromisoformat(
                attributes["send_time"].replace("Z", "+00:00")
            )

        return CampaignStats(
            id=campaign_data["id"],
            name=attributes["name"],
            status=attributes["status"],
            created=datetime.fromisoformat(
                attributes["created"].replace("Z", "+00:00")
            ),
            updated=datetime.fromisoformat(
                attributes["updated"].replace("Z", "+00:00")
            ),
            send_time=send_time,
            channel=attributes.get("channel", "unknown"),
            message_type=attributes.get("message_type", "unknown"),
            subject_line=attributes.get("subject_line"),
            from_email=attributes.get("from_email"),
            from_name=attributes.get("from_name"),
            tags=tag_names,
            recipient_count=metrics.get("recipient_count", 0),
            open_rate=metrics.get("open_rate", 0.0),
            click_rate=metrics.get("click_rate", 0.0),
            revenue=metrics.get("revenue", 0.0),
        )

    async def analyze_all_campaigns(self) -> List[CampaignStats]:
        """Get statistics for all campaigns."""
        campaign_stats = []
        next_page = None

        with self.console.status("[bold green]Fetching campaigns...") as status:
            while True:
                # If we have a next_page URL, use it directly
                if next_page and next_page.startswith("http"):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            next_page, headers=self.client._headers
                        ) as response:
                            campaigns_response = await response.json()
                else:
                    campaigns_response = await self.client._make_request("campaigns")

                if not campaigns_response or "data" not in campaigns_response:
                    break

                current_campaigns = campaigns_response["data"]

                # Process each campaign in the current page
                for campaign in current_campaigns:
                    campaign_id = campaign["id"]
                    campaign_stats.append(await self.get_campaign_stats(campaign_id))
                    status.update(
                        f"[bold green]Processing campaigns... ({len(campaign_stats)} found)"
                    )

                # Check for next page
                links = campaigns_response.get("links", {})
                next_page = links.get("next")

                if not next_page:
                    break

                await asyncio.sleep(0.1)  # Small delay between requests

        return campaign_stats

    def print_campaign_analysis(self, campaign_stats: List[CampaignStats]) -> None:
        """Print a detailed analysis of campaigns to the console."""
        # Create summary table
        table = Table(title="Campaign Analysis Summary")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Recipients", justify="right")
        table.add_column("Open Rate", justify="right")
        table.add_column("Click Rate", justify="right")
        table.add_column("Revenue", justify="right")
        table.add_column("Send Time", style="yellow")
        table.add_column("Tags")

        for stat in sorted(
            campaign_stats, key=lambda x: x.send_time or x.created, reverse=True
        ):
            table.add_row(
                stat.name,
                stat.status,
                f"{stat.channel}/{stat.message_type}",
                f"{stat.recipient_count:,}",
                f"{stat.open_rate:.1%}" if stat.open_rate else "-",
                f"{stat.click_rate:.1%}" if stat.click_rate else "-",
                f"${stat.revenue:,.2f}" if stat.revenue else "-",
                stat.send_time.strftime("%Y-%m-%d") if stat.send_time else "-",
                ", ".join(stat.tags) if stat.tags else "-",
            )

        self.console.print(table)

        # Print insights
        self.console.print("\n[bold]Campaign Insights:[/bold]")

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Calculate performance metrics
        sent_campaigns = [s for s in campaign_stats if s.status == "sent"]
        if sent_campaigns:
            avg_open_rate = sum(c.open_rate for c in sent_campaigns) / len(
                sent_campaigns
            )
            avg_click_rate = sum(c.click_rate for c in sent_campaigns) / len(
                sent_campaigns
            )
            total_revenue = sum(c.revenue for c in sent_campaigns)

            self.console.print("\n[bold]Performance Summary:[/bold]")
            self.console.print(f"Average Open Rate: {avg_open_rate:.1%}")
            self.console.print(f"Average Click Rate: {avg_click_rate:.1%}")
            self.console.print(f"Total Revenue: ${total_revenue:,.2f}")

        # Identify draft campaigns
        draft_campaigns = [s for s in campaign_stats if s.status == "draft"]
        if draft_campaigns:
            self.console.print(
                f"\n🔸 Found {len(draft_campaigns)} campaigns in draft status:"
            )
            for campaign in draft_campaigns:
                self.console.print(f"  - {campaign.name}")

        # Identify campaigns without tags
        untagged_campaigns = [s for s in campaign_stats if not s.tags]
        if untagged_campaigns:
            self.console.print(
                f"\n🔸 Found {len(untagged_campaigns)} campaigns without tags:"
            )
            for campaign in untagged_campaigns:
                self.console.print(f"  - {campaign.name}")

        # Identify high-performing campaigns
        if sent_campaigns:
            top_revenue = sorted(sent_campaigns, key=lambda x: x.revenue, reverse=True)[
                :5
            ]
            top_open_rate = sorted(
                sent_campaigns, key=lambda x: x.open_rate, reverse=True
            )[:5]

            self.console.print("\n[bold]Top Performing Campaigns:[/bold]")

            self.console.print("\nTop Revenue Generators:")
            for campaign in top_revenue:
                self.console.print(f"  - {campaign.name}: ${campaign.revenue:,.2f}")

            self.console.print("\nHighest Open Rates:")
            for campaign in top_open_rate:
                self.console.print(f"  - {campaign.name}: {campaign.open_rate:.1%}")

    def get_cleanup_recommendations(
        self, campaign_stats: List[CampaignStats]
    ) -> List[str]:
        """Generate recommendations for campaigns that could potentially be cleaned up."""
        recommendations = []

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Check for old draft campaigns
        old_drafts = [
            s
            for s in campaign_stats
            if s.status == "draft" and (now - s.created).days > 30
        ]
        if old_drafts:
            recommendations.append(
                f"Consider reviewing {len(old_drafts)} draft campaigns older than 30 days:"
            )
            for campaign in old_drafts:
                recommendations.append(
                    f"  - {campaign.name} (Created: {campaign.created.strftime('%Y-%m-%d')})"
                )

        # Check for duplicate campaign names
        name_counts = {}
        for stat in campaign_stats:
            if stat.name not in name_counts:
                name_counts[stat.name] = []
            name_counts[stat.name].append(stat.id)

        duplicates = {name: ids for name, ids in name_counts.items() if len(ids) > 1}
        if duplicates:
            recommendations.append("\nFound campaigns with duplicate names:")
            for name, ids in duplicates.items():
                recommendations.append(f"  - {name} ({len(ids)} campaigns)")

        # Check for low-performing campaigns
        sent_campaigns = [s for s in campaign_stats if s.status == "sent"]
        if sent_campaigns:
            avg_open_rate = sum(c.open_rate for c in sent_campaigns) / len(
                sent_campaigns
            )
            low_performing = [
                s
                for s in sent_campaigns
                if s.open_rate < (avg_open_rate * 0.5)  # Less than 50% of average
            ]
            if low_performing:
                recommendations.append(
                    f"\nReview {len(low_performing)} campaigns with below-average performance:"
                )
                for campaign in low_performing:
                    recommendations.append(
                        f"  - {campaign.name} (Open Rate: {campaign.open_rate:.1%}, Avg: {avg_open_rate:.1%})"
                    )

        return recommendations
