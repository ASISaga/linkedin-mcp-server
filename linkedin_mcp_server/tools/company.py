# src/linkedin_mcp_server/tools/company.py
"""
LinkedIn company tools using official LinkedIn API.

Provides MCP tools for managing and accessing LinkedIn company information through
the official LinkedIn API with proper OAuth 2.0 authentication.

Note: Company data access is limited to companies you manage through the official API.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from linkedin_mcp_server.linkedin_auth import get_authenticated_client, get_access_token
from linkedin_mcp_server.exceptions import AuthenticationError, APIError

logger = logging.getLogger(__name__)


def register_company_tools(mcp: FastMCP) -> None:
    """
    Register all company-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool()
    async def search_companies(search_criteria: Dict[str, Any], fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for companies using LinkedIn's official API.
        
        Note: This requires appropriate API permissions and may be limited to 
        companies you have access to manage.

        Args:
            search_criteria (Dict[str, Any]): Search criteria for companies
                Example: {
                    "status": {"values": ["ACTIVE"]},
                    "reference": {"values": ["urn:li:organization:123"]}
                }
            fields (str, optional): Comma-separated fields to retrieve

        Returns:
            Dict[str, Any]: Search results and company data
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {"search": search_criteria}
            if fields:
                query_params["fields"] = fields
            
            logger.info("Searching companies via LinkedIn API")
            response = client.finder(
                resource_path="/organizations",
                finder_name="search",
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "companies": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "total_results": response.paging.total if response.paging else len(response.elements)
            }
            
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "error": "Authentication required",
                "message": str(e),
                "help": "Please ensure you have completed OAuth and have appropriate company permissions"
            }
        except APIError as e:
            logger.error(f"LinkedIn API error: {e}")
            return {
                "error": "API request failed", 
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in search_companies: {e}")
            return {
                "error": "Unexpected error",
                "message": str(e)
            }

    @mcp.tool()
    async def get_organization_info(organization_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific organization.
        
        Note: Access is typically limited to organizations you manage.

        Args:
            organization_id (str): LinkedIn organization ID or URN
            fields (str, optional): Comma-separated fields to retrieve

        Returns:
            Dict[str, Any]: Organization information
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            # Clean up organization ID format
            if organization_id.startswith("urn:li:organization:"):
                org_id = organization_id.split(":")[-1]
            else:
                org_id = organization_id
            
            query_params = {"fields": fields} if fields else None
            
            logger.info(f"Fetching organization info for ID: {org_id}")
            response = client.get(
                resource_path="/organizations/{id}",
                path_keys={"id": org_id},
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "organization": response.entity,
                "organization_id": org_id
            }
            
        except Exception as e:
            logger.error(f"Error in get_organization_info: {e}")
            return {
                "error": "Failed to fetch organization information",
                "message": str(e)
            }

    @mcp.tool()
    async def get_company_posts(company_urn: str, start: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Get posts from a company page.
        
        Requires appropriate permissions to access company social media content.

        Args:
            company_urn (str): Company URN (e.g., "urn:li:organization:123")
            start (int): Starting index for pagination
            count (int): Number of posts to retrieve (max 100)

        Returns:
            Dict[str, Any]: Company posts and metadata
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {
                "author": company_urn,
                "start": start,
                "count": min(count, 100)  # Limit to API maximum
            }
            
            logger.info(f"Fetching company posts for: {company_urn}")
            response = client.get_all(
                resource_path="/posts",
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "posts": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "company_urn": company_urn
            }
            
        except Exception as e:
            logger.error(f"Error in get_company_posts: {e}")
            return {
                "error": "Failed to fetch company posts",
                "message": str(e),
                "note": "This feature requires w_member_social scope and company admin permissions"
            }

    @mcp.tool()
    async def create_company_post(company_urn: str, post_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a post on behalf of a company.
        
        Requires w_member_social scope and company admin permissions.

        Args:
            company_urn (str): Company URN (e.g., "urn:li:organization:123")
            post_content (Dict[str, Any]): Post content structure
                Example: {
                    "commentary": "Post text content",
                    "visibility": "PUBLIC"
                }

        Returns:
            Dict[str, Any]: Created post information
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            # Structure the post entity
            post_entity = {
                "author": company_urn,
                "commentary": post_content.get("commentary", ""),
                "visibility": post_content.get("visibility", "PUBLIC"),
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                }
            }
            
            # Add content if provided
            if "content" in post_content:
                post_entity["content"] = post_content["content"]
            
            logger.info(f"Creating company post for: {company_urn}")
            response = client.create(
                resource_path="/posts",
                entity=post_entity,
                access_token=access_token
            )
            
            if response.status_code not in [200, 201]:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "success": True,
                "post_id": response.entity_id,
                "post_urn": f"urn:li:post:{response.entity_id}",
                "company_urn": company_urn
            }
            
        except Exception as e:
            logger.error(f"Error in create_company_post: {e}")
            return {
                "error": "Failed to create company post",
                "message": str(e),
                "note": "This requires w_member_social scope and company admin permissions"
            }

    @mcp.tool()
    async def get_managed_companies() -> Dict[str, Any]:
        """
        Get list of companies/organizations that the authenticated user can manage.

        Returns:
            Dict[str, Any]: List of managed companies
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            logger.info("Fetching managed companies")
            response = client.finder(
                resource_path="/organizationAuthorizations",
                finder_name="roleAssignee",
                access_token=access_token
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            # Extract organization information from authorizations
            managed_companies = []
            for auth in response.elements:
                if "organization" in auth:
                    managed_companies.append({
                        "organization_urn": auth["organization"],
                        "role": auth.get("role", "Unknown"),
                        "authorization": auth
                    })
            
            return {
                "managed_companies": managed_companies,
                "total_count": len(managed_companies),
                "note": "Only companies you have admin access to are shown"
            }
            
        except Exception as e:
            logger.error(f"Error in get_managed_companies: {e}")
            return {
                "error": "Failed to fetch managed companies",
                "message": str(e),
                "note": "This requires appropriate organizational permissions"
            }
