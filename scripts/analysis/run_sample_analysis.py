#!/usr/bin/env python
"""
This script runs AI analysis with sample data for testing purposes.
It uses the mock provider by default but can be switched to anthropic or openai.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Create mock data for sample mode
def get_mock_data():
    """Create mock data for testing AI analysis."""
    return {
        "campaigns": [
            {
                "id": "mock_campaign_1",
                "name": "Mock Newsletter Campaign",
                "status": "sent",
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-05T12:00:00Z",
                "send_time": "2024-01-10T08:00:00Z",
                "channel": "email",
                "message_type": "newsletter",
                "subject_line": "Check out our new products!",
                "from_email": "marketing@example.com",
                "from_name": "Marketing Team",
                "tags": ["newsletter", "product:launch", "audience:all"],
                "metrics": {
                    "recipient_count": 5000,
                    "open_rate": 0.22,
                    "click_rate": 0.08,
                    "revenue": 1200.00,
                }
            },
            {
                "id": "mock_campaign_2",
                "name": "Mock Sale Announcement",
                "status": "sent",
                "created": "2024-02-01T10:00:00Z",
                "updated": "2024-02-05T12:00:00Z",
                "send_time": "2024-02-10T08:00:00Z",
                "channel": "email",
                "message_type": "promotional",
                "subject_line": "50% Off Sale - This Weekend Only!",
                "from_email": "sales@example.com",
                "from_name": "Sales Team",
                "tags": ["promotion", "sale", "audience:active"],
                "metrics": {
                    "recipient_count": 8000,
                    "open_rate": 0.35,
                    "click_rate": 0.12,
                    "revenue": 5600.00,
                }
            },
            {
                "id": "mock_campaign_3",
                "name": "Mock Product Announcement",
                "status": "sent",
                "created": "2024-03-01T10:00:00Z",
                "updated": "2024-03-05T12:00:00Z",
                "send_time": "2024-03-10T08:00:00Z",
                "channel": "email",
                "message_type": "announcement",
                "subject_line": "Introducing Our New Product Line",
                "from_email": "products@example.com",
                "from_name": "Product Team",
                "tags": ["product:launch", "announcement", "audience:all"],
                "metrics": {
                    "recipient_count": 12000,
                    "open_rate": 0.28,
                    "click_rate": 0.09,
                    "revenue": 3200.00,
                }
            }
        ],
        "flows": [
            {
                "id": "mock_flow_1",
                "name": "Mock Welcome Series",
                "status": "live",
                "archived": False,
                "created": "2023-01-15T10:00:00Z",
                "updated": "2024-01-20T12:00:00Z",
                "trigger_type": "signup",
                "structure": {
                    "action_count": 5,
                    "email_count": 3,
                    "sms_count": 1,
                    "time_delay_count": 3,
                },
                "tags": ["onboarding", "automation:welcome", "audience:new"]
            },
            {
                "id": "mock_flow_2",
                "name": "Mock Abandoned Cart",
                "status": "live",
                "archived": False,
                "created": "2023-02-15T10:00:00Z",
                "updated": "2024-02-20T12:00:00Z",
                "trigger_type": "abandoned_cart",
                "structure": {
                    "action_count": 6,
                    "email_count": 3,
                    "sms_count": 2,
                    "time_delay_count": 4,
                },
                "tags": ["cart", "recovery", "automation:cart"]
            },
            {
                "id": "mock_flow_3",
                "name": "Mock Re-engagement",
                "status": "live",
                "archived": False,
                "created": "2023-03-15T10:00:00Z",
                "updated": "2024-03-20T12:00:00Z",
                "trigger_type": "metric_triggered",
                "structure": {
                    "action_count": 4,
                    "email_count": 3,
                    "sms_count": 0,
                    "time_delay_count": 2,
                },
                "tags": ["re-engagement", "win-back", "audience:inactive"]
            }
        ],
        "lists": [
            {
                "id": "mock_list_1",
                "name": "Mock Newsletter Subscribers",
                "created": "2023-01-10T10:00:00Z",
                "updated": "2024-01-15T12:00:00Z",
                "profile_count": 25000,
                "is_dynamic": False,
                "folder_name": "Main Lists",
                "tags": ["newsletter", "source:website", "opt-in:explicit"]
            },
            {
                "id": "mock_list_2",
                "name": "Mock High Value Customers",
                "created": "2023-02-10T10:00:00Z",
                "updated": "2024-02-15T12:00:00Z",
                "profile_count": 5000,
                "is_dynamic": True,
                "folder_name": "Segments",
                "tags": ["high-value", "segment:value", "behavior:purchase"]
            },
            {
                "id": "mock_list_3",
                "name": "Mock VIP Members",
                "created": "2023-03-10T10:00:00Z",
                "updated": "2024-03-15T12:00:00Z",
                "profile_count": 1000,
                "is_dynamic": True,
                "folder_name": "VIP",
                "tags": ["vip", "segment:loyalty", "tier:gold"]
            }
        ]
    }

async def main(provider: str = "mock", export_format: Optional[str] = "md"):
    """Run AI analysis with sample data."""
    # Import after defining mock data to avoid circular import
    from src.klavicle.ai.analyzer import AIAnalyzer
    from rich.console import Console
    
    # Set up console output
    console = Console()
    console.print("[bold green]Running AI analysis with sample data...[/bold green]")
    
    # Get mock data
    data = get_mock_data()
    
    # Create AI analyzer with the specified provider
    analyzer = AIAnalyzer(provider=provider)
    
    # Run analysis on the unified data
    with console.status("[bold green]Analyzing with AI..."):
        data_json = json.dumps(data)
        results = await analyzer.analyze_data("unified", data_json)
    
    # Print results
    console.print("\n[bold blue]Analysis Results[/bold blue]")
    analyzer.format_insights_for_display(results)
    
    # Export results if requested
    if export_format:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create outputs directory if it doesn't exist
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        filename = outputs_dir / f"unified_analysis_{timestamp}.{export_format}"
        
        if export_format in ["md", "markdown"]:
            with open(filename, "w") as f:
                # Create a nice markdown document
                f.write(f"# AI Analysis Results - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                # Summary section
                if "summary" in results:
                    f.write("## Summary\n\n")
                    f.write(f"{results['summary']}\n\n")
                
                # Account health section
                if "account_health" in results:
                    account_health = results["account_health"]
                    f.write("## Account Health\n\n")
                    f.write(f"**Overall Score**: {account_health.get('score', 'N/A')}/10\n\n")
                    
                    if "strengths" in account_health and account_health["strengths"]:
                        f.write("### Strengths\n\n")
                        for strength in account_health["strengths"]:
                            f.write(f"- {strength}\n")
                        f.write("\n")
                    
                    if "areas_for_improvement" in account_health and account_health["areas_for_improvement"]:
                        f.write("### Areas for Improvement\n\n")
                        for area in account_health["areas_for_improvement"]:
                            f.write(f"- {area}\n")
                        f.write("\n")
                    
                    if "critical_issues" in account_health and account_health["critical_issues"]:
                        f.write("### Critical Issues\n\n")
                        for issue in account_health["critical_issues"]:
                            f.write(f"- {issue}\n")
                        f.write("\n")
                
                # Strategic recommendations
                if "strategic_recommendations" in results and results["strategic_recommendations"]:
                    f.write("## Strategic Recommendations\n\n")
                    for i, rec in enumerate(results["strategic_recommendations"], 1):
                        area = rec.get("area", "General")
                        current = rec.get("current_state", "")
                        target = rec.get("target_state", "")
                        priority = rec.get("priority", "Medium")
                        steps = rec.get("steps", [])
                        
                        f.write(f"### {i}. {area} ({priority} Priority)\n\n")
                        if current:
                            f.write(f"**Current State**: {current}\n\n")
                        if target:
                            f.write(f"**Target State**: {target}\n\n")
                        
                        if steps:
                            f.write("#### Implementation Steps\n\n")
                            for j, step in enumerate(steps, 1):
                                f.write(f"{j}. {step}\n")
                            f.write("\n")
                
                # Tag analysis
                if "tag_analysis" in results:
                    tag_analysis = results["tag_analysis"]
                    f.write("## Tag Analysis\n\n")
                    
                    if "consistency_score" in tag_analysis:
                        f.write(f"**Consistency Score**: {tag_analysis['consistency_score']}\n\n")
                    
                    if "well_used_tags" in tag_analysis and tag_analysis["well_used_tags"]:
                        f.write("### Well-Used Tags\n\n")
                        for tag in tag_analysis["well_used_tags"]:
                            f.write(f"- {tag}\n")
                        f.write("\n")
                    
                    if "inconsistent_tags" in tag_analysis and tag_analysis["inconsistent_tags"]:
                        f.write("### Inconsistent Tags\n\n")
                        for tag in tag_analysis["inconsistent_tags"]:
                            f.write(f"- {tag}\n")
                        f.write("\n")
                    
                    if "recommended_taxonomy" in tag_analysis:
                        f.write("### Recommended Taxonomy\n\n")
                        f.write(f"{tag_analysis['recommended_taxonomy']}\n\n")
                
                # Customer journey
                if "customer_journey" in results and results["customer_journey"]:
                    f.write("## Customer Journey Mapping\n\n")
                    for journey in results["customer_journey"]:
                        segment = journey.get("journey_segment", "Unnamed Segment")
                        f.write(f"### {segment}\n\n")
                        
                        if "entry_points" in journey and journey["entry_points"]:
                            f.write("#### Entry Points\n\n")
                            for point in journey["entry_points"]:
                                f.write(f"- {point}\n")
                            f.write("\n")
                        
                        if "flow_through" in journey:
                            f.write("#### Customer Flow\n\n")
                            f.write(f"{journey['flow_through']}\n\n")
                        
                        if "exit_points" in journey and journey["exit_points"]:
                            f.write("#### Exit Points\n\n")
                            for point in journey["exit_points"]:
                                f.write(f"- {point}\n")
                            f.write("\n")
                        
                        if "optimization_opportunities" in journey and journey["optimization_opportunities"]:
                            f.write("#### Optimization Opportunities\n\n")
                            for opportunity in journey["optimization_opportunities"]:
                                f.write(f"- {opportunity}\n")
                            f.write("\n")
                
                # Cross-entity correlations
                if "cross_entity_correlations" in results and results["cross_entity_correlations"]:
                    f.write("## Cross-Entity Correlations\n\n")
                    for correlation in results["cross_entity_correlations"]:
                        entities = correlation.get("entities", [])
                        relationship = correlation.get("relationship", "")
                        impact = correlation.get("performance_impact", "")
                        recommendation = correlation.get("recommendation", "")
                        
                        entity_str = " & ".join(entities) if entities else "Cross-Entity"
                        f.write(f"### {entity_str}\n\n")
                        
                        if relationship:
                            f.write(f"**Relationship**: {relationship}\n\n")
                        if impact:
                            f.write(f"**Performance Impact**: {impact}\n\n")
                        if recommendation:
                            f.write(f"**Recommendation**: {recommendation}\n\n")
                
                # Resource allocation
                if "resource_allocation" in results:
                    resource = results["resource_allocation"]
                    f.write("## Resource Allocation\n\n")
                    
                    if "current_allocation" in resource:
                        f.write(f"**Current Allocation**: {resource['current_allocation']}\n\n")
                    
                    if "recommended_shifts" in resource and resource["recommended_shifts"]:
                        f.write("### Recommended Shifts\n\n")
                        for i, shift in enumerate(resource["recommended_shifts"], 1):
                            f.write(f"{i}. {shift}\n")
                        f.write("\n")
                    
                    if "expected_roi" in resource:
                        f.write(f"**Expected ROI**: {resource['expected_roi']}\n\n")
                
                # Add timestamp
                f.write(f"\n\n---\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using Klavicle's AI Analysis")
                
            console.print(f"[green]Markdown report exported to: {filename}[/green]")
        elif export_format == "json":
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            console.print(f"[green]JSON report exported to: {filename}[/green]")
        else:
            console.print(f"[yellow]Export format '{export_format}' not supported.[/yellow]")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AI analysis with sample data")
    parser.add_argument("--provider", choices=["mock", "anthropic", "openai"], default="mock", 
                        help="AI provider to use (default: mock)")
    parser.add_argument("--export", choices=["md", "markdown", "json"], default="md",
                        help="Export format (default: md)")
    
    args = parser.parse_args()
    
    asyncio.run(main(provider=args.provider, export_format=args.export))