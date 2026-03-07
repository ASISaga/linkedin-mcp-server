# src/linkedin_mcp_server/tools/social.py
"""
LinkedIn social action tools using official LinkedIn API.

Provides MCP tools for social interactions including reactions, comments,
and UGC (User Generated Content) posts through the official LinkedIn API
with OAuth 2.0 authentication.

Requires the 'w_member_social' OAuth scope for write operations and
'r_member_social' or 'r_organization_social' for read operations.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from linkedin_mcp_server.linkedin_auth import get_authenticated_client, get_access_token
from linkedin_mcp_server.exceptions import APIError

logger = logging.getLogger(__name__)


def register_social_tools(mcp: FastMCP) -> None:
    """
    Register all social action tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool()
    async def add_post_reaction(
        post_urn: str,
        reaction_type: str = "LIKE",
        actor_urn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a reaction to a LinkedIn post.

        Requires 'w_member_social' scope.

        Args:
            post_urn (str): URN of the post to react to (e.g., "urn:li:ugcPost:123")
            reaction_type (str): Type of reaction. Options: LIKE, PRAISE, APPRECIATION,
                                EMPATHY, INTEREST, ENTERTAINMENT. Default: LIKE
            actor_urn (str, optional): URN of the actor (person or organization).
                                      If not provided, uses the authenticated user.

        Returns:
            Dict[str, Any]: Reaction result
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            reaction_entity: Dict[str, Any] = {
                "reactionType": reaction_type,
            }
            if actor_urn:
                reaction_entity["actor"] = actor_urn

            logger.info(f"Adding {reaction_type} reaction to post: {post_urn}")
            response = client.create(
                resource_path="/reactions",
                entity=reaction_entity,
                access_token=access_token,
                query_params={"actor": actor_urn} if actor_urn else None,
            )

            if response.status_code not in [200, 201]:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "success": True,
                "post_urn": post_urn,
                "reaction_type": reaction_type,
                "message": f"Successfully added {reaction_type} reaction",
            }

        except Exception as e:
            logger.error(f"Error in add_post_reaction: {e}")
            return {
                "error": "Failed to add reaction",
                "message": str(e),
                "note": "Requires 'w_member_social' scope",
            }

    @mcp.tool()
    async def get_post_reactions(
        post_urn: str,
        start: int = 0,
        count: int = 20,
    ) -> Dict[str, Any]:
        """
        Get reactions for a LinkedIn post.

        Requires 'r_member_social' scope.

        Args:
            post_urn (str): URN of the post (e.g., "urn:li:ugcPost:123")
            start (int): Starting index for pagination
            count (int): Number of reactions to retrieve (max 100)

        Returns:
            Dict[str, Any]: Reactions list and metadata
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Fetching reactions for post: {post_urn}")
            response = client.finder(
                resource_path="/reactions",
                finder_name="entity",
                access_token=access_token,
                query_params={
                    "entity": post_urn,
                    "start": start,
                    "count": min(count, 100),
                },
            )

            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "reactions": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "post_urn": post_urn,
            }

        except Exception as e:
            logger.error(f"Error in get_post_reactions: {e}")
            return {
                "error": "Failed to fetch reactions",
                "message": str(e),
                "note": "Requires 'r_member_social' scope",
            }

    @mcp.tool()
    async def add_post_comment(
        post_urn: str,
        comment_text: str,
        actor_urn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a comment to a LinkedIn post.

        Requires 'w_member_social' scope.

        Args:
            post_urn (str): URN of the post to comment on (e.g., "urn:li:ugcPost:123")
            comment_text (str): Text content of the comment
            actor_urn (str, optional): URN of the actor (person or organization).
                                      If not provided, uses the authenticated user.

        Returns:
            Dict[str, Any]: Created comment information
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            comment_entity: Dict[str, Any] = {
                "object": post_urn,
                "message": {
                    "text": comment_text,
                },
            }
            if actor_urn:
                comment_entity["actor"] = actor_urn

            logger.info(f"Adding comment to post: {post_urn}")
            response = client.create(
                resource_path="/comments",
                entity=comment_entity,
                access_token=access_token,
            )

            if response.status_code not in [200, 201]:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "success": True,
                "comment_id": response.entity_id,
                "comment_urn": f"urn:li:comment:{response.entity_id}",
                "post_urn": post_urn,
            }

        except Exception as e:
            logger.error(f"Error in add_post_comment: {e}")
            return {
                "error": "Failed to add comment",
                "message": str(e),
                "note": "Requires 'w_member_social' scope",
            }

    @mcp.tool()
    async def get_post_comments(
        post_urn: str,
        start: int = 0,
        count: int = 20,
    ) -> Dict[str, Any]:
        """
        Get comments for a LinkedIn post.

        Requires 'r_member_social' scope.

        Args:
            post_urn (str): URN of the post (e.g., "urn:li:ugcPost:123")
            start (int): Starting index for pagination
            count (int): Number of comments to retrieve (max 100)

        Returns:
            Dict[str, Any]: Comments list and metadata
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Fetching comments for post: {post_urn}")
            response = client.finder(
                resource_path="/comments",
                finder_name="object",
                access_token=access_token,
                query_params={
                    "object": post_urn,
                    "start": start,
                    "count": min(count, 100),
                },
            )

            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "comments": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "post_urn": post_urn,
            }

        except Exception as e:
            logger.error(f"Error in get_post_comments: {e}")
            return {
                "error": "Failed to fetch comments",
                "message": str(e),
                "note": "Requires 'r_member_social' scope",
            }

    @mcp.tool()
    async def create_ugc_post(ugc_post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a User Generated Content (UGC) post on LinkedIn.

        This uses the UGC Posts API which supports richer content types
        including articles, images, and video content.

        Requires 'w_member_social' scope.

        Args:
            ugc_post_data (Dict[str, Any]): UGC post data structure.
                Example: {
                    "author": "urn:li:person:ABC123",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": "Post text"},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }

        Returns:
            Dict[str, Any]: Created UGC post information
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Creating UGC post for: {ugc_post_data.get('author')}")
            response = client.create(
                resource_path="/ugcPosts",
                entity=ugc_post_data,
                access_token=access_token,
            )

            if response.status_code not in [200, 201]:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "success": True,
                "ugc_post_id": response.entity_id,
                "ugc_post_urn": f"urn:li:ugcPost:{response.entity_id}",
                "author": ugc_post_data.get("author"),
            }

        except Exception as e:
            logger.error(f"Error in create_ugc_post: {e}")
            return {
                "error": "Failed to create UGC post",
                "message": str(e),
                "note": "Requires 'w_member_social' scope",
            }

    @mcp.tool()
    async def get_ugc_posts(
        author_urn: str,
        start: int = 0,
        count: int = 20,
    ) -> Dict[str, Any]:
        """
        Get UGC posts authored by a specific person or organization.

        Requires 'r_member_social' or 'r_organization_social' scope.

        Args:
            author_urn (str): URN of the author (e.g., "urn:li:person:ABC123"
                             or "urn:li:organization:123")
            start (int): Starting index for pagination
            count (int): Number of posts to retrieve (max 100)

        Returns:
            Dict[str, Any]: UGC posts list and metadata
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Fetching UGC posts for author: {author_urn}")
            response = client.finder(
                resource_path="/ugcPosts",
                finder_name="authors",
                access_token=access_token,
                query_params={
                    "authors": f"List({author_urn})",
                    "start": start,
                    "count": min(count, 100),
                },
            )

            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "ugc_posts": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "author_urn": author_urn,
            }

        except Exception as e:
            logger.error(f"Error in get_ugc_posts: {e}")
            return {
                "error": "Failed to fetch UGC posts",
                "message": str(e),
                "note": "Requires 'r_member_social' or 'r_organization_social' scope",
            }

    @mcp.tool()
    async def get_shares(
        owner_urn: str,
        start: int = 0,
        count: int = 20,
    ) -> Dict[str, Any]:
        """
        Get shares (posts) for a person or organization using the Shares API.

        Requires 'r_member_social' or 'r_organization_social' scope.

        Args:
            owner_urn (str): URN of the owner (e.g., "urn:li:person:ABC123"
                            or "urn:li:organization:123")
            start (int): Starting index for pagination
            count (int): Number of shares to retrieve (max 100)

        Returns:
            Dict[str, Any]: Shares list and metadata
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Fetching shares for owner: {owner_urn}")
            response = client.finder(
                resource_path="/shares",
                finder_name="owners",
                access_token=access_token,
                query_params={
                    "owners": f"List({owner_urn})",
                    "start": start,
                    "count": min(count, 100),
                },
            )

            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "shares": response.elements,
                "paging": response.paging.__dict__ if response.paging else None,
                "owner_urn": owner_urn,
            }

        except Exception as e:
            logger.error(f"Error in get_shares: {e}")
            return {
                "error": "Failed to fetch shares",
                "message": str(e),
                "note": "Requires 'r_member_social' or 'r_organization_social' scope",
            }

    @mcp.tool()
    async def get_social_actions_summary(entity_urn: str) -> Dict[str, Any]:
        """
        Get social actions summary (likes, comments, shares counts) for a post.

        Requires 'r_member_social' scope.

        Args:
            entity_urn (str): URN of the post or entity
                             (e.g., "urn:li:ugcPost:123" or "urn:li:share:123")

        Returns:
            Dict[str, Any]: Social actions summary with counts
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()

            logger.info(f"Fetching social actions summary for: {entity_urn}")
            response = client.get(
                resource_path="/socialMetadata/{entityUrn}",
                path_keys={"entityUrn": entity_urn},
                access_token=access_token,
            )

            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")

            return {
                "social_metadata": response.entity,
                "entity_urn": entity_urn,
            }

        except Exception as e:
            logger.error(f"Error in get_social_actions_summary: {e}")
            return {
                "error": "Failed to fetch social actions summary",
                "message": str(e),
                "note": "Requires 'r_member_social' scope",
            }

    @mcp.tool()
    async def get_social_api_info() -> Dict[str, Any]:
        """
        Get information about available LinkedIn social API endpoints and required scopes.

        Returns:
            Dict[str, Any]: Information about social API capabilities and permissions
        """
        return {
            "available_endpoints": {
                "reactions": {
                    "add_post_reaction": "Add a reaction (LIKE, PRAISE, etc.) to a post",
                    "get_post_reactions": "Retrieve reactions for a specific post",
                    "required_scope": "w_member_social (write), r_member_social (read)",
                },
                "comments": {
                    "add_post_comment": "Add a text comment to a post",
                    "get_post_comments": "Retrieve comments for a specific post",
                    "required_scope": "w_member_social (write), r_member_social (read)",
                },
                "ugc_posts": {
                    "create_ugc_post": "Create rich UGC posts with media and articles",
                    "get_ugc_posts": "Retrieve UGC posts by author",
                    "required_scope": "w_member_social (write), r_member_social (read)",
                },
                "shares": {
                    "get_shares": "Retrieve shares/posts for a person or organization",
                    "required_scope": "r_member_social or r_organization_social",
                },
                "social_metadata": {
                    "get_social_actions_summary": "Get aggregate counts (likes, comments, shares)",
                    "required_scope": "r_member_social",
                },
            },
            "supported_reaction_types": [
                "LIKE",
                "PRAISE",
                "APPRECIATION",
                "EMPATHY",
                "INTEREST",
                "ENTERTAINMENT",
            ],
            "required_api_products": [
                "Sign In with LinkedIn using OpenID Connect",
                "Share on LinkedIn",
                "Marketing Developer Platform (for organization social)",
            ],
        }
