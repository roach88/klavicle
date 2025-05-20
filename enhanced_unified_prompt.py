#!/usr/bin/env python
"""
This script updates the unified prompt to provide more detailed analysis.
"""

import os
import sys
from pathlib import Path

# Ensure we can import from src.klavicle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Replace the unified prompt with the enhanced version
enhanced_prompt = """
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

# Path to the prompts.py file
prompts_path = Path("src/klavicle/ai/prompts.py")

# Check if the file exists
if not prompts_path.exists():
    print(f"Error: {prompts_path} not found.")
    sys.exit(1)

# Read the current content
with open(prompts_path, "r") as f:
    content = f.read()

# Find the unified prompt function
start_marker = "def get_unified_prompt() -> str:"
end_marker = "def get_"

# Find the start of the function
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Error: Could not find the unified prompt function.")
    sys.exit(1)

# Find the end of the function (start of the next function)
end_idx = content.find(end_marker, start_idx + len(start_marker))
if end_idx == -1:
    # If there's no next function, go to the end of the file
    end_idx = len(content)

# Extract the function body
func_body = content[start_idx:end_idx]

# Create a backup
backup_path = prompts_path.with_suffix(".py.bak")
with open(backup_path, "w") as f:
    f.write(content)
print(f"Created backup at {backup_path}")

# Replace the function body
new_func_body = f'''def get_unified_prompt() -> str:
    """Get the detailed prompt template for unified cross-entity analysis."""
    return """{enhanced_prompt}"""
'''

new_content = content[:start_idx] + new_func_body + content[end_idx:]

# Write the updated content
with open(prompts_path, "w") as f:
    f.write(new_content)

print(f"Updated the unified prompt in {prompts_path}")
print("\nNow you can run your original command with more detailed analysis:")
print("\nklavicle ai analyze --entity-type=all --provider=anthropic --export-format=md")
print("\nThis will provide a much more detailed and actionable analysis.")