"""AI-powered analytics for Klaviyo data."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Literal, Optional, Union

import aiohttp
from rich.console import Console

from ..config import get_config
from .mock_analyzer import MockAIAnalyzer

# Configure logging
logger = logging.getLogger(__name__)
console = Console()

# Define provider types
ProviderType = Literal["openai", "anthropic", "mock"]


class AIAnalyzer:
    """Provides AI-powered analysis of Klaviyo data."""

    def __init__(
        self,
        provider: ProviderType = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize AI analyzer with desired provider and settings.

        Args:
            provider: AI service provider ("openai", "anthropic", or "mock")
            api_key: API key for the selected provider (falls back to environment variables)
            model: Specific model to use (defaults to appropriate model per provider)
        """
        self.provider = provider
        self._setup_provider(api_key, model)
        self.console = Console()

    def _setup_provider(self, api_key: Optional[str], model: Optional[str]) -> None:
        """
        Configure the selected AI provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
        """
        # Get configuration manager
        config = get_config()

        if self.provider == "openai":
            # Use provided key, or get from config/env
            self.api_key = api_key or config.get_ai_provider_api_key("openai")
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = model or config.get_ai_provider_model("openai")
            if not self.api_key:
                logger.warning(
                    "No OpenAI API key provided. Use set-api-key command or set OPENAI_API_KEY environment variable."
                )
        elif self.provider == "anthropic":
            # Use provided key, or get from config/env
            self.api_key = api_key or config.get_ai_provider_api_key("anthropic")
            self.api_url = "https://api.anthropic.com/v1/messages"
            self.model = model or config.get_ai_provider_model("anthropic")
            if not self.api_key:
                logger.warning(
                    "No Anthropic API key provided. Use set-api-key command or set ANTHROPIC_API_KEY environment variable."
                )
        elif self.provider == "mock":
            # Mock provider for testing without API calls
            self.api_key = "mock_key"
            self.api_url = "mock://api.example.com"
            self.model = "mock-model"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def analyze_data(
        self,
        data_type: str,
        data: Union[str, Dict, List],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze Klaviyo data using AI and return structured insights.

        Args:
            data_type: Type of data being analyzed ("campaigns", "flows", "lists", etc.)
            data: The data to analyze (JSON string or Python dict/list)
            context: Optional additional context or instructions for analysis

        Returns:
            Dict containing structured analysis results
        """
        # Convert data to string if it's a dict or list
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        else:
            data_str = data

        # Generate the appropriate prompt
        prompt = self._generate_prompt(data_type, data_str, context)

        # Query the AI provider
        try:
            # Pass data_type for better mock responses
            response = await self._query_ai(prompt, data_type)
            # Parse the response into a structured format
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            return {
                "error": str(e),
                "summary": "AI analysis failed. See error for details.",
                "recommendations": [],
            }

    def _generate_prompt(
        self, data_type: str, data: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an appropriate prompt for the given data type.

        Args:
            data_type: Type of data being analyzed
            data: The data to analyze as a string
            context: Optional additional context or instructions

        Returns:
            Formatted prompt string
        """
        # Start with a base prompt appropriate for the data type
        if data_type == "campaigns":
            base_prompt = self._get_campaign_prompt_template()
        elif data_type == "flows":
            base_prompt = self._get_flow_prompt_template()
        elif data_type == "lists":
            base_prompt = self._get_list_prompt_template()
        elif data_type == "unified":
            base_prompt = self._get_unified_prompt_template()
        else:
            base_prompt = self._get_generic_prompt_template()

        # Add context-specific instructions if provided
        if context:
            context_str = "\n\nAdditional context and instructions:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            base_prompt += context_str

        # Add the data
        # Limit data size to avoid token limits
        data_preview = data[:10000]  # Limit to 10K chars for preview
        full_prompt = (
            f"{base_prompt}\n\n"
            f"DATA (potentially truncated for preview):\n```json\n{data_preview}\n```\n\n"
            "Provide your analysis in JSON format as specified in the instructions above."
        )

        return full_prompt

    def _get_campaign_prompt_template(self) -> str:
        """Return the prompt template for campaign analysis."""
        from .prompts import get_campaign_prompt

        return get_campaign_prompt()

    def _get_flow_prompt_template(self) -> str:
        """Return the prompt template for flow analysis."""
        from .prompts import get_flow_prompt

        return get_flow_prompt()

    def _get_list_prompt_template(self) -> str:
        """Return the prompt template for list analysis."""
        from .prompts import get_list_prompt

        return get_list_prompt()

    def _get_unified_prompt_template(self) -> str:
        """Return the prompt template for unified cross-entity analysis."""
        from .prompts import get_unified_prompt

        return get_unified_prompt()

    def _get_generic_prompt_template(self) -> str:
        """Return a generic prompt template for unknown data types."""
        return """
You are analyzing Klaviyo marketing data.

Your task is to analyze this data to provide actionable insights and recommendations.

Please provide the following analysis:
1. Key patterns and insights from the data
2. Areas of strength in the current approach
3. Areas for improvement or optimization
4. Specific recommendations for enhancement
5. Suggested experiments or tests

Return your analysis as a JSON object with the following structure:
{
  "summary": "Brief overview of findings",
  "key_insights": [
    {"insight": "Description of insight", "evidence": "Evidence for this insight", "impact": "Business impact"}
  ],
  "strengths": [
    {"area": "Area of strength", "details": "Details about this strength", "leverage_suggestion": "How to further leverage"}
  ],
  "improvement_areas": [
    {"area": "Area for improvement", "issue": "Description of issue", "opportunity": "Opportunity size"}
  ],
  "recommendations": [
    {"area": "Area of improvement", "recommendation": "Specific recommendation", "expected_impact": "Expected impact"}
  ],
  "experiments": [
    {"hypothesis": "Hypothesis to test", "test_design": "How to set up the test", "metrics_to_track": ["metric1", "metric2"]}
  ]
}
"""

    async def _query_ai(self, prompt: str, data_type: str = "generic") -> str:
        """
        Send a query to the AI provider and get the response.

        Args:
            prompt: The prompt to send to the AI
            data_type: Type of data being analyzed (used for mock responses)

        Returns:
            Raw response text from the AI
        """
        if self.provider == "mock":
            # Extract data from the prompt for better mock responses
            data_json = None

            # Try to extract the data from the prompt
            try:
                # Look for JSON data in the prompt
                if "```json" in prompt:
                    data_parts = prompt.split("```json")
                    if len(data_parts) > 1:
                        json_text = data_parts[1].split("```")[0]
                        data_json = json_text.strip()
            except Exception:
                # If extraction fails, proceed without data
                pass

            # Return enhanced mock response for testing
            parsed_data = None
            if data_json is not None:
                try:
                    parsed_data = json.loads(data_json)
                except Exception:
                    parsed_data = None
            return self._get_mock_response(data_type, parsed_data)

        headers = self._get_provider_headers()
        data = self._get_provider_payload(prompt)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API returned {response.status}: {error_text}")

                    result = await response.json()
                    return self._extract_response_text(result)
            except asyncio.TimeoutError:
                raise Exception("Request to AI provider timed out")
            except Exception as e:
                raise Exception(f"Error querying AI provider: {str(e)}")

    def _get_provider_headers(self) -> Dict[str, str]:
        """Get the appropriate headers for the configured provider."""
        if self.provider == "openai":
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
        elif self.provider == "anthropic":
            return {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key or "",
                "anthropic-version": "2023-06-01",
            }
        else:
            return {"Content-Type": "application/json"}

    def _get_provider_payload(self, prompt: str) -> Dict[str, Any]:
        """Get the appropriate request payload for the configured provider."""
        if self.provider == "openai":
            return {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,  # Lower temperature for more deterministic outputs
                "response_format": {"type": "json_object"},  # Request JSON response
            }
        elif self.provider == "anthropic":
            return {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4000,
            }
        else:
            return {"prompt": prompt}

    def _extract_response_text(self, response_json: Dict[str, Any]) -> str:
        """Extract the response text from the provider-specific JSON response."""
        if self.provider == "openai":
            return response_json["choices"][0]["message"]["content"]
        elif self.provider == "anthropic":
            return response_json["content"][0]["text"]
        else:
            return str(response_json)

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the AI response text into a structured format.

        Args:
            response_text: Raw response from the AI

        Returns:
            Structured dict of analysis results
        """
        try:
            # Try to parse the response as JSON
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from the text
            try:
                # Look for JSON between ``` markers
                json_text = response_text.split("```json")[1].split("```")[0]
                result = json.loads(json_text.strip())
                return result
            except (IndexError, json.JSONDecodeError):
                # Return a simplified dict with the raw text
                return {
                    "error": "Failed to parse AI response as JSON",
                    "summary": "The AI response couldn't be structured properly.",
                    "raw_response": response_text,
                }

    def _get_mock_response(
        self, data_type: str = "generic", data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Return an enhanced mock response for testing without API calls.

        Args:
            data_type: Type of data being analyzed
            data: Optional data to use for generating more realistic mock responses

        Returns:
            Mock analysis results as a JSON string
        """
        # Create a mock analyzer instance
        mock_analyzer = MockAIAnalyzer()

        # Parse data from string if needed
        parsed_data = None
        if data is not None and isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                pass
        else:
            parsed_data = data

        # Get appropriate mock response
        mock_response = mock_analyzer.get_mock_response(data_type, parsed_data)

        # Convert to JSON string
        return json.dumps(mock_response, indent=2)

    def format_insights_for_display(self, insights: Dict[str, Any]) -> None:
        """
        Format AI insights for console display using rich.

        Args:
            insights: The structured insights dict returned from analyze_data
        """
        # Check for error
        if "error" in insights:
            self.console.print(
                f"[bold red]Error during AI analysis:[/bold red] {insights['error']}"
            )
            return

        # Print summary
        self.console.print("\n[bold blue]AI Analysis Summary[/bold blue]")
        self.console.print(insights.get("summary", "No summary provided."))

        # Print key metrics if available
        if "key_metrics" in insights:
            self.console.print("\n[bold blue]Key Metrics[/bold blue]")
            for metric, value in insights["key_metrics"].items():
                self.console.print(f"• {metric.replace('_', ' ').title()}: {value}")

        # Print recommendations (higher priority display)
        if "recommendations" in insights:
            self.console.print("\n[bold blue]Recommendations[/bold blue]")
            for i, rec in enumerate(insights["recommendations"], 1):
                area = rec.get("area", "General")
                recommendation = rec.get("recommendation", "No recommendation provided")
                impact = rec.get("expected_impact", "Unknown")
                self.console.print(
                    f"{i}. [bold]{area}:[/bold] {recommendation} [italic]({impact} impact)[/italic]"
                )

        # Handle account health section for unified analysis
        if "account_health" in insights:
            self.console.print("\n[bold blue]Account Health[/bold blue]")
            score = insights["account_health"].get("score", "N/A")
            self.console.print(f"• Overall Score: {score}/10")

            # Print strengths
            if (
                "strengths" in insights["account_health"]
                and insights["account_health"]["strengths"]
            ):
                self.console.print("• [bold]Strengths:[/bold]")
                for item in insights["account_health"]["strengths"]:
                    self.console.print(f"  - {item}")

            # Print areas for improvement
            if (
                "areas_for_improvement" in insights["account_health"]
                and insights["account_health"]["areas_for_improvement"]
            ):
                self.console.print("• [bold]Areas for Improvement:[/bold]")
                for item in insights["account_health"]["areas_for_improvement"]:
                    self.console.print(f"  - {item}")

            # Print critical issues
            if (
                "critical_issues" in insights["account_health"]
                and insights["account_health"]["critical_issues"]
            ):
                self.console.print("• [bold]Critical Issues:[/bold]")
                for item in insights["account_health"]["critical_issues"]:
                    self.console.print(f"  - {item}")

        # Handle strategic recommendations for unified analysis
        if "strategic_recommendations" in insights:
            self.console.print("\n[bold blue]Strategic Recommendations[/bold blue]")
            for i, rec in enumerate(insights["strategic_recommendations"], 1):
                area = rec.get("area", "General")
                current = rec.get("current_state", "")
                target = rec.get("target_state", "")
                priority = rec.get("priority", "Medium")

                self.console.print(
                    f"{i}. [bold]{area}[/bold] ([italic]{priority} priority[/italic])"
                )
                if current:
                    self.console.print(f"   Current: {current}")
                if target:
                    self.console.print(f"   Target: {target}")

                # Print steps
                if "steps" in rec and rec["steps"]:
                    self.console.print("   Steps:")
                    for step in rec["steps"]:
                        self.console.print(f"   - {step}")

        # Print other sections based on their presence
        for section_name, section_title in [
            ("key_insights", "Key Insights"),
            ("top_performing", "Top Performing Campaigns"),
            ("underperforming", "Underperforming Campaigns"),
            ("trends", "Trends"),
            ("subject_line_insights", "Subject Line Insights"),
            ("timing_insights", "Timing Insights"),
            ("trigger_analysis", "Trigger Analysis"),
            ("channel_usage", "Channel Usage"),
            ("complexity_analysis", "Flow Complexity Analysis"),
            ("staleness", "Content Staleness"),
            ("size_distribution", "List Size Distribution"),
            ("type_analysis", "List Type Analysis"),
            ("freshness_analysis", "List Freshness Analysis"),
            ("segmentation_strategy", "Segmentation Strategy"),
            ("organization_recommendations", "Organization Recommendations"),
            ("tag_analysis", "Tag Analysis"),
            ("customer_journey", "Customer Journey Mapping"),
            ("cross_entity_correlations", "Cross-Entity Correlations"),
            ("experiments", "Suggested Experiments"),
            ("tag_recommendations", "Tag Recommendations"),
            ("resource_allocation", "Resource Allocation"),
        ]:
            if section_name in insights and insights[section_name]:
                self.console.print(f"\n[bold blue]{section_title}[/bold blue]")

                # Handle section-specific formatting
                if section_name == "channel_usage" and isinstance(
                    insights[section_name], dict
                ):
                    # Special handling for channel_usage which is a dict, not a list
                    channel_data = insights[section_name]
                    for k, v in channel_data.items():
                        if k != "insights":  # Handle insights separately
                            self.console.print(f"• {k.replace('_', ' ').title()}: {v}")
                    if "insights" in channel_data:
                        self.console.print(
                            f"\n• [bold]Insights:[/bold] {channel_data['insights']}"
                        )
                elif section_name == "resource_allocation" and isinstance(
                    insights[section_name], dict
                ):
                    # Special handling for resource_allocation
                    resource_data = insights[section_name]
                    if "current_allocation" in resource_data:
                        self.console.print(
                            f"• [bold]Current Allocation:[/bold] {resource_data['current_allocation']}"
                        )
                    if (
                        "recommended_shifts" in resource_data
                        and resource_data["recommended_shifts"]
                    ):
                        self.console.print("• [bold]Recommended Shifts:[/bold]")
                        for shift in resource_data["recommended_shifts"]:
                            self.console.print(f"  - {shift}")
                    if "expected_roi" in resource_data:
                        self.console.print(
                            f"• [bold]Expected ROI:[/bold] {resource_data['expected_roi']}"
                        )
                elif section_name == "size_distribution" and isinstance(
                    insights[section_name], dict
                ):
                    # Special handling for size_distribution
                    size_data = insights[section_name]
                    for k, v in size_data.items():
                        if k != "insights":  # Handle insights separately
                            self.console.print(f"• {k.replace('_', ' ').title()}: {v}")
                    if "insights" in size_data:
                        self.console.print(
                            f"\n• [bold]Insights:[/bold] {size_data['insights']}"
                        )
                elif section_name == "type_analysis" and isinstance(
                    insights[section_name], dict
                ):
                    # Special handling for type_analysis
                    type_data = insights[section_name]
                    for k, v in type_data.items():
                        if k != "recommendations":  # Handle recommendations separately
                            self.console.print(f"• {k.replace('_', ' ').title()}: {v}")
                    if "recommendations" in type_data:
                        self.console.print(
                            f"\n• [bold]Recommendations:[/bold] {type_data['recommendations']}"
                        )
                else:
                    # Standard handling for list-type sections
                    for i, item in enumerate(insights[section_name], 1):
                        if isinstance(item, dict):
                            # Get a key to use as the main point (prioritizing certain keys)
                            main_key = None
                            for priority_key in [
                                "area",
                                "insight",
                                "trend",
                                "pattern",
                                "name",
                                "flow_name",
                                "list_name",
                                "trigger_type",
                                "journey_segment",
                            ]:
                                if priority_key in item:
                                    main_key = priority_key
                                    break

                            if main_key is None:
                                # Get the first key if no priority key found
                                main_key = next(iter(item))

                            main_value = item.get(main_key)
                            self.console.print(f"• [bold]{main_value}[/bold]")

                            # Print the rest of the details indented
                            for k, v in item.items():
                                if k != main_key:
                                    if isinstance(v, list):
                                        self.console.print(
                                            f"  - {k.replace('_', ' ').title()}: {', '.join(str(x) for x in v)}"
                                        )
                                    else:
                                        self.console.print(
                                            f"  - {k.replace('_', ' ').title()}: {v}"
                                        )
                        else:
                            self.console.print(f"• {item}")
