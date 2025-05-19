# CLAUDE.md - Guidance for Claude

This file contains important information and guidance for Claude when working with this codebase.

## Project Structure

Klavicle is a tool for Klaviyo data integration and analysis, featuring:

- CLI interface for interacting with Klaviyo data
- Multiple analyzers for different data types (campaigns, flows, lists)
- Data export and reporting capabilities

## Key Files and Directories

- `/src/klavicle/klaviyo/` - Core Klaviyo integration components
- `/src/klavicle/cli/` - Command-line interface implementations
- `/src/klavicle/database/` - Database interactions
- `/docs/` - Documentation files, including implementation plans

## Implementation Plans

When working on AI analysis features, refer to the detailed plan:

- `/docs/AI_ANALYSIS_PLAN.md` - Comprehensive plan for AI analysis implementation

When implementing new features, always consult this plan to stay aligned with the project's goals and approach.

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints consistently
- Document all public functions and classes
- Maintain backward compatibility when extending existing features
- Write unit tests for new functionality

## Command Execution Reference

- Run tests: `poetry run pytest`
- Format code: `poetry run ruff.`
- Type checking: `poetry run mypy.`

## AI Analysis Implementation Guidelines

1. Always refer to the AI Analysis Plan in `/docs/AI_ANALYSIS_PLAN.md` when working on AI features
2. Implement features according to the phased approach defined in the plan
3. Maintain compatibility with existing static analysis methods
4. Use the TaskMaster AI todo list to track implementation progress
5. Separate AI-specific code from core functionality to maintain modularity
6. Follow the defined class structures and integration points

## Common Issues and Solutions

If you encounter rate limiting with Klaviyo API:

- Implement exponential backoff with the retrying mechanism in client.py
- Consider batching requests when possible

For AI API integration:

- Handle API errors gracefully
- Provide meaningful fallbacks when AI services are unavailable
- Cache responses when appropriate to reduce API costs
