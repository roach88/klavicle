"""AI-powered analytics for Klaviyo data."""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import aiohttp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from ..config import get_config
from .mock_analyzer import MockAIAnalyzer

# Configure logging
logger = logging.getLogger(__name__)
console = Console()

# Define provider types
ProviderType = Literal["anthropic", "mock"]

# Cache configuration
CACHE_DIR = Path.home() / ".klavicle" / "cache" / "analysis"
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds


class AnalysisCache:
    """Handles caching of analysis results."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, data_type: str, data_hash: str) -> Path:
        """Generate cache file path."""
        return self.cache_dir / f"{data_type}_{data_hash}.json"

    def _hash_data(self, data: Union[str, Dict, List]) -> str:
        """Generate a hash for the data."""
        import hashlib

        if isinstance(data, str):
            data_str = data
        else:
            data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(
        self, data_type: str, data: Union[str, Dict, List]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if available and not expired."""
        data_hash = self._hash_data(data)
        cache_file = self._get_cache_key(data_type, data_hash)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            # Check if cache is expired
            if time.time() - cache_data["timestamp"] > CACHE_EXPIRY:
                cache_file.unlink()
                return None

            return cache_data["results"]
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
            return None

    def set(
        self, data_type: str, data: Union[str, Dict, List], results: Dict[str, Any]
    ) -> None:
        """Cache analysis results."""
        data_hash = self._hash_data(data)
        cache_file = self._get_cache_key(data_type, data_hash)

        try:
            cache_data = {"timestamp": time.time(), "results": results}
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Error writing to cache: {str(e)}")

    def clear(self, data_type: Optional[str] = None) -> None:
        """Clear cache for a specific data type or all types."""
        if data_type:
            pattern = f"{data_type}_*.json"
        else:
            pattern = "*.json"

        for cache_file in self.cache_dir.glob(pattern):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Error clearing cache file {cache_file}: {str(e)}")


