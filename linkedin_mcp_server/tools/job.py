# src/linkedin_mcp_server/tools/job.py
"""
LinkedIn job tools using official LinkedIn API.

Provides MCP tools for job-related functionality through the official LinkedIn API.
Note: Job data access through the official API is very limited compared to scraping.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from linkedin_mcp_server.linkedin_auth import get_authenticated_client, get_access_token
from linkedin_mcp_server.exceptions import AuthenticationError, APIError

logger = logging.getLogger(__name__)


def register_job_tools(mcp: FastMCP) -> None:
    """
    Register all job-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool()
    async def search_job_postings(search_criteria: Dict[str, Any], start: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Search for job postings using LinkedIn's API.
        
        Note: This typically requires specific API access and may be limited 
        to job postings from companies you manage.

        Args:
            search_criteria (Dict[str, Any]): Search criteria for jobs
                Example: {
                    "status": {"values": ["LISTED"]},
                    "companyJobsFilterCriteria": {
                        "company": "urn:li:company:123"
                    }
                }
            start (int): Starting index for pagination
            count (int): Number of results to retrieve

        Returns:
            Dict[str, Any]: Job search results
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {
                "search": search_criteria,
                "start": start,
                "count": min(count, 100)
            }
            
            logger.info("Searching job postings via LinkedIn API")
            response = client.finder(
                resource_path="/jobPostings",
                finder_name="search",
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "job_postings": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "total_results": response.paging.total if response.paging else len(response.elements)
            }
            
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "error": "Authentication required",
                "message": str(e),
                "note": "Job posting access requires specific API permissions"
            }
        except Exception as e:
            logger.error(f"Error in search_job_postings: {e}")
            return {
                "error": "Failed to search job postings",
                "message": str(e),
                "note": "Job posting access is typically limited to companies you manage"
            }

    @mcp.tool()
    async def get_company_job_postings(company_urn: str, start: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Get job postings for a specific company.
        
        Note: Access is typically limited to companies you manage.

        Args:
            company_urn (str): Company URN (e.g., "urn:li:organization:123")
            start (int): Starting index for pagination
            count (int): Number of results to retrieve

        Returns:
            Dict[str, Any]: Company job postings
        """
        try:
            search_criteria = {
                "companyJobsFilterCriteria": {
                    "company": company_urn
                },
                "status": {"values": ["LISTED", "DRAFT"]}
            }
            
            return await search_job_postings(search_criteria, start, count)
            
        except Exception as e:
            logger.error(f"Error in get_company_job_postings: {e}")
            return {
                "error": "Failed to fetch company job postings",
                "message": str(e)
            }

    @mcp.tool()
    async def create_job_posting(company_urn: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job posting for a company.
        
        Requires company admin permissions and appropriate API access.

        Args:
            company_urn (str): Company URN (e.g., "urn:li:organization:123")
            job_data (Dict[str, Any]): Job posting data
                Example: {
                    "title": "Software Engineer",
                    "description": "Job description here",
                    "location": "San Francisco, CA",
                    "employmentType": "FULL_TIME"
                }

        Returns:
            Dict[str, Any]: Created job posting information
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            # Structure the job posting entity
            job_entity = {
                "companyApplyUrl": job_data.get("apply_url"),
                "description": job_data.get("description", ""),
                "employmentStatus": job_data.get("employment_status", "FULL_TIME"),
                "externalJobPostingId": job_data.get("external_id"),
                "listedAt": job_data.get("listed_at"),
                "jobPostingOperationType": "CREATE",
                "jobFunction": {"code": job_data.get("job_function", "eng")},
                "industry": {"code": job_data.get("industry", "4")},
                "title": job_data.get("title", ""),
                "partner": company_urn,
                "location": job_data.get("location", ""),
                "workplaceTypes": job_data.get("workplace_types", ["on_site"])
            }
            
            logger.info(f"Creating job posting for company: {company_urn}")
            response = client.create(
                resource_path="/jobPostings",
                entity=job_entity,
                access_token=access_token
            )
            
            if response.status_code not in [200, 201]:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "success": True,
                "job_posting_id": response.entity_id,
                "job_posting_urn": f"urn:li:jobPosting:{response.entity_id}",
                "company_urn": company_urn
            }
            
        except Exception as e:
            logger.error(f"Error in create_job_posting: {e}")
            return {
                "error": "Failed to create job posting",
                "message": str(e),
                "note": "This requires company admin permissions and Job Posting API access"
            }

    @mcp.tool()
    async def get_job_applications(job_posting_urn: str, start: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        Get applications for a specific job posting.
        
        Requires company admin permissions and appropriate API access.

        Args:
            job_posting_urn (str): Job posting URN
            start (int): Starting index for pagination
            count (int): Number of applications to retrieve

        Returns:
            Dict[str, Any]: Job applications data
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {
                "jobPosting": job_posting_urn,
                "start": start,
                "count": min(count, 100)
            }
            
            logger.info(f"Fetching applications for job: {job_posting_urn}")
            response = client.finder(
                resource_path="/jobApplications",
                finder_name="jobPosting",
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "applications": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "job_posting_urn": job_posting_urn
            }
            
        except Exception as e:
            logger.error(f"Error in get_job_applications: {e}")
            return {
                "error": "Failed to fetch job applications",
                "message": str(e),
                "note": "This requires Job Posting API access and company admin permissions"
            }

    @mcp.tool()
    async def get_job_posting_analytics(job_posting_urn: str) -> Dict[str, Any]:
        """
        Get analytics data for a job posting.
        
        Requires company admin permissions and analytics API access.

        Args:
            job_posting_urn (str): Job posting URN

        Returns:
            Dict[str, Any]: Analytics data for the job posting
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {
                "jobPosting": job_posting_urn
            }
            
            logger.info(f"Fetching analytics for job: {job_posting_urn}")
            response = client.finder(
                resource_path="/jobPostingAnalytics",
                finder_name="jobPosting", 
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "analytics": response.elements,
                "job_posting_urn": job_posting_urn
            }
            
        except Exception as e:
            logger.error(f"Error in get_job_posting_analytics: {e}")
            return {
                "error": "Failed to fetch job posting analytics",
                "message": str(e),
                "note": "This requires analytics API access and company admin permissions"
            }

    @mcp.tool()
    async def get_job_api_limitations() -> Dict[str, Any]:
        """
        Get information about LinkedIn Job API limitations and requirements.

        Returns:
            Dict[str, Any]: Information about API limitations
        """
        return {
            "api_limitations": {
                "job_search": "Limited to companies you manage or have API partnerships with",
                "job_details": "Only accessible for your own company's job postings",
                "job_applications": "Requires company admin permissions",
                "public_job_search": "Not available through official API",
                "job_recommendations": "Not available through standard API"
            },
            "required_permissions": {
                "job_posting_api": "Required for creating and managing job postings",
                "company_admin": "Required for accessing company job data",
                "analytics_api": "Required for job posting analytics"
            },
            "migration_notes": {
                "from_scraping": "Official API has much more limited job access than scraping",
                "data_coverage": "Only your own company's jobs are accessible",
                "public_search": "Public job search is not supported",
                "alternative": "Consider maintaining scraping approach for public job data with appropriate compliance"
            },
            "compliance": {
                "official_api": "Fully compliant with LinkedIn Terms of Service",
                "rate_limits": "Apply according to your API product tier",
                "enterprise_options": "Contact LinkedIn for enterprise job data solutions"
            }
        }
