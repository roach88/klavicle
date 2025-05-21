"""Prompt templates for AI analysis."""


def get_campaign_prompt() -> str:
    """Get the detailed prompt template for campaign analysis."""
    return """
You are analyzing Klaviyo email campaign data. 

Your task is to analyze the performance and patterns of these email campaigns to provide actionable insights.

The data includes:
- Campaign metrics like open rates, click rates, and revenue
- Campaign metadata like send times, subject lines, and tags
- Status information (draft, sent, etc.)

Please provide the following analysis:
1. Key performance insights and trends
2. Anomalies or underperforming campaigns
3. Subject line effectiveness patterns
4. Sending time and frequency patterns
5. Specific recommendations for improvement
6. Suggested A/B tests or experiments
7. Tag usage and organization recommendations

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief overview of findings",
  "key_metrics": {
    "avg_open_rate": 0.0,
    "avg_click_rate": 0.0,
    "total_revenue": 0.0,
    "campaign_count": 0
  },
  "top_performing": [
    {"name": "Campaign Name", "metric": "open_rate", "value": 0.0, "reasons": ["reason1", "reason2"]}
  ],
  "underperforming": [
    {"name": "Campaign Name", "metric": "open_rate", "value": 0.0, "reasons": ["reason1", "reason2"]}
  ],
  "trends": [
    {"trend": "Description of trend", "evidence": "Evidence for this trend", "impact": "Impact"}
  ],
  "subject_line_insights": [
    {"pattern": "Pattern observed", "effect": "Effect on metrics", "examples": ["example1", "example2"]}
  ],
  "timing_insights": [
    {"pattern": "Pattern observed", "effect": "Effect on metrics"}
  ],
  "recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "experiments": [
    {"hypothesis": "Hypothesis to test", "test_design": "How to set up the test", "metrics_to_track": ["metric1", "metric2"]}
  ],
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ]
}

DATA ANALYSIS GUIDANCE:
- When analyzing open rates, industry averages are typically 15-25% for most sectors
- Click rates typically average 2-5% for marketing emails
- Look for correlations between subject line length/content and open rates
- Analyze if there's a relationship between send time and performance
- Identify if shorter or longer campaigns perform better
- Check if specific types of campaigns consistently outperform others
- Look for seasonal patterns in performance
- Identify if there are particular days of the week that show better performance
"""


def get_flow_prompt() -> str:
    """Get the detailed prompt template for flow analysis."""
    return """
You are analyzing Klaviyo flow data. 

Your task is to analyze these automation flows to provide actionable insights on their structure and effectiveness.

The data includes:
- Flow status and trigger types
- Flow components (emails, SMS, time delays)
- Performance metrics where available
- Tag information
- Creation and update timestamps

Please provide the following analysis:
1. Flow structure patterns and insights
2. Flow trigger distribution and effectiveness
3. Channel usage patterns (email vs SMS)
4. Flow complexity and potential simplification opportunities
5. Flow organization recommendations
6. Maintenance and update needs
7. Tag usage recommendations

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief overview of findings",
  "key_metrics": {
    "total_flows": 0,
    "active_flows": 0,
    "avg_steps_per_flow": 0.0
  },
  "trigger_analysis": [
    {"trigger_type": "Type", "count": 0, "percentage": 0.0, "effectiveness": "Analysis of effectiveness"}
  ],
  "channel_usage": {
    "email_count": 0,
    "sms_count": 0,
    "email_percentage": 0.0,
    "sms_percentage": 0.0,
    "insights": "Insights about channel balance"
  },
  "complexity_analysis": [
    {"flow_name": "Flow Name", "steps": 0, "complexity": "High/Medium/Low", "simplification": "Suggestion"}
  ],
  "staleness": [
    {"flow_name": "Flow Name", "days_since_update": 0, "recommendation": "Update recommendation"}
  ],
  "organization_recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ]
}

DATA ANALYSIS GUIDANCE:
- Flows with more than 10 steps may be overly complex and confusing
- Abandoned cart flows typically perform best when they have 2-3 messages spaced 4-24 hours apart
- Welcome series typically perform best with 3-5 messages over 1-2 weeks
- Flows that haven't been updated in 6+ months should be reviewed for relevance
- Time delays are most effective when they account for typical customer behavior cycles
- SMS messages should be used strategically, not just duplicating email content
- Look for opportunities to segment flows more effectively
- Check for redundant flows that could be consolidated
"""


