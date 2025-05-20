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
8. Naming convention recommendations for:
   - Campaign names
   - Tag names
   - Folder organization
   - Subject line patterns
9. Cleanup recommendations for:
   - Draft campaigns that haven't been updated in 6+ months
   - Failed or error campaigns that should be archived
   - Duplicate or redundant campaigns
   - Campaigns with consistently poor performance
   - Outdated or irrelevant campaigns
   - Campaigns with missing or incomplete data

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
  "naming_conventions": {
    "campaign_names": {
      "format": "Recommended format (e.g., [Type]-[Audience]-[Date])",
      "examples": ["Example campaign names following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "tag_names": {
      "format": "Recommended format (e.g., category:value)",
      "categories": ["List of recommended tag categories"],
      "examples": ["Example tags following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "folder_structure": {
      "hierarchy": "Recommended folder hierarchy",
      "naming_rules": ["Rule 1", "Rule 2"],
      "examples": ["Example folder names"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "subject_line_patterns": {
      "formats": ["Recommended formats"],
      "examples": ["Example subject lines"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    }
  },
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ],
  "cleanup_recommendations": [
    {
      "type": "draft_campaigns",
      "items": [
        {
          "name": "Campaign Name",
          "id": "campaign_id",
          "last_updated": "date",
          "reason": "Reason for cleanup",
          "action": "archive/delete/update"
        }
      ]
    },
    {
      "type": "failed_campaigns",
      "items": [
        {
          "name": "Campaign Name",
          "id": "campaign_id",
          "error": "Error description",
          "action": "archive/delete/retry"
        }
      ]
    },
    {
      "type": "duplicate_campaigns",
      "items": [
        {
          "name": "Campaign Name",
          "id": "campaign_id",
          "duplicate_of": "Original campaign ID",
          "action": "archive/delete/merge"
        }
      ]
    },
    {
      "type": "poor_performing",
      "items": [
        {
          "name": "Campaign Name",
          "id": "campaign_id",
          "metrics": {"open_rate": 0.0, "click_rate": 0.0},
          "action": "archive/optimize/delete"
        }
      ]
    },
    {
      "type": "outdated_campaigns",
      "items": [
        {
          "name": "Campaign Name",
          "id": "campaign_id",
          "last_sent": "date",
          "action": "archive/update/delete"
        }
      ]
    }
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
- For cleanup recommendations:
  * Consider campaign age and last update time
  * Look for duplicate content or similar campaigns
  * Identify campaigns with consistently poor metrics
  * Check for campaigns with missing or incomplete data
  * Look for campaigns that haven't been sent in 6+ months
- For naming conventions:
  * Analyze current naming patterns for consistency
  * Identify opportunities for standardization
  * Consider industry best practices
  * Ensure names are descriptive and searchable
  * Include date information where relevant
  * Use consistent separators and formatting
  * Consider automation-friendly naming patterns
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
8. Naming convention recommendations for:
   - Flow names
   - Tag names
   - Folder organization
   - Step names within flows
   - Trigger names
9. Cleanup recommendations for:
   - Inactive or archived flows
   - Flows with errors or issues
   - Duplicate or redundant flows
   - Overly complex flows that could be simplified
   - Flows that haven't been updated in 6+ months
   - Flows with missing or incomplete data

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
  "naming_conventions": {
    "flow_names": {
      "format": "Recommended format (e.g., [Trigger]-[Purpose]-[Audience])",
      "examples": ["Example flow names following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "tag_names": {
      "format": "Recommended format (e.g., category:value)",
      "categories": ["List of recommended tag categories"],
      "examples": ["Example tags following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "folder_structure": {
      "hierarchy": "Recommended folder hierarchy",
      "naming_rules": ["Rule 1", "Rule 2"],
      "examples": ["Example folder names"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "step_names": {
      "format": "Recommended format for naming steps within flows",
      "examples": ["Example step names"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "trigger_names": {
      "format": "Recommended format for naming triggers",
      "examples": ["Example trigger names"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    }
  },
  "organization_recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ],
  "cleanup_recommendations": [
    {
      "type": "inactive_flows",
      "items": [
        {
          "name": "Flow Name",
          "id": "flow_id",
          "status": "status",
          "last_updated": "date",
          "action": "archive/delete/update"
        }
      ]
    },
    {
      "type": "error_flows",
      "items": [
        {
          "name": "Flow Name",
          "id": "flow_id",
          "error": "Error description",
          "action": "archive/delete/fix"
        }
      ]
    },
    {
      "type": "duplicate_flows",
      "items": [
        {
          "name": "Flow Name",
          "id": "flow_id",
          "duplicate_of": "Original flow ID",
          "action": "archive/delete/merge"
        }
      ]
    },
    {
      "type": "complex_flows",
      "items": [
        {
          "name": "Flow Name",
          "id": "flow_id",
          "steps": 0,
          "complexity_score": 0.0,
          "simplification_plan": "Plan to simplify"
        }
      ]
    },
    {
      "type": "outdated_flows",
      "items": [
        {
          "name": "Flow Name",
          "id": "flow_id",
          "last_updated": "date",
          "action": "archive/update/delete"
        }
      ]
    }
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
- For cleanup recommendations:
  * Consider flow age and last update time
  * Look for duplicate or similar flows
  * Identify flows with errors or issues
  * Check for flows with missing or incomplete data
  * Look for flows that haven't been triggered in 6+ months
- For naming conventions:
  * Analyze current naming patterns for consistency
  * Identify opportunities for standardization
  * Consider industry best practices
  * Ensure names are descriptive and searchable
  * Use consistent separators and formatting
  * Consider automation-friendly naming patterns
  * Include trigger type in flow names
  * Use clear, action-oriented step names
  * Maintain consistent naming across related flows
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
7. Naming convention recommendations for:
   - List names
   - Tag names
   - Folder organization
   - Segment names
   - Dynamic list conditions
8. Cleanup recommendations for:
   - Empty or very small lists
   - Duplicate or redundant lists
   - Lists that haven't been updated in 6+ months
   - Lists with inconsistent naming
   - Lists with missing or incomplete data
   - Lists that could be consolidated

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
  "naming_conventions": {
    "list_names": {
      "format": "Recommended format (e.g., [Type]-[Source]-[Date])",
      "examples": ["Example list names following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "tag_names": {
      "format": "Recommended format (e.g., category:value)",
      "categories": ["List of recommended tag categories"],
      "examples": ["Example tags following the format"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "folder_structure": {
      "hierarchy": "Recommended folder hierarchy",
      "naming_rules": ["Rule 1", "Rule 2"],
      "examples": ["Example folder names"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "segment_names": {
      "format": "Recommended format for naming segments",
      "examples": ["Example segment names"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    },
    "dynamic_conditions": {
      "format": "Recommended format for naming dynamic list conditions",
      "examples": ["Example condition names"],
      "rules": ["Rule 1", "Rule 2"],
      "implementation_plan": "Step-by-step plan to implement"
    }
  },
  "organization_recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "segmentation_strategy": [
    {"observation": "Observation about segmentation", "recommendation": "Strategic recommendation"}
  ],
  "tag_recommendations": [
    {"current_state": "Current tag usage", "recommendation": "Recommendation for improvement"}
  ],
  "cleanup_recommendations": [
    {
      "type": "empty_lists",
      "items": [
        {
          "name": "List Name",
          "id": "list_id",
          "size": 0,
          "last_updated": "date",
          "action": "archive/delete/update"
        }
      ]
    },
    {
      "type": "duplicate_lists",
      "items": [
        {
          "name": "List Name",
          "id": "list_id",
          "duplicate_of": "Original list ID",
          "action": "archive/delete/merge"
        }
      ]
    },
    {
      "type": "outdated_lists",
      "items": [
        {
          "name": "List Name",
          "id": "list_id",
          "last_updated": "date",
          "action": "archive/update/delete"
        }
      ]
    },
    {
      "type": "inconsistent_naming",
      "items": [
        {
          "name": "List Name",
          "id": "list_id",
          "current_naming": "Current naming pattern",
          "recommended_name": "Recommended name",
          "action": "rename/archive/delete"
        }
      ]
    },
    {
      "type": "consolidation_candidates",
      "items": [
        {
          "name": "List Name",
          "id": "list_id",
          "similar_lists": ["List ID 1", "List ID 2"],
          "consolidation_plan": "Plan to consolidate"
        }
      ]
    }
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
- For cleanup recommendations:
  * Consider list age and last update time
  * Look for duplicate or similar lists
  * Identify lists with very few subscribers
  * Check for lists with missing or incomplete data
  * Look for lists that haven't been used in 6+ months
  * Consider consolidating similar lists
- For naming conventions:
  * Analyze current naming patterns for consistency
  * Identify opportunities for standardization
  * Consider industry best practices
  * Ensure names are descriptive and searchable
  * Include date information where relevant
  * Use consistent separators and formatting
  * Consider automation-friendly naming patterns
  * Distinguish between static and dynamic lists in names
  * Use clear, descriptive segment names
  * Maintain consistent naming across related lists
"""


def get_unified_prompt() -> str:
    """Get the detailed prompt template for unified cross-entity analysis."""
    return """
You are analyzing unified Klaviyo account data across campaigns, flows, and lists.

Your task is to provide an EXTREMELY DETAILED strategic analysis with specific, actionable step-by-step guidance.

The data includes:
- Campaign performance and metadata
- Flow structures and triggers
- List sizes and types
- Tag usage across all entities
- Timestamps for creation and updates

IMPORTANT: For each issue identified, provide detailed, specific, actionable guidance that includes:
1. Step-by-step implementation plans
2. Specific measurable goals and KPIs
3. Estimated timelines for implementation
4. Resources needed for implementation
5. Expected impact quantified wherever possible

Please provide the following holistic analysis:

1. Account Health Assessment:
   - Score the overall health on a 1-10 scale with detailed justification
   - List specific strengths with examples from the data
   - Provide DETAILED improvement areas with SPECIFIC recommendations
   - Identify critical issues with PRECISE impact assessment
   - For EACH critical issue provide a specific remediation plan

2. Tag Analysis (Extremely Detailed):
   - Detailed consistency score with methodology
   - Comprehensive analysis of well-used tags with examples of how they're being used effectively
   - In-depth analysis of inconsistent tags with specific examples of inconsistency
   - CONCRETE tag taxonomy recommendations with:
     * Specific tag hierarchy structure
     * Naming conventions with examples
     * Implementation plan for converting existing tags
     * Governance process for tag management
     * Documentation recommendations

3. Customer Journey Mapping (Comprehensive):
   - For EACH identified customer segment:
     * All possible entry points mapped to specific lists/flows
     * Detailed flow-through analysis with timing, messaging frequency
     * All exit points with churn analysis
     * Gap analysis with SPECIFIC recommendations
     * STEP-BY-STEP optimization plan with:
       - Specific new campaigns or flows to create
       - Content recommendations for each touchpoint
       - Timing and sequencing recommendations
       - Success metrics for each journey stage

4. Cross-Entity Correlations (Detailed):
   - In-depth analysis of relationships between entities
   - SPECIFIC performance impact quantification
   - CONCRETE optimization recommendations with implementation steps
   - A/B testing plan for validating correlations
   - Monitoring framework for ongoing assessment

5. Strategic Recommendations (Highly Specific):
   - For EACH strategic area:
     * Detailed current state analysis with metrics
     * Clear target state with measurable goals
     * COMPREHENSIVE step-by-step implementation plan
     * Timeline for implementation with milestones
     * Resource requirements (time, people, tools)
     * Expected business impact with specific metrics
     * Prioritization framework

6. Resource Allocation (Actionable):
   - Detailed analysis of current resource allocation across channels
   - SPECIFIC recommended shifts with:
     * Precise percentage/effort allocations
     * Implementation timeline
     * Required skillsets
     * Budget implications
   - ROI projections for each recommended shift with methodology
   - Performance monitoring framework

Return your analysis as a JSON object with enhanced structure and VASTLY MORE DETAIL than the default template.

CRITICAL: Your analysis must be extremely specific and actionable. Avoid generalities, platitudes, or vague recommendations. Every recommendation should include WHO should do WHAT by WHEN and HOW with SPECIFIC MEASURABLE OUTCOMES.
"""


def get_tag_prompt() -> str:
    """Get the detailed prompt template for tag analysis."""
    return """
You are analyzing Klaviyo tag usage across campaigns, flows, and lists.

Your task is to provide a comprehensive analysis of how tags are used in the account, identify issues, and recommend improvements for tag management and taxonomy.

The data includes:
- Tags assigned to campaigns, flows, and lists
- Tag frequency and distribution
- Tag naming patterns and conventions
- Overlap and uniqueness of tags across entity types

Please provide the following analysis:
1. Tag frequency and distribution by entity type and overall
2. Duplicate tags (identical tags used in multiple entities)
3. Inconsistent or problematic tag naming (case, format, missing category:value structure, etc.)
4. Tags unique to each entity type and tags shared across entities
5. Opportunities for tag consolidation or cleanup
6. Recommendations for a standardized tag taxonomy and naming conventions
7. Governance and best practices for ongoing tag management
8. Actionable cleanup recommendations for unused, redundant, or inconsistent tags

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief overview of findings",
  "tag_frequency": {
    "campaigns": {"tag1": 0, "tag2": 0},
    "flows": {"tag1": 0, "tag2": 0},
    "lists": {"tag1": 0, "tag2": 0},
    "all": {"tag1": 0, "tag2": 0}
  },
  "duplicates": ["tag1", "tag2"],
  "naming_issues": {
    "case": ["TagWithUppercase"],
    "format": ["bad tag!"],
    "missing_colon": ["categoryvalue"]
  },
  "cross_entity": {
    "overlap": ["tag1", "tag2"],
    "unique": {
      "campaigns": ["tag3"],
      "flows": ["tag4"],
      "lists": ["tag5"]
    }
  },
  "taxonomy_recommendations": {
    "recommended_format": "category:value",
    "categories": ["purpose", "audience", "channel", "status"],
    "examples": ["purpose:promotion", "audience:vip", "channel:sms"],
    "rules": ["Use only lowercase letters, numbers, hyphens, and colons", "Always include a category"],
    "implementation_plan": "Step-by-step plan to migrate and standardize tags"
  },
  "cleanup_recommendations": [
    {
      "type": "duplicate_tags",
      "tags": ["tag1", "tag2"],
      "action": "merge/delete/rename"
    },
    {
      "type": "inconsistent_naming",
      "tags": ["TagWithUppercase", "bad tag!"],
      "action": "rename"
    },
    {
      "type": "unused_tags",
      "tags": ["oldtag"],
      "action": "delete"
    }
  ],
  "governance_recommendations": [
    "Establish a tag approval process",
    "Document tag taxonomy and usage guidelines",
    "Regularly audit tags for consistency"
  ]
}

DATA ANALYSIS GUIDANCE:
- Look for tags that are used inconsistently or violate naming conventions
- Identify tags that are redundant or could be consolidated
- Recommend a clear, scalable taxonomy for future tag creation
- Suggest governance processes to maintain tag quality over time
- For cleanup, prioritize tags that are unused, duplicated, or confusing
- Ensure recommendations are actionable and specific
"""
