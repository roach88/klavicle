"""AI-powered analytics for Klaviyo data."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Literal, Optional, Union

import aiohttp
from rich.console import Console

from ..config import get_config

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
            response = await self._query_ai(prompt)
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

    async def _query_ai(self, prompt: str) -> str:
        """
        Send a query to the AI provider and get the response.

        Args:
            prompt: The prompt to send to the AI

        Returns:
            Raw response text from the AI
        """
        if self.provider == "mock":
            # Return mock response for testing
            return self._get_mock_response()

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

    def _get_mock_response(self) -> str:
        """Return a mock response for testing without API calls."""
        return """
{
  "summary": "This is a mock AI analysis for testing purposes.",
  "key_insights": [
    {"insight": "Mock insight 1", "evidence": "Mock evidence", "impact": "High"},
    {"insight": "Mock insight 2", "evidence": "Mock evidence", "impact": "Medium"}
  ],
  "recommendations": [
    {"area": "Testing", "recommendation": "This is a test recommendation", "expected_impact": "Low"}
  ]
}
"""

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

        # Print recommendations
        if "recommendations" in insights:
            self.console.print("\n[bold blue]Recommendations[/bold blue]")
            for i, rec in enumerate(insights["recommendations"], 1):
                area = rec.get("area", "General")
                recommendation = rec.get("recommendation", "No recommendation provided")
                impact = rec.get("expected_impact", "Unknown")
                self.console.print(
                    f"{i}. [bold]{area}:[/bold] {recommendation} [italic]({impact} impact)[/italic]"
                )

        # Print other sections based on their presence
        for section_name, section_title in [
            ("key_insights", "Key Insights"),
            ("trends", "Trends"),
            ("experiments", "Suggested Experiments"),
            ("tag_recommendations", "Tag Recommendations"),
        ]:
            if section_name in insights and insights[section_name]:
                self.console.print(f"\n[bold blue]{section_title}[/bold blue]")
                for i, item in enumerate(insights[section_name], 1):
                    if isinstance(item, dict):
                        # Get the first key-value pair to use as the main point
                        key, value = next(iter(item.items()))
                        self.console.print(f"• [bold]{value}[/bold]")
                        # Print the rest of the details indented
                        for k, v in item.items():
                            if k != key:
                                if isinstance(v, list):
                                    self.console.print(
                                        f"  - {k.replace('_', ' ').title()}: {', '.join(v)}"
                                    )
                                else:
                                    self.console.print(
                                        f"  - {k.replace('_', ' ').title()}: {v}"
                                    )
                    else:
                        self.console.print(f"• {item}")
