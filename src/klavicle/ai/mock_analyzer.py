"""Mock AI analyzer for testing and development."""

import json
from typing import Any, Dict, List, Optional


class MockAIAnalyzer:
    """Provides mock AI analysis responses for testing and development."""

    def get_mock_response(self, data_type: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a mock AI response based on the data type.

        Args:
            data_type: Type of data being analyzed ("campaigns", "flows", "lists", "unified")
            data: Optional data to use for generating more realistic mock responses

        Returns:
            Mock analysis results as a dictionary
        """
        if data_type == "campaigns":
            return self._get_campaigns_mock_response(data)
        elif data_type == "flows":
            return self._get_flows_mock_response(data)
        elif data_type == "lists":
            return self._get_lists_mock_response(data)
        elif data_type == "unified":
            return self._get_unified_mock_response(data)
        else:
            # Generic mock response
            return {
                "summary": f"This is a mock AI analysis for {data_type} data.",
                "key_insights": [
                    {"insight": "Mock insight 1", "evidence": "Mock evidence", "impact": "High"},
                    {"insight": "Mock insight 2", "evidence": "Mock evidence", "impact": "Medium"}
                ],
                "recommendations": [
                    {"area": "Testing", "recommendation": "This is a test recommendation", "expected_impact": "Low"}
                ]
            }

    def _get_campaigns_mock_response(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a realistic mock response for campaign analysis."""
        # Count campaigns if data is provided
        campaign_count = 0
        if data and isinstance(data, dict) and "campaigns" in data:
            campaign_count = len(data.get("campaigns", []))

        return {
            "summary": f"Analysis of {campaign_count or 'your'} campaigns shows good overall performance with opportunities for improvement in subject lines and send timing. Open rates are generally above industry average, but click-through rates could be improved. Some campaigns significantly outperform others, suggesting opportunities to identify and replicate successful patterns.",
            "key_metrics": {
                "avg_open_rate": 24.6,
                "avg_click_rate": 3.2,
                "total_revenue": 12450.75,
                "campaign_count": campaign_count or 15
            },
            "top_performing": [
                {"name": "Summer Sale Announcement", "metric": "open_rate", "value": 32.7, "reasons": ["Clear value proposition in subject", "Sent during optimal time window", "Strong visuals"]},
                {"name": "Limited Time Offer", "metric": "revenue", "value": 4089.50, "reasons": ["Strong call to action", "Urgency element", "Clear product benefits"]}
            ],
            "underperforming": [
                {"name": "Monthly Newsletter", "metric": "click_rate", "value": 1.4, "reasons": ["Too many competing CTAs", "Content not sufficiently targeted", "Weak subject line"]},
                {"name": "Product Update", "metric": "open_rate", "value": 12.3, "reasons": ["Vague subject line", "Sent on low-engagement day", "Similar to recent campaigns"]}
            ],
            "trends": [
                {"trend": "Campaigns sent mid-week perform better than those sent on weekends", "evidence": "20% higher open rates on Tuesday-Thursday", "impact": "High"},
                {"trend": "Subject lines with numbers show 15% higher open rates", "evidence": "7 out of 10 top-performing campaigns use numbers in subject lines", "impact": "Medium"}
            ],
            "subject_line_insights": [
                {"pattern": "Including recipient's first name", "effect": "+18% open rate on average", "examples": ["Your Spring Collection", "Tyler's Shopping Cart"]},
                {"pattern": "Using questions", "effect": "+12% click rate on average", "examples": ["Ready to upgrade?", "Have you seen our new collection?"]}
            ],
            "timing_insights": [
                {"pattern": "Morning sends (8-10am) outperform evening", "effect": "+22% engagement metrics"},
                {"pattern": "Tuesday and Wednesday show highest conversion rates", "effect": "2.3x weekend rates"}
            ],
            "recommendations": [
                {"area": "Subject Lines", "recommendation": "Test more personalized and question-based subject lines", "expected_impact": "Medium"},
                {"area": "Send Timing", "recommendation": "Shift campaign sends to Tuesday-Thursday mornings", "expected_impact": "High"},
                {"area": "Content Structure", "recommendation": "Reduce number of CTAs per campaign to focus user attention", "expected_impact": "Medium"}
            ],
            "experiments": [
                {"hypothesis": "Emojis in subject lines will increase open rates for younger audience segments", "test_design": "A/B test with identical content but emoji vs. no emoji subject lines", "metrics_to_track": ["open_rate", "click_rate", "conversion_rate"]},
                {"hypothesis": "More concise email content will improve click-through rates", "test_design": "Test 30% shorter email designs against current templates", "metrics_to_track": ["click_rate", "time_on_page", "conversion_rate"]}
            ],
            "tag_recommendations": [
                {"current_state": "Inconsistent tag usage across campaigns", "recommendation": "Implement standardized tagging system with campaign type, audience, and goal tags"}
            ]
        }

    def _get_flows_mock_response(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a realistic mock response for flow analysis."""
        # Count flows if data is provided
        flow_count = 0
        active_flows = 0
        if data and isinstance(data, dict) and "flows" in data:
            flows = data.get("flows", [])
            flow_count = len(flows)
            active_flows = sum(1 for flow in flows if flow.get("status") == "active")

        return {
            "summary": f"Analysis of {flow_count or 'your'} automation flows reveals a solid foundation with several opportunities for optimization. Welcome and abandoned cart flows are well-structured, while browse abandonment and re-engagement flows could benefit from refinement. Email is the dominant channel with limited SMS integration.",
            "key_metrics": {
                "total_flows": flow_count or 12,
                "active_flows": active_flows or 8,
                "avg_steps_per_flow": 6.3
            },
            "trigger_analysis": [
                {"trigger_type": "Metric", "count": 5, "percentage": 41.7, "effectiveness": "Highly effective for abandoned cart and browse abandonment flows"},
                {"trigger_type": "List", "count": 4, "percentage": 33.3, "effectiveness": "Effective for welcome series and educational content"},
                {"trigger_type": "Segment", "count": 2, "percentage": 16.7, "effectiveness": "Moderately effective for targeted promotions"},
                {"trigger_type": "Integration", "count": 1, "percentage": 8.3, "effectiveness": "Limited data but shows potential for cross-platform engagement"}
            ],
            "channel_usage": {
                "email_count": 42,
                "sms_count": 8,
                "email_percentage": 84.0,
                "sms_percentage": 16.0,
                "insights": "SMS is underutilized, particularly for time-sensitive notifications where it could improve engagement"
            },
            "complexity_analysis": [
                {"flow_name": "VIP Customer Journey", "steps": 12, "complexity": "High", "simplification": "Consider breaking into 2-3 smaller targeted flows to improve maintainability"},
                {"flow_name": "Abandoned Cart", "steps": 4, "complexity": "Low", "simplification": "No changes needed - well optimized"},
                {"flow_name": "Re-engagement", "steps": 10, "complexity": "Medium", "simplification": "Consolidate similar message steps and remove duplicate delay periods"}
            ],
            "staleness": [
                {"flow_name": "Customer Birthday", "days_since_update": 218, "recommendation": "Review and update creative elements and offers"},
                {"flow_name": "Product Education", "days_since_update": 175, "recommendation": "Update for current product catalog and refresh content"}
            ],
            "organization_recommendations": [
                {"area": "Flow Naming", "recommendation": "Standardize naming convention with format: [Trigger]-[Purpose]-[Audience]", "expected_impact": "Improved management efficiency"},
                {"area": "Flow Structure", "recommendation": "Establish standard templates for common flow types", "expected_impact": "Faster creation and consistent performance"}
            ],
            "tag_recommendations": [
                {"current_state": "Minimal tag usage on flows", "recommendation": "Implement tags for flow purpose, target audience, and update status"}
            ]
        }

    def _get_lists_mock_response(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a realistic mock response for list analysis."""
        # Count lists if data is provided
        list_count = 0
        total_profiles = 0
        if data and isinstance(data, dict) and "lists" in data:
            lists = data.get("lists", [])
            list_count = len(lists)
            total_profiles = sum(list.get("profile_count", 0) for list in lists)

        return {
            "summary": f"Analysis of {list_count or 'your'} lists shows a good mix of static and dynamic lists with some organizational opportunities. Several empty or low-member lists could be consolidated. List naming is inconsistent and folder organization could be improved for easier management.",
            "key_metrics": {
                "total_lists": list_count or 18,
                "total_profiles": total_profiles or 145620,
                "avg_list_size": (total_profiles / list_count) if list_count else 8090,
                "static_lists_percentage": 66.7,
                "dynamic_lists_percentage": 33.3
            },
            "size_distribution": {
                "empty": 3,
                "small": 5,
                "medium": 7,
                "large": 3,
                "insights": "Consider removing or consolidating empty lists, and evaluate why some lists have very low membership"
            },
            "type_analysis": {
                "static_count": 12,
                "dynamic_count": 6,
                "recommendations": "Increase usage of dynamic lists for more automated segmentation, particularly for engagement and purchase behavior"
            },
            "freshness_analysis": [
                {"list_name": "Summer 2022 Promotion", "days_since_update": 325, "recommendation": "Archive or remove this outdated campaign list"},
                {"list_name": "Newsletter Subscribers", "days_since_update": 2, "recommendation": "No action needed - actively maintained"}
            ],
            "organization_recommendations": [
                {"area": "List Naming", "recommendation": "Standardize naming with format: [Purpose]-[Source]-[Date]", "expected_impact": "Improved searchability and organization"},
                {"area": "Folder Structure", "recommendation": "Reorganize into hierarchy: Acquisition > Engagement > Retention > Campaigns > Archive", "expected_impact": "Better list management and clearer organization"}
            ],
            "segmentation_strategy": [
                {"observation": "Limited segmentation by engagement level", "recommendation": "Create dynamic lists for high, medium, and low engagement customers"},
                {"observation": "Product interest segmentation is manual", "recommendation": "Implement behavioral-based dynamic lists for product category interests"}
            ],
            "tag_recommendations": [
                {"current_state": "Inconsistent tag usage with some duplicate concepts", "recommendation": "Implement standardized tag taxonomy with source, purpose, and status tags"}
            ]
        }

    def _get_unified_mock_response(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a realistic mock response for unified cross-entity analysis."""
        # Extract some basic metrics if data is provided
        campaign_count = 0
        flow_count = 0
        list_count = 0
        
        if data and isinstance(data, dict):
            campaign_count = len(data.get("campaigns", []))
            flow_count = len(data.get("flows", []))
            list_count = len(data.get("lists", []))

        return {
            "summary": f"Analysis of your Klaviyo account reveals a solid marketing automation foundation with {campaign_count} campaigns, {flow_count} flows, and {list_count} lists. The account shows strengths in campaign execution but has opportunities in cross-channel coordination and list management. Key recommendations include implementing consistent tagging across entities, improving the welcome-to-purchase customer journey, and developing more nuanced segmentation strategies for targeted messaging.",
            "account_health": {
                "score": 7,
                "strengths": [
                    "Strong campaign execution with above-average open rates",
                    "Well-structured abandoned cart and welcome series flows",
                    "Good balance of static and dynamic lists"
                ],
                "areas_for_improvement": [
                    "Inconsistent tagging and organization across entities",
                    "Limited SMS integration in flows",
                    "Several underutilized or empty lists",
                    "Gaps in the post-purchase customer journey"
                ],
                "critical_issues": [
                    "Several outdated flows that haven't been updated in 6+ months",
                    "Missing re-engagement strategy for lapsed customers"
                ]
            },
            "tag_analysis": {
                "consistency_score": 0.4,
                "well_used_tags": [
                    "promotion",
                    "newsletter",
                    "product-launch"
                ],
                "inconsistent_tags": [
                    "promo/promotion",
                    "welcome/onboarding",
                    "vip/loyalty"
                ],
                "recommended_taxonomy": "Implement category:value format with standardized categories: purpose, audience, channel, campaign, product"
            },
            "customer_journey": [
                {
                    "journey_segment": "New customer onboarding",
                    "entry_points": ["Newsletter signup", "First purchase", "Account creation"],
                    "flow_through": "Good initial welcome but limited educational content and cross-sell opportunities",
                    "exit_points": ["Welcome series completion", "First purchase"],
                    "optimization_opportunities": ["Add product education", "Incorporate progressive profiling", "Introduce loyalty program earlier"]
                },
                {
                    "journey_segment": "Repeat customer nurturing",
                    "entry_points": ["Second purchase", "High engagement with emails"],
                    "flow_through": "Limited personalized recommendations and VIP treatment",
                    "exit_points": ["Purchase completion", "No clear next steps"],
                    "optimization_opportunities": ["Develop tiered engagement strategy", "Implement cross-category recommendations", "Add exclusive content for repeat customers"]
                }
            ],
            "cross_entity_correlations": [
                {
                    "entities": ["Welcome Flow", "New Products List", "Product Announcement Campaigns"],
                    "relationship": "Disconnected messaging strategy across these related touchpoints",
                    "performance_impact": "Lower conversion from new subscribers to repeat customers",
                    "recommendation": "Coordinate messaging across these entities with progressive storytelling"
                },
                {
                    "entities": ["VIP List", "Loyalty Flow", "Special Offer Campaigns"],
                    "relationship": "Inconsistent identification and treatment of high-value customers",
                    "performance_impact": "Missed revenue from best customers and lower customer lifetime value",
                    "recommendation": "Create unified high-value customer strategy with coordinated messaging"
                }
            ],
            "strategic_recommendations": [
                {
                    "area": "Customer Segmentation",
                    "current_state": "Basic segmentation with few dynamic targeting strategies",
                    "target_state": "Advanced behavioral and predictive segmentation",
                    "steps": [
                        "Implement engagement scoring system",
                        "Create product category affinity segments",
                        "Develop purchase frequency and recency segments",
                        "Build predictive churn risk segments"
                    ],
                    "expected_impact": "15-25% improvement in campaign performance and customer retention",
                    "priority": "High"
                },
                {
                    "area": "Channel Integration",
                    "current_state": "Email-dominant with minimal SMS",
                    "target_state": "Coordinated multi-channel approach",
                    "steps": [
                        "Expand SMS in time-sensitive flows",
                        "Develop channel preference tracking",
                        "Implement cross-channel frequency capping",
                        "Create specialized content for each channel"
                    ],
                    "expected_impact": "20-30% increase in overall engagement and 10-15% revenue lift",
                    "priority": "Medium"
                }
            ],
            "resource_allocation": {
                "current_allocation": "Heavy focus on campaign creation with limited optimization of flows and lists",
                "recommended_shifts": [
                    "Reduce one-off campaign frequency by 25% and invest time in flow optimization",
                    "Allocate resources to list cleanup and segmentation strategy",
                    "Invest in better tagging and organization system across all entities"
                ],
                "expected_roi": "Higher long-term engagement and revenue with reduced ongoing effort"
            }
        }