def get_list_prompt() -> str:
    """Get the detailed prompt template for list analysis."""
    return """
You are analyzing Klaviyo list data.

Your task is to analyze these subscriber lists to provide actionable insights on list management and segmentation.

The data includes:
- List sizes and growth patterns
- Static vs dynamic list information
- List organization (folders, tags)
- Creation and update timestamps

Please provide the following analysis:
1. List size distribution and insights
2. Static vs dynamic list usage patterns
3. List freshness and maintenance needs
4. List organization recommendations
5. Segmentation strategy insights
6. Tag usage recommendations

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief overview of findings",
  "key_metrics": {
    "total_lists": 0,
    "total_profiles": 0,
    "avg_list_size": 0,
    "static_lists_percentage": 0.0,
    "dynamic_lists_percentage": 0.0
  },
  "size_distribution": {
    "empty": 0,
    "small": 0,
    "medium": 0,
    "large": 0,
    "insights": "Insights about size distribution"
  },
  "type_analysis": {
    "static_count": 0,
    "dynamic_count": 0,
    "recommendations": "Recommendations for list type usage"
  },
  "freshness_analysis": [
    {"list_name": "List Name", "days_since_update": 0, "recommendation": "Recommendation"}
  ],
  "organization_recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "segmentation_strategy": [
    {"observation": "Observation about segmentation", "recommendation": "Strategic recommendation"}
  ],
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ]
}

DATA ANALYSIS GUIDANCE:
- Empty lists (0 subscribers) should typically be removed unless they're new
- Most accounts should have a mix of static and dynamic lists
- Dynamic lists should be used for ongoing segmentation based on behavior
- Static lists are best for one-time imports or specific campaign targets
- Lists that haven't been updated in 6+ months may need cleanup
- Look for opportunities to consolidate similar lists
- Check for logic in how lists are organized in folders
- Analyze whether there's a clear naming convention
- Consider if tags are used consistently across lists
- Identify if there are lists that should be segmented further
"""


def get_unified_prompt() -> str:
    """Get the detailed prompt template for unified cross-entity analysis."""
    return """
You are analyzing unified Klaviyo account data across campaigns, flows, and lists.

Your task is to analyze the relationships and patterns across these different entities to provide strategic insights.

The data includes:
- Campaign performance and metadata
- Flow structures and triggers
- List sizes and types
- Tag usage across all entities
- Timestamps for creation and updates

Please provide the following holistic analysis:
1. Cross-entity tag usage patterns and inconsistencies
2. Customer journey mapping across different entities
3. Performance correlation between lists, flows, and campaigns
4. Strategic recommendations for the entire Klaviyo account
5. Resource allocation guidance across different marketing channels
6. Overall account health assessment

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief strategic overview of the account",
  "account_health": {
    "score": 0,  // 1-10 scale
    "strengths": ["strength1", "strength2"],
    "areas_for_improvement": ["area1", "area2"],
    "critical_issues": ["issue1", "issue2"]
  },
  "tag_analysis": {
    "consistency_score": 0.0,  // 0-1 scale
    "well_used_tags": ["tag1", "tag2"],
    "inconsistent_tags": ["tag3", "tag4"],
    "recommended_taxonomy": "Recommendation for tag structure"
  },
  "customer_journey": [
    {
      "journey_segment": "Segment name",
      "entry_points": ["point1", "point2"],
      "flow_through": "Description of customer movement",
      "exit_points": ["point1", "point2"],
      "optimization_opportunities": ["opportunity1", "opportunity2"]
    }
  ],
  "cross_entity_correlations": [
    {
      "entities": ["Entity1", "Entity2"],
      "relationship": "Description of relationship",
      "performance_impact": "Impact on performance",
      "recommendation": "Recommendation to optimize"
    }
  ],
  "strategic_recommendations": [
    {
      "area": "Strategic area",
      "current_state": "Current situation",
      "target_state": "Desired outcome",
      "steps": ["step1", "step2"],
      "expected_impact": "Expected business impact",
      "priority": "High/Medium/Low"
    }
  ],
  "resource_allocation": {
    "current_allocation": "Description of current resource use",
    "recommended_shifts": ["shift1", "shift2"],
    "expected_roi": "Expected return on reallocation"
  }
}

DATA ANALYSIS GUIDANCE:
- Look for consistency in how tags are used across campaigns, flows, and lists
- Identify gaps in the customer journey where new flows or campaigns could be added
- Check if lists are appropriately targeted by campaigns and flows
- Analyze whether there's alignment between campaign content and flow content
- Identify underutilized channels or message types
- Look for redundancies across different marketing activities
- Check for balance between acquisition, engagement, and retention efforts
- Identify opportunities to create more cohesive customer experiences
- Analyze whether resources are appropriately allocated across different marketing activities
- Look for strategic opportunities to consolidate or expand different marketing initiatives
"""