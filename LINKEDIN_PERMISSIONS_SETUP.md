# LinkedIn Developer API Setup and Permissions Guide

This document explains how to set up LinkedIn Developer permissions required for the LinkedIn MCP Server using the official LinkedIn API.

## Prerequisites

1. LinkedIn Account
2. LinkedIn Company Page (required for some API products)

## Step 1: Create a LinkedIn Developer Application

1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps/)
2. Click "Create App"
3. Fill in the required information:
   - **App Name**: Your application name (e.g., "LinkedIn MCP Server")
   - **LinkedIn Company Page**: Select your company page
   - **Privacy Policy URL**: Required URL to your privacy policy
   - **App Logo**: Upload a logo (optional but recommended)
4. Accept the API Terms of Use
5. Click "Create App"

## Step 2: Configure OAuth Settings

1. In your app dashboard, go to the "Auth" tab
2. Add your OAuth 2.0 redirect URLs:
   - For development: `http://localhost:8000/auth/callback`
   - For production: `https://yourdomain.com/auth/callback`
3. Note down your:
   - **Client ID**
   - **Client Secret**

## Step 3: Request API Product Access

The LinkedIn MCP Server requires access to specific API products. Request access to the following:

### Required API Products

#### 1. Sign In with LinkedIn using OpenID Connect
- **Purpose**: Basic profile information access
- **Scopes Provided**: `openid`, `profile`, `email`
- **Status**: Self-serve (automatically granted)
- **Use Cases**: 
  - Get basic user profile information
  - User authentication

#### 2. Share on LinkedIn (Optional)
- **Purpose**: Post content to LinkedIn
- **Scopes Provided**: `w_member_social`
- **Status**: Self-serve (automatically granted)
- **Use Cases**: 
  - Create posts on behalf of users
  - Share content

#### 3. Advertising API (For Company/Job Data)
- **Purpose**: Access to company and job posting information
- **Scopes Provided**: `r_ads`, `r_ads_reporting`
- **Status**: Requires application review
- **Use Cases**: 
  - Access company information
  - Job posting data
  - Ad account management

#### 4. Marketing Developer Platform (Advanced)
- **Purpose**: Enhanced marketing and analytics data
- **Scopes Provided**: `r_marketing_leadgen_automation`, `r_1st_connections_size`
- **Status**: Requires application review
- **Use Cases**: 
  - Lead generation
  - Connection analytics

### How to Request Access

1. In your app dashboard, go to the "Products" tab
2. Click "Request Access" for each required product
3. For products requiring review:
   - Fill out the application form
   - Provide detailed use case descriptions
   - Submit supporting documentation
   - Wait for LinkedIn review (typically 7-10 business days)

## Step 4: API Limitations and Considerations

### Rate Limiting
- **Basic products**: 500 requests per day per member
- **Advanced products**: Higher limits based on approval
- **Enterprise**: Custom limits

### Data Access Restrictions
Unlike web scraping, the official LinkedIn API has strict limitations:

- **Profile Data**: Only basic information from authorized users
- **Company Data**: Limited to companies you have admin access to
- **Job Data**: Limited to job postings from your company
- **Search**: No public profile or company search capabilities

### Comparison: Scraping vs Official API

| Feature | Web Scraping | Official API |
|---------|--------------|--------------|
| Profile Access | Any public profile | Only authorized users |
| Company Access | Any public company | Only managed companies |
| Job Search | Any job posting | Limited job access |
| Rate Limits | IP-based blocking | Strict API quotas |
| Authentication | Session cookies | OAuth 2.0 tokens |
| Compliance | Against ToS | Compliant |
| Reliability | Fragile to changes | Stable API contract |

## Step 5: Environment Configuration

Once you have your LinkedIn app set up, configure these environment variables:

```bash
# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/callback

# Optional: Specific access token for testing
LINKEDIN_ACCESS_TOKEN=your_access_token_here
```

## Step 6: OAuth 2.0 Flow Implementation

The LinkedIn MCP Server will implement OAuth 2.0 Authorization Code Flow:

1. **Authorization**: Direct users to LinkedIn's authorization URL
2. **Callback**: Handle the authorization code at your redirect URI
3. **Token Exchange**: Exchange authorization code for access token
4. **API Calls**: Use access token for API requests
5. **Refresh**: Use refresh tokens to maintain access

## Step 7: Testing Your Setup

1. Use LinkedIn's [Token Generator Tool](https://www.linkedin.com/developers/tools/oauth/token-generator) for testing
2. Generate a 3-legged access token with required scopes
3. Test API calls using the official client library

## Important Notes

### Migration from Scraping

If you're migrating from the web scraping approach:

1. **Data Coverage**: Official API provides less data than scraping
2. **User Authorization**: Users must explicitly authorize your app
3. **Company Data**: Limited to companies you manage
4. **Job Data**: No public job search capabilities
5. **Compliance**: Fully compliant with LinkedIn's Terms of Service

### Best Practices

1. **Minimal Scopes**: Request only the scopes you actually need
2. **Token Security**: Store access tokens securely
3. **Error Handling**: Implement robust error handling for rate limits
4. **User Consent**: Clearly explain why you need LinkedIn access
5. **Data Privacy**: Handle user data according to privacy regulations

## Troubleshooting

### Common Issues

1. **"Invalid Client" Error**: Check your Client ID and Client Secret
2. **"Redirect URI Mismatch"**: Ensure redirect URI exactly matches app settings
3. **"Scope Not Allowed"**: Request proper API product access first
4. **Rate Limiting**: Implement exponential backoff for retries

### Getting Help

- [LinkedIn Developer Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [LinkedIn Developer Community](https://www.linkedin.com/groups/3722520/)
- [LinkedIn Developer Support](https://www.linkedin.com/help/linkedin/topics/6424/6470)

## Next Steps

After completing this setup:

1. Configure the LinkedIn MCP Server with your credentials
2. Test the OAuth flow with your application
3. Implement proper error handling for API limitations
4. Consider fallback strategies for unavailable data

---

**⚠️ Important Security Note**: Never commit your Client Secret or access tokens to version control. Always use environment variables or secure credential storage.