class AIAnalyzer:
    """Provides AI-powered analysis of Klaviyo data."""

    def __init__(
        self,
        provider: ProviderType = "mock",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        batch_size: int = 1000,  # Default batch size for large datasets
        max_tokens: int = 100000,  # Default max tokens per request
        use_cache: bool = True,  # Enable/disable caching
        cache_expiry: int = CACHE_EXPIRY,  # Cache expiry in seconds
    ):
        """
        Initialize the AI analyzer.

        Args:
            provider: AI provider to use ("openai", "anthropic", or "mock")
            api_key: Optional API key (if not provided, will use config)
            model: Optional model name (if not provided, will use provider default)
            batch_size: Maximum number of items to process in a single batch
            max_tokens: Maximum tokens to use per request
            use_cache: Whether to use caching for analysis results
            cache_expiry: Cache expiry time in seconds
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self.max_tokens = max_tokens
        self.use_cache = use_cache
        self.cache_expiry = cache_expiry
        self._setup_provider()
        self.console = Console()
        self.cache = AnalysisCache() if use_cache else None
        self._analysis_progress = None

    def _setup_progress(self, total: int, description: str) -> None:
        """Set up progress tracking."""
        self._analysis_progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self._analysis_progress.start()
        self._task_id = self._analysis_progress.add_task(description, total=total)

    def _update_progress(self, advance: int = 1) -> None:
        """Update progress tracking."""
        if self._analysis_progress and hasattr(self, "_task_id"):
            self._analysis_progress.advance(self._task_id, advance)

    def _finish_progress(self) -> None:
        """Finish progress tracking."""
        if self._analysis_progress:
            self._analysis_progress.stop()
            self._analysis_progress = None

    def _setup_provider(self) -> None:
        """Set up the AI provider based on configuration."""
        if self.provider == "anthropic":
            from anthropic import AsyncAnthropic

            self.api_url = "https://api.anthropic.com/v1/messages"
            api_key = self.api_key or get_config().get_ai_provider_api_key("anthropic")
            self.client = AsyncAnthropic(api_key=api_key)
        else:
            # Mock provider
            self.client = None
            self.api_url = None

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.
        This is a rough estimate based on average token length.

        Args:
            text: The text to estimate tokens for

        Returns:
            Estimated number of tokens
        """
        # Rough estimate: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def _should_batch(self, data: Union[str, Dict, List]) -> bool:
        """
        Determine if the data should be processed in batches.

        Args:
            data: The data to check

        Returns:
            True if data should be batched, False otherwise
        """
        if isinstance(data, str):
            return self._estimate_tokens(data) > self.max_tokens
        elif isinstance(data, (dict, list)):
            data_str = json.dumps(data)
            return self._estimate_tokens(data_str) > self.max_tokens
        return False

    def _create_batches(self, data: List[Any]) -> List[List[Any]]:
        """
        Split data into batches, prioritizing data type grouping.

        Args:
            data: List of items to batch

        Returns:
            List of batches
        """
        # First, group by data type if possible
        if data and isinstance(data[0], dict):
            # Group by type if available
            type_groups = {}
            for item in data:
                item_type = item.get("type", "unknown")
                if item_type not in type_groups:
                    type_groups[item_type] = []
                type_groups[item_type].append(item)

            # If we have multiple types, return type-based batches
            if len(type_groups) > 1:
                return list(type_groups.values())

            # If all same type, check if we need to split by size
            if len(data) > self.batch_size:
                return [
                    data[i : i + self.batch_size]
                    for i in range(0, len(data), self.batch_size)
                ]
            return [data]

        # Fallback to size-based batching if we can't group by type
        return [
            data[i : i + self.batch_size] for i in range(0, len(data), self.batch_size)
        ]

    def _filter_by_date_range(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_field: str = "created",
    ) -> List[Dict[str, Any]]:
        """
        Filter data by date range.

        Args:
            data: List of data items to filter
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            date_field: Field name containing the date to filter on

        Returns:
            Filtered list of data items
        """
        if not start_date and not end_date:
            return data

        filtered_data = []
        for item in data:
            item_date = item.get(date_field)
            if not item_date:
                continue

            try:
                if isinstance(item_date, str):
                    item_date = datetime.fromisoformat(item_date.replace("Z", "+00:00"))

                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue

                filtered_data.append(item)
            except (ValueError, TypeError):
                continue

        return filtered_data

    async def analyze_data(
        self,
        data_type: str,
        data: Union[str, Dict, List],
        context: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_field: str = "created",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze Klaviyo data using AI and return structured insights.

        Args:
            data_type: Type of data being analyzed ("campaigns", "flows", "lists", "unified")
            data: The data to analyze (JSON string or Python dict/list)
            context: Optional additional context or instructions for analysis
            start_date: Optional start date for filtering data
            end_date: Optional end date for filtering data
            date_field: Field name containing the date to filter on
            force_refresh: Whether to force a fresh analysis ignoring cache

        Returns:
            Dict containing structured analysis results
        """
        logger.info(f"Starting analysis of {data_type} data")

        # Check cache first if enabled and not forcing refresh
        if self.use_cache and self.cache and not force_refresh:
            cached_results = self.cache.get(data_type, data)
            if cached_results:
                logger.info(f"Using cached results for {data_type} analysis")
                return cached_results

        try:
            # Convert data to dict if it's a string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON string provided: {str(e)}")
                    raise ValueError("Invalid JSON string provided")

            # For unified analysis, use the hybrid approach
            if data_type == "unified" and isinstance(data, dict):
                logger.info("Starting unified analysis using hybrid approach")
                self._setup_progress(3, "Analyzing individual entities...")

                # First analyze individual entities
                individual_results = await self.analyze_individual_entities(
                    data,
                    start_date=start_date,
                    end_date=end_date,
                )

                self._update_progress()
                logger.info("Individual entity analysis complete")

                # Then perform unified analysis
                self._update_progress()
                logger.info("Starting unified analysis synthesis")
                results = await self.analyze_unified(individual_results, data)

                self._finish_progress()

                # Cache results if enabled
                if self.use_cache and self.cache:
                    self.cache.set(data_type, data, results)

                return results

            # For individual entity analysis, use the original approach
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise ValueError("Data must be a string, dict, or list")

            # Apply date filtering if dates are provided
            if start_date or end_date:
                data = self._filter_by_date_range(
                    data, start_date, end_date, date_field
                )

            # Check if we need to batch the data
            if self._should_batch(data):
                logger.info("Data requires batching. Creating batches...")
                batches = self._create_batches(data)
                total_batches = len(batches)
                self._setup_progress(
                    total_batches, f"Processing {total_batches} batches..."
                )

                all_results = []
                for i, batch in enumerate(batches, 1):
                    try:
                        logger.info(f"Processing batch {i}/{total_batches}")
                        batch_str = json.dumps(batch)
                        prompt = self._generate_prompt(data_type, batch_str, context)

                        response = await self._query_ai(prompt, data_type)
                        batch_results = self._parse_response(response)
                        all_results.append(batch_results)
                        self._update_progress()
                    except Exception as e:
                        logger.error(f"Error processing batch {i}: {str(e)}")
                        # Continue with next batch instead of failing completely
                        continue

                self._finish_progress()
                results = self._combine_batch_results(all_results)
            else:
                # Process all data at once
                logger.info("Processing data in single batch")
                data_str = json.dumps(data)
                prompt = self._generate_prompt(data_type, data_str, context)

                try:
                    response = await self._query_ai(prompt, data_type)
                    results = self._parse_response(response)
                except Exception as e:
                    logger.error(f"Error during AI analysis: {str(e)}")
                    return {
                        "error": str(e),
                        "summary": "AI analysis failed. See error for details.",
                        "recommendations": [],
                    }

            # Cache results if enabled
            if self.use_cache and self.cache:
                self.cache.set(data_type, data, results)

            return results

        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            self._finish_progress()
            return {
                "error": str(e),
                "summary": "Analysis failed due to unexpected error",
                "recommendations": [],
            }

    def _combine_batch_results(
        self, batch_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine results from multiple batches into a single analysis.

        Args:
            batch_results: List of results from individual batches

        Returns:
            Combined analysis results
        """
        if not batch_results:
            return {
                "error": "No valid results from any batch",
                "summary": "Analysis failed across all batches",
                "recommendations": [],
            }

        # Initialize combined results
        combined = {
            "summary": "Combined analysis from multiple batches",
            "key_insights": [],
            "strengths": [],
            "improvement_areas": [],
            "recommendations": [],
            "experiments": [],
        }

        # Combine results from each batch
        for batch in batch_results:
            if "key_insights" in batch:
                combined["key_insights"].extend(batch["key_insights"])
            if "strengths" in batch:
                combined["strengths"].extend(batch["strengths"])
            if "improvement_areas" in batch:
                combined["improvement_areas"].extend(batch["improvement_areas"])
            if "recommendations" in batch:
                combined["recommendations"].extend(batch["recommendations"])
            if "experiments" in batch:
                combined["experiments"].extend(batch["experiments"])

        # Remove duplicates based on content
        for key in [
            "key_insights",
            "strengths",
            "improvement_areas",
            "recommendations",
            "experiments",
        ]:
            if key in combined:
                seen = set()
                combined[key] = [
                    item
                    for item in combined[key]
                    if not (item in seen or seen.add(item))
                ]

        return combined

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
        elif data_type == "tags":
            base_prompt = self._get_tag_prompt_template()
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

    def _get_tag_prompt_template(self) -> str:
        """Return the prompt template for tag analysis."""
        from .prompts import get_tag_prompt

        return get_tag_prompt()

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

        # Anthropic API
        elif self.provider == "anthropic" and self.client:
            try:
                payload = self._get_provider_payload(prompt)
                print(
                    f"Making request to Anthropic API with model: {payload.get('model')}"
                )

                # Direct client usage for Anthropic
                response = await self.client.messages.create(
                    model=payload.get("model", "claude-3-opus-20240229"),
                    messages=payload.get(
                        "messages", [{"role": "user", "content": prompt}]
                    ),
                    system=payload.get("system", ""),
                    max_tokens=payload.get("max_tokens", 4000),
                    temperature=payload.get("temperature", 0.3),
                )

                # Extract Anthropic response
                if hasattr(response, "content") and isinstance(response.content, list):
                    return "".join(
                        getattr(block, "text", "")
                        for block in response.content
                        if getattr(block, "type", None) == "text"
                    )
                return str(response)
            except Exception as e:
                logger.error(f"Error using Anthropic client: {str(e)}")
                # Fall through to HTTP method
                raise Exception(f"Failed to query Anthropic API: {str(e)}")

        # Fallback HTTP method for Anthropic (should only happen in exceptional cases)
        headers = self._get_provider_headers()
        data = self._get_provider_payload(prompt)

        # Log connection details if verbose logging is enabled
        if self.provider == "anthropic" and logger.isEnabledFor(logging.DEBUG):
            if self.api_key:
                logger.debug(f"API key: {self.api_key[:5]}...{self.api_key[-4:]}")
            logger.debug(f"Headers: {json.dumps(headers)}")
            logger.debug(f"Model: {self.model or data.get('model', 'default')}")

        async with aiohttp.ClientSession() as session:
            try:
                if not self.api_url:
                    raise ValueError("API URL not configured for provider")
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
        if self.provider == "anthropic":
            return {
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": self.api_key or "",
            }
        else:
            # Mock provider
            return {"Content-Type": "application/json"}

    def _get_provider_payload(
        self, prompt: str, thinking: bool = False
    ) -> Dict[str, Any]:
        """Get the appropriate request payload for the configured provider."""
        if self.provider == "anthropic":
            return {
                "model": self.model or "claude-3-opus-20240229",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4000,
                "system": "You must respond with valid JSON only, omitting any preamble or explanation.",
            }
        else:
            # Mock provider
            return {"prompt": prompt}

    def _extract_response_text(self, response_json: Dict[str, Any]) -> str:
        """Extract the response text from the provider-specific JSON response."""
        if self.provider == "anthropic":
            # For Anthropic, the response format differs between API versions
            try:
                # Claude 3 format - content is a list of content blocks
                if "content" in response_json:
                    if isinstance(response_json["content"], list):
                        return "".join(
                            getattr(block, "text", "")
                            for block in response_json["content"]
                            if getattr(block, "type", None) == "text"
                        )

                # Claude 2 format - completion is a string
                elif "completion" in response_json:
                    return response_json["completion"]

                # Fall back to string representation
                return str(response_json)
            except Exception as e:
                logger.error(f"Error extracting response text: {str(e)}")
                return str(response_json)
        else:
            # Mock provider
            return str(response_json)

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

    async def analyze_individual_entities(
        self,
        data: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze individual entity types (campaigns, flows, lists) in parallel.

        Args:
            data: Dictionary containing entity data
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Dictionary containing analysis results for each entity type
        """

        async def analyze_entity(
            entity_type: str, entity_data: List[Any]
        ) -> Dict[str, Any]:
            try:
                data_str = json.dumps(entity_data)
                return await self.analyze_data(
                    entity_type,
                    data_str,
                    start_date=start_date,
                    end_date=end_date,
                )
            except Exception as e:
                logger.error(f"Error analyzing {entity_type}: {str(e)}")
                return {
                    "error": str(e),
                    "summary": f"Analysis of {entity_type} failed",
                }

        # Run individual analyses in parallel
        tasks = []
        for entity_type in ["campaigns", "flows", "lists"]:
            if entity_type in data:
                tasks.append(analyze_entity(entity_type, data[entity_type]))

        results = await asyncio.gather(*tasks)

        return {
            "campaigns": results[0] if "campaigns" in data else {},
            "flows": results[1] if "flows" in data else {},
            "lists": results[2] if "lists" in data else {},
        }

    def _extract_key_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key insights from an individual analysis.

        Args:
            analysis: Analysis results for an entity type

        Returns:
            Dictionary containing key insights and metrics
        """
        return {
            "summary": analysis.get("summary", ""),
            "key_metrics": analysis.get("key_metrics", {}),
            "top_performing": analysis.get("top_performing", []),
            "underperforming": analysis.get("underperforming", []),
            "trends": analysis.get("trends", []),
            "recommendations": analysis.get("recommendations", []),
            "critical_issues": analysis.get("critical_issues", []),
        }

    async def analyze_unified(
        self,
        individual_results: Dict[str, Dict[str, Any]],
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform unified analysis using results from individual entity analyses.

        Args:
            individual_results: Results from individual entity analyses
            raw_data: Original raw data for reference

        Returns:
            Unified analysis results
        """
        # Extract key insights from individual analyses
        summary_data = {
            entity_type: self._extract_key_insights(results)
            for entity_type, results in individual_results.items()
        }

        # Add raw data metrics
        summary_data["raw_metrics"] = {
            "campaign_count": len(raw_data.get("campaigns", [])),
            "flow_count": len(raw_data.get("flows", [])),
            "list_count": len(raw_data.get("lists", [])),
        }

        # Generate unified prompt with summarized insights
        prompt = self._generate_unified_prompt(summary_data, raw_data)

        try:
            response = await self._query_ai(prompt, "unified")
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Error during unified analysis: {str(e)}")
            return {
                "error": str(e),
                "summary": "Unified analysis failed",
            }

    def _generate_unified_prompt(
        self,
        summary_data: Dict[str, Any],
        raw_data: Dict[str, Any],
    ) -> str:
        """
        Generate a prompt for unified analysis using summarized insights.

        Args:
            summary_data: Summarized insights from individual analyses
            raw_data: Original raw data

        Returns:
            Formatted prompt string
        """
        base_prompt = self._get_unified_prompt_template()

        # Add summarized insights
        insights_str = json.dumps(summary_data, indent=2)

        # Add raw data preview
        raw_data_preview = json.dumps(raw_data, indent=2)[:10000]  # Limit preview size

        return f"""
{base_prompt}

SUMMARIZED INSIGHTS FROM INDIVIDUAL ANALYSES:
```json
{insights_str}
```

RAW DATA PREVIEW (potentially truncated):
```json
{raw_data_preview}
```

Provide your unified analysis in JSON format as specified in the instructions above.
Focus on synthesizing the pre-analyzed insights and identifying cross-entity patterns.
"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the AI response text into a structured format.

        Args:
            response_text: Raw response from the AI

        Returns:
            Structured dict of analysis results
        """
        logger.debug(f"Parsing response text: {response_text[:200]}...")

        try:
            # Try to parse the response as JSON
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error: {str(e)}")

            # If not valid JSON, try to extract JSON from the text
            try:
                # Try to find JSON object with regex
                import re

                json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                    logger.debug("Extracted JSON using regex")
                    result = json.loads(json_text.strip())
                    return result

                # Look for JSON between ``` markers
                if "```" in response_text:
                    parts = response_text.split("```")
                    for i in range(1, len(parts), 2):
                        try:
                            result = json.loads(parts[i].strip())
                            logger.debug("Extracted JSON from code block")
                            return result
                        except json.JSONDecodeError:
                            continue

                    # Try with specific json tag
                    if "```json" in response_text:
                        json_text = response_text.split("```json")[1].split("```")[0]
                        result = json.loads(json_text.strip())
                        logger.debug("Extracted JSON from json code block")
                        return result

                logger.debug("Could not extract JSON from response")
            except (IndexError, json.JSONDecodeError) as e:
                logger.debug(f"JSON extraction error: {str(e)}")

            # Return a simplified dict with the raw text
            return {
                "error": "Failed to parse AI response as JSON",
                "summary": "The AI response couldn't be structured properly.",
                "raw_response": response_text,
            }

    async def refresh_analysis(
        self,
        data_type: str,
        data: Union[str, Dict, List],
        context: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Force a fresh analysis, ignoring any cached results.

        Args:
            data_type: Type of data being analyzed
            data: The data to analyze
            context: Optional additional context
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Fresh analysis results
        """
        logger.info(f"Refreshing analysis for {data_type}")
        return await self.analyze_data(
            data_type=data_type,
            data=data,
            context=context,
            start_date=start_date,
            end_date=end_date,
            force_refresh=True,
        )

    def clear_cache(self, data_type: Optional[str] = None) -> None:
        """
        Clear the analysis cache.

        Args:
            data_type: Optional specific data type to clear cache for
        """
        if self.cache:
            self.cache.clear(data_type)
            logger.info(f"Cleared cache for {data_type if data_type else 'all types'}")
