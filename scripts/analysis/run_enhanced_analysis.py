#!/usr/bin/env python
"""
Enhanced AI Analysis Script for Klavicle

This script runs a detailed analysis with enhanced prompts for more specific, 
actionable insights.
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

from src.klavicle.ai.analyzer import AIAnalyzer
from src.klavicle.cli.ai_commands import analyze_impl
from src.klavicle.cli.klaviyo_commands import get_klaviyo_client
from src.klavicle.klaviyo.campaign_analyzer import CampaignAnalyzer
from src.klavicle.klaviyo.flow_analyzer import FlowAnalyzer  
from src.klavicle.klaviyo.list_analyzer import ListAnalyzer

async def run_enhanced_analysis():
    """Run enhanced analysis with detailed instructions."""
    
    # Load enhanced prompt
    enhanced_prompt_path = Path("prompts/enhanced_prompt.txt")
    if not enhanced_prompt_path.exists():
        print("Enhanced prompt file not found. Please create it first.")
        return
        
    with open(enhanced_prompt_path, "r") as f:
        enhanced_instructions = f.read()
    
    # Create context with enhanced instructions
    context = {
        "enhanced_instructions": enhanced_instructions,
        "require_detailed_analysis": True,
        "output_level": "extremely_detailed",
        "include_implementation_steps": True,
        "include_kpis": True,
        "prioritize_recommendations": True
    }
    
    # Set up analysis parameters
    entity_type = "all"
    provider = "anthropic"  # You can change to "openai" if preferred
    export_format = "md"
    sample = False  # Set to True for faster testing
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create outputs directory if it doesn't exist
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    output_filename = outputs_dir / f"enhanced_analysis_{timestamp}.md"
    
    print(f"Running enhanced analysis, output will be saved to {output_filename}")
    
    # Create client and data collectors
    client = get_klaviyo_client()
    
    # Create unified data structure
    unified_data = {}
    
    # Collect all data
    print("Collecting campaign data...")
    campaign_analyzer = CampaignAnalyzer(client)
    campaign_stats = await campaign_analyzer.analyze_all_campaigns()
    campaign_data = [
        {
            "id": stat.id,
            "name": stat.name,
            "status": stat.status,
            "created": stat.created.isoformat() if stat.created else None,
            "updated": stat.updated.isoformat() if stat.updated else None,
            "send_time": stat.send_time.isoformat() if stat.send_time else None,
            "channel": stat.channel,
            "message_type": stat.message_type,
            "subject_line": stat.subject_line,
            "from_email": stat.from_email,
            "from_name": stat.from_name,
            "tags": stat.tags,
            "metrics": {
                "recipient_count": stat.recipient_count,
                "open_rate": stat.open_rate,
                "click_rate": stat.click_rate,
                "revenue": stat.revenue,
            },
        }
        for stat in campaign_stats
    ]
    unified_data["campaigns"] = campaign_data
    
    print("Collecting flow data...")
    flow_analyzer = FlowAnalyzer(client)
    flow_stats = await flow_analyzer.analyze_all_flows()
    flow_data = [
        {
            "id": stat.id,
            "name": stat.name,
            "status": stat.status,
            "archived": stat.archived,
            "created": stat.created.isoformat() if stat.created else None,
            "updated": stat.updated.isoformat() if stat.updated else None,
            "trigger_type": stat.trigger_type,
            "structure": {
                "action_count": stat.action_count,
                "email_count": stat.email_count,
                "sms_count": stat.sms_count,
                "time_delay_count": stat.time_delay_count,
            },
            "tags": stat.tags,
        }
        for stat in flow_stats
    ]
    unified_data["flows"] = flow_data
    
    print("Collecting list data...")
    list_analyzer = ListAnalyzer(client)
    list_stats = await list_analyzer.analyze_all_lists()
    list_data = [
        {
            "id": stat.id,
            "name": stat.name,
            "created": stat.created.isoformat() if stat.created else None,
            "updated": stat.updated.isoformat() if stat.updated else None,
            "profile_count": stat.profile_count,
            "is_dynamic": stat.is_dynamic,
            "folder_name": stat.folder_name,
            "tags": stat.tags,
        }
        for stat in list_stats
    ]
    unified_data["lists"] = list_data
    
    # Create AI analyzer with the specified provider
    ai_analyzer = AIAnalyzer(provider=provider)
    
    print(f"Running enhanced AI analysis using {provider}...")
    data_json = json.dumps(unified_data)
    analysis_results = await ai_analyzer.analyze_data(
        "unified", data_json, context=context
    )
    
    # Generate enhanced markdown export
    print("Generating enhanced markdown export...")
    with open(output_filename, "w") as f:
        f.write(f"# Enhanced AI Analysis Results for Klaviyo Account\n\n")
        f.write(f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
        
        # Add summary
        if "summary" in analysis_results:
            f.write("## Executive Summary\n\n")
            f.write(f"{analysis_results['summary']}\n\n")
        
        # Add account health
        if "account_health" in analysis_results:
            f.write("## Account Health Assessment\n\n")
            
            score = analysis_results["account_health"].get("score", "N/A")
            f.write(f"**Overall Health Score:** {score}/10\n\n")
            
            # Strengths
            if "strengths" in analysis_results["account_health"]:
                f.write("### Strengths\n\n")
                for item in analysis_results["account_health"]["strengths"]:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # Areas for improvement
            if "areas_for_improvement" in analysis_results["account_health"]:
                f.write("### Areas for Improvement\n\n")
                for item in analysis_results["account_health"]["areas_for_improvement"]:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # Critical issues
            if "critical_issues" in analysis_results["account_health"]:
                f.write("### Critical Issues\n\n")
                for item in analysis_results["account_health"]["critical_issues"]:
                    f.write(f"- {item}\n")
                f.write("\n")
                
        # Tag analysis
        if "tag_analysis" in analysis_results:
            f.write("## Tag System Analysis\n\n")
            
            tag_analysis = analysis_results["tag_analysis"]
            
            if "consistency_score" in tag_analysis:
                f.write(f"**Tag Consistency Score:** {tag_analysis['consistency_score']}/1.0\n\n")
            
            if "well_used_tags" in tag_analysis:
                f.write("### Well-Used Tags\n\n")
                for tag in tag_analysis["well_used_tags"]:
                    f.write(f"- {tag}\n")
                f.write("\n")
                
            if "inconsistent_tags" in tag_analysis:
                f.write("### Inconsistently Used Tags\n\n")
                for tag in tag_analysis["inconsistent_tags"]:
                    f.write(f"- {tag}\n")
                f.write("\n")
                
            if "recommended_taxonomy" in tag_analysis:
                f.write("### Recommended Tag Taxonomy\n\n")
                f.write(f"{tag_analysis['recommended_taxonomy']}\n\n")
        
        # Customer journey
        if "customer_journey" in analysis_results:
            f.write("## Customer Journey Analysis\n\n")
            
            for i, journey in enumerate(analysis_results["customer_journey"], 1):
                segment = journey.get("journey_segment", f"Segment {i}")
                f.write(f"### {segment}\n\n")
                
                # Entry points
                if "entry_points" in journey:
                    f.write("#### Entry Points\n\n")
                    for point in journey["entry_points"]:
                        f.write(f"- {point}\n")
                    f.write("\n")
                
                # Flow through
                if "flow_through" in journey:
                    f.write("#### Customer Flow\n\n")
                    f.write(f"{journey['flow_through']}\n\n")
                
                # Exit points
                if "exit_points" in journey:
                    f.write("#### Exit Points\n\n")
                    for point in journey["exit_points"]:
                        f.write(f"- {point}\n")
                    f.write("\n")
                
                # Optimization opportunities
                if "optimization_opportunities" in journey:
                    f.write("#### Optimization Opportunities\n\n")
                    for opportunity in journey["optimization_opportunities"]:
                        f.write(f"- {opportunity}\n")
                    f.write("\n")
        
        # Cross-entity correlations
        if "cross_entity_correlations" in analysis_results:
            f.write("## Cross-Entity Correlations\n\n")
            
            for i, correlation in enumerate(analysis_results["cross_entity_correlations"], 1):
                entities = correlation.get("entities", [])
                entities_str = " & ".join(entities) if entities else f"Correlation {i}"
                
                f.write(f"### {entities_str}\n\n")
                
                if "relationship" in correlation:
                    f.write("**Relationship:** ")
                    f.write(f"{correlation['relationship']}\n\n")
                    
                if "performance_impact" in correlation:
                    f.write("**Performance Impact:** ")
                    f.write(f"{correlation['performance_impact']}\n\n")
                    
                if "recommendation" in correlation:
                    f.write("**Recommendation:** ")
                    f.write(f"{correlation['recommendation']}\n\n")
                    
        # Strategic recommendations
        if "strategic_recommendations" in analysis_results:
            f.write("## Strategic Recommendations\n\n")
            
            for i, rec in enumerate(analysis_results["strategic_recommendations"], 1):
                area = rec.get("area", f"Area {i}")
                priority = rec.get("priority", "Medium")
                
                f.write(f"### {i}. {area} ({priority} Priority)\n\n")
                
                if "current_state" in rec:
                    f.write("**Current State:** ")
                    f.write(f"{rec['current_state']}\n\n")
                    
                if "target_state" in rec:
                    f.write("**Target State:** ")
                    f.write(f"{rec['target_state']}\n\n")
                    
                if "steps" in rec:
                    f.write("**Implementation Steps:**\n\n")
                    for j, step in enumerate(rec["steps"], 1):
                        f.write(f"{j}. {step}\n")
                    f.write("\n")
                    
                if "expected_impact" in rec:
                    f.write("**Expected Impact:** ")
                    f.write(f"{rec['expected_impact']}\n\n")
                    
        # Resource allocation
        if "resource_allocation" in analysis_results:
            f.write("## Resource Allocation\n\n")
            
            resource_data = analysis_results["resource_allocation"]
            
            if "current_allocation" in resource_data:
                f.write("### Current Resource Allocation\n\n")
                f.write(f"{resource_data['current_allocation']}\n\n")
                
            if "recommended_shifts" in resource_data:
                f.write("### Recommended Resource Shifts\n\n")
                for i, shift in enumerate(resource_data["recommended_shifts"], 1):
                    f.write(f"{i}. {shift}\n")
                f.write("\n")
                
            if "expected_roi" in resource_data:
                f.write("### Expected ROI\n\n")
                f.write(f"{resource_data['expected_roi']}\n\n")
                
        # Additional sections based on what's available in the analysis
        for section_name, section_title in [
            ("implementation_plan", "Implementation Plan"),
            ("timeline", "Timeline"),
            ("metrics_tracking", "Metrics & KPIs"),
            ("governance", "Governance & Maintenance"),
        ]:
            if section_name in analysis_results:
                f.write(f"## {section_title}\n\n")
                
                section_data = analysis_results[section_name]
                if isinstance(section_data, list):
                    for item in section_data:
                        if isinstance(item, dict):
                            for key, value in item.items():
                                f.write(f"### {key}\n\n")
                                if isinstance(value, list):
                                    for bullet in value:
                                        f.write(f"- {bullet}\n")
                                else:
                                    f.write(f"{value}\n")
                                f.write("\n")
                        else:
                            f.write(f"- {item}\n")
                    f.write("\n")
                elif isinstance(section_data, dict):
                    for key, value in section_data.items():
                        f.write(f"### {key}\n\n")
                        if isinstance(value, list):
                            for bullet in value:
                                f.write(f"- {bullet}\n")
                        else:
                            f.write(f"{value}\n")
                        f.write("\n")
                else:
                    f.write(f"{section_data}\n\n")
    
    print(f"Enhanced analysis completed and saved to {output_filename}")
    return output_filename

if __name__ == "__main__":
    asyncio.run(run_enhanced_analysis())