---
title: "User Authentication API"
version: "1.2.0"
date: "2024-01-15"
author: "Jane Developer"
status: "published"
tags: ["authentication", "api", "rest"]
---

# User Authentication API

This API provides secure user authentication and authorization services.

## Overview

The User Authentication API allows applications to manage user accounts, authenticate users, and control access to protected resources. It supports OAuth 2.0, JWT tokens, and traditional session-based authentication.

Key features:
- Secure password hashing with bcrypt
- JWT token generation and validation  
- OAuth 2.0 integration with Google and GitHub
- Role-based access control (RBAC)
- Rate limiting and abuse protection

## API Reference

### Endpoints

#### POST /auth/login
Authenticate a user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": "12345",
    "email": "user@example.com",
    "role": "user"
  }
}
```

#### POST /auth/logout
Invalidate the current session or token.

#### GET /auth/me
Get current user information (requires authentication).

### Authentication

All protected endpoints require an Authorization header:

```
Authorization: Bearer <jwt_token>
```

JWT tokens are valid for 1 hour by default. Refresh tokens can be used to obtain new access tokens.

### Rate Limiting

- Login attempts: 5 per minute per IP
- General API calls: 100 per minute per user
- Token refresh: 10 per hour per user

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Examples

### Basic Usage

Here's a simple login flow using curl:

```bash
# Login and get token
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use token for authenticated request
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  https://api.example.com/auth/me
```

### Advanced Usage

OAuth 2.0 flow with Google:

```bash
# Redirect user to Google OAuth
https://api.example.com/auth/oauth/google?redirect_uri=https://myapp.com/callback

# Handle callback and exchange code for token
curl -X POST https://api.example.com/auth/oauth/callback \
  -H "Content-Type: application/json" \
  -d '{"code": "oauth_code_from_google", "provider": "google"}'
```

### SDK Integration

This section demonstrates how to integrate the authentication API with various programming languages and frameworks. Each example includes multiple paragraphs explaining the implementation details and best practices.

#### Python Integration

The Python SDK provides a comprehensive wrapper around the authentication API. It handles token management, automatic refresh, and error handling out of the box. This makes it ideal for Python applications that need robust authentication without dealing with the low-level HTTP details.

```python
from auth_sdk import AuthClient
import asyncio

# Initialize the authentication client
auth_client = AuthClient(
    base_url="https://api.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

async def login_example():
    try:
        # Authenticate user with email and password
        result = await auth_client.login(
            email="user@example.com", 
            password="secure_password"
        )
        
        print(f"Login successful! Token expires in {result.expires_in} seconds")
        print(f"User ID: {result.user.id}")
        
        # The SDK automatically handles token storage and refresh
        return result.token
        
    except AuthenticationError as e:
        print(f"Login failed: {e.message}")
        return None

# Run the async function
token = asyncio.run(login_example())
```

When working with the Python SDK, it's important to understand that all network operations are asynchronous. This design choice allows your application to handle multiple authentication requests concurrently without blocking the main thread. The SDK also implements automatic retry logic with exponential backoff for handling temporary network failures.

For production applications, consider implementing proper token caching to avoid unnecessary authentication requests. The SDK provides built-in token validation that checks expiry times before making API calls. This reduces latency and improves the overall user experience.

#### JavaScript/Node.js Integration

The JavaScript SDK offers both Promise-based and async/await patterns for maximum flexibility. It works seamlessly in both browser and Node.js environments, with automatic environment detection for optimal performance.

```javascript
const { AuthClient } = require('@example/auth-sdk');

// Create client instance with configuration
const authClient = new AuthClient({
  baseURL: 'https://api.example.com',
  clientId: process.env.AUTH_CLIENT_ID,
  timeout: 10000,
  retryAttempts: 3
});

class AuthService {
  constructor() {
    this.currentToken = null;
    this.refreshTimer = null;
  }

  async authenticate(email, password) {
    try {
      const response = await authClient.login({ email, password });
      
      this.currentToken = response.data.token;
      this.scheduleTokenRefresh(response.data.expires_in);
      
      // Store user information for later use
      this.currentUser = response.data.user;
      
      console.log(`Authentication successful for user: ${this.currentUser.email}`);
      return this.currentToken;
      
    } catch (error) {
      if (error.response?.status === 429) {
        console.log('Rate limit exceeded. Please try again later.');
        throw new RateLimitError('Too many login attempts');
      }
      
      console.error('Authentication failed:', error.message);
      throw error;
    }
  }

  async getProtectedData(endpoint) {
    if (!this.isTokenValid()) {
      await this.refreshToken();
    }

    return await authClient.get(endpoint, {
      headers: {
        'Authorization': `Bearer ${this.currentToken}`
      }
    });
  }

  scheduleTokenRefresh(expiresIn) {
    // Refresh token 5 minutes before expiry
    const refreshTime = (expiresIn - 300) * 1000;
    
    this.refreshTimer = setTimeout(async () => {
      try {
        await this.refreshToken();
      } catch (error) {
        console.error('Token refresh failed:', error);
        // Handle refresh failure (e.g., redirect to login)
      }
    }, refreshTime);
  }
}
```

The JavaScript implementation showcases several important patterns for production applications. First, it demonstrates proper error handling that distinguishes between different types of failures (rate limiting vs. authentication errors). Second, it implements automatic token refresh scheduling to ensure users don't experience unexpected authentication failures.

The service class pattern shown here provides a clean abstraction over the raw API calls. This makes it easier to integrate authentication throughout your application while maintaining consistent behavior. The automatic retry logic handles temporary network issues, while the timeout configuration prevents hanging requests in poor network conditions.

#### cURL Advanced Examples

For testing and debugging purposes, cURL remains an invaluable tool. These examples demonstrate various authentication scenarios and error handling techniques that are useful during development and troubleshooting.

```bash
#!/bin/bash

# Set up environment variables for security
API_BASE="https://api.example.com"
CLIENT_ID="your_client_id"
CLIENT_SECRET="your_client_secret"

# Function to handle login with error checking
login_user() {
    local email=$1
    local password=$2
    
    echo "Attempting login for: $email"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$API_BASE/auth/login" \
        -H "Content-Type: application/json" \
        -H "User-Agent: MyApp/1.0" \
        -d "{
            \"email\": \"$email\",
            \"password\": \"$password\",
            \"client_id\": \"$CLIENT_ID\"
        }")
    
    # Extract HTTP status code
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        echo "Login successful!"
        # Extract token using jq
        token=$(echo $body | jq -r '.token')
        echo "Token: $token"
        return 0
    else
        echo "Login failed with status: $http_code"
        echo "Response: $body"
        return 1
    fi
}

# Function to make authenticated requests
make_authenticated_request() {
    local token=$1
    local endpoint=$2
    
    curl -s \
        -H "Authorization: Bearer $token" \
        -H "Accept: application/json" \
        "$API_BASE$endpoint"
}

# Example usage with proper error handling
if login_user "user@example.com" "password123"; then
    # Use the token for subsequent requests
    user_info=$(make_authenticated_request "$token" "/auth/me")
    echo "User info: $user_info"
    
    # Example of accessing protected resource
    protected_data=$(make_authenticated_request "$token" "/api/protected")
    echo "Protected data: $protected_data"
else
    echo "Cannot proceed without authentication"
    exit 1
fi
```

These cURL examples demonstrate production-ready scripting techniques that include proper error handling, response parsing, and security considerations. The script uses environment variables to avoid hardcoding sensitive information and implements proper HTTP status code checking to handle different response scenarios.

The modular function approach shown here makes it easy to reuse authentication logic across different scripts and testing scenarios. This is particularly useful for CI/CD pipelines where automated testing requires reliable authentication mechanisms.

## Changelog

### Version 1.2.0 (2024-01-15)
- Added OAuth 2.0 support for Google and GitHub
- Improved rate limiting with sliding window algorithm
- Added refresh token rotation for enhanced security

### Version 1.1.0 (2023-12-01)
- Implemented role-based access control
- Added password complexity requirements
- Enhanced error messages and response codes

### Version 1.0.0 (2023-10-15)
- Initial release
- Basic email/password authentication
- JWT token support
- Session management