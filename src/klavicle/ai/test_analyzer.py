"""Tests for the AIAnalyzer class."""

import asyncio
import json
import os
from typing import Dict, List

import pytest

from .analyzer import AIAnalyzer


def test_ai_analyzer_init():
    """Test AIAnalyzer initialization."""
    # Test with default params
    analyzer = AIAnalyzer()
    assert analyzer.provider == "openai"
    assert analyzer.model == "gpt-4o"

    # Test with custom params
    analyzer = AIAnalyzer(provider="anthropic", model="claude-3-opus-20240229")
    assert analyzer.provider == "anthropic"
    assert analyzer.model == "claude-3-opus-20240229"

    # Test with mock provider
    analyzer = AIAnalyzer(provider="mock")
    assert analyzer.provider == "mock"
    assert analyzer.model == "mock-model"


def test_prompt_generation():
    """Test prompt generation for different data types."""
    analyzer = AIAnalyzer(provider="mock")
    
    # Create sample data
    sample_data = json.dumps([{"id": "test1", "name": "Test Campaign"}])
    
    # Test campaign prompt
    campaign_prompt = analyzer._generate_prompt("campaigns", sample_data)
    assert "klaviyo" in campaign_prompt.lower()
    assert "campaign" in campaign_prompt.lower()
    assert sample_data in campaign_prompt
    
    # Test flow prompt
    flow_prompt = analyzer._generate_prompt("flows", sample_data)
    assert "klaviyo" in flow_prompt.lower()
    assert "flow" in flow_prompt.lower()
    
    # Test list prompt
    list_prompt = analyzer._generate_prompt("lists", sample_data)
    assert "klaviyo" in list_prompt.lower()
    assert "list" in list_prompt.lower()
    
    # Test unified prompt
    unified_prompt = analyzer._generate_prompt("unified", sample_data)
    assert "klaviyo" in unified_prompt.lower()
    assert "unified" in unified_prompt.lower()
    
    # Test generic prompt
    generic_prompt = analyzer._generate_prompt("unknown_type", sample_data)
    assert "klaviyo" in generic_prompt.lower()
    assert "marketing data" in generic_prompt.lower()


def test_response_parsing():
    """Test parsing of AI responses."""
    analyzer = AIAnalyzer(provider="mock")
    
    # Test valid JSON response
    valid_json = '{"summary": "Test summary", "recommendations": ["rec1", "rec2"]}'
    parsed = analyzer._parse_response(valid_json)
    assert parsed["summary"] == "Test summary"
    assert len(parsed["recommendations"]) == 2
    
    # Test invalid JSON response
    invalid_json = "This is not JSON"
    parsed = analyzer._parse_response(invalid_json)
    assert "error" in parsed
    assert "raw_response" in parsed
    
    # Test JSON embedded in markdown - our implementation extracts JSON from markdown now
    markdown_json = '```json\n{"summary": "Embedded JSON"}\n```'
    parsed = analyzer._parse_response(markdown_json)
    assert parsed["summary"] == "Embedded JSON"


@pytest.mark.asyncio
async def test_mock_analysis():
    """Test mock analysis to ensure we can get results without real API calls."""
    analyzer = AIAnalyzer(provider="mock")
    
    # Create sample data
    sample_data = [{"id": "test1", "name": "Test Campaign"}]
    
    # Run analysis for campaigns
    results = await analyzer.analyze_data("campaigns", sample_data)
    
    # Check results structure for campaigns
    assert "summary" in results
    assert "campaigns" in results["summary"].lower()
    assert "recommendations" in results
    assert "key_metrics" in results
    
    # Test flows analysis
    flow_results = await analyzer.analyze_data("flows", sample_data)
    assert "flows" in flow_results["summary"].lower()
    assert "key_metrics" in flow_results
    
    # Test lists analysis
    list_results = await analyzer.analyze_data("lists", sample_data)
    assert "lists" in list_results["summary"].lower()
    assert "key_metrics" in list_results
    
    # Test unified analysis
    unified_results = await analyzer.analyze_data("unified", sample_data)
    assert "account" in unified_results["summary"].lower()
    assert "account_health" in unified_results


if __name__ == "__main__":
    # Run the asyncio test manually
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mock_analysis())
    print("Mock analysis test passed!")
    
    # Run other tests
    test_ai_analyzer_init()
    print("Initialization test passed!")
    
    test_prompt_generation()
    print("Prompt generation test passed!")
    
    test_response_parsing()
    print("Response parsing test passed!")