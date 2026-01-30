---
name: api-client-helper
description: Helps design and implement REST API clients with best practices for authentication,
  error handling, and response parsing
allowed-tools: Read, Write, Edit, Bash, WebFetch
version: 1.0.0
created: '2025-10-26'
---

## Purpose

This skill provides comprehensive guidance for creating robust REST API clients. It covers:

- API endpoint discovery and documentation review
- Authentication methods (API keys, OAuth, JWT)
- Request/response handling patterns
- Error handling and retry logic
- Rate limiting and throttling
- Testing strategies

## Instructions

When helping with API client development:

1. **Analyze Requirements**
   - Review API documentation or OpenAPI specs
   - Identify authentication requirements
   - Determine rate limits and constraints

2. **Design Client Structure**
   - Create base client class with auth handling
   - Implement request/response wrappers
   - Add error handling and retries

3. **Implement Endpoints**
   - Create method for each API endpoint
   - Add type hints and documentation
   - Include request validation

4. **Testing**
   - Write unit tests with mocked responses
   - Create integration tests with real API calls
   - Document test setup and credentials

## Examples

## Example: Basic Client Structure

Create a base client class that handles authentication and common request patterns.

## Example: Error Handling

Implement retry logic with exponential backoff for handling transient failures and rate limits.

## Additional Notes

## Best Practices

- Always use connection pooling for multiple requests
- Implement exponential backoff for retries
- Cache responses when appropriate
- Use environment variables for sensitive credentials
- Log requests for debugging (without sensitive data)
- Validate responses against expected schemas

## Common Pitfalls

- Hardcoding API credentials
- Not handling rate limits
- Ignoring HTTP status codes
- Not setting request timeouts
- Poor error messages for API failures
