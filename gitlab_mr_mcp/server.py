#!/usr/bin/env python3
import asyncio
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptMessage,
    TextContent,
    Tool,
)

from gitlab_mr_mcp.config import get_gitlab_config
from gitlab_mr_mcp.logging_config import configure_logging
from gitlab_mr_mcp.prompts import PROMPTS
from gitlab_mr_mcp.tools import (
    approve_merge_request,
    create_merge_request,
    create_review_comment,
    get_branch_merge_requests,
    get_commit_discussions,
    get_job_log,
    get_merge_request_details,
    get_merge_request_pipeline,
    get_merge_request_reviews,
    get_merge_request_test_report,
    get_pipeline_test_summary,
    list_merge_requests,
    list_my_projects,
    list_project_labels,
    list_project_members,
    merge_merge_request,
    reply_to_review_comment,
    resolve_review_discussion,
    search_projects,
    unapprove_merge_request,
    update_merge_request,
)

PROJECT_ID_SCHEMA = {
    "type": "string",
    "description": "Project ID or 'group/project'. Unknown? Call search_projects first.",
}

MR_IID = {
    "type": "integer",
    "minimum": 1,
    "description": "MR internal ID",
}


def resolve_project_id(arguments, default_project_id):
    """Resolve project_id from arguments or fall back to default."""
    project_id = arguments.get("project_id") or default_project_id
    if not project_id:
        raise ValueError(
            "project_id is required but not provided. "
            "Please call search_projects(search='project name') or list_my_projects() first to find the project ID, "
            "then pass it as project_id parameter."
        )
    return project_id


class GitLabMCPServer:
    def __init__(self):
        configure_logging()
        logging.info("Initializing GitLabMCPServer")

        self.config = get_gitlab_config()

        self.server = Server(self.config["server_name"])
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            logging.info("list_tools called")
            read_only = {"readOnlyHint": True}
            write_op = {"readOnlyHint": False}
            destructive = {"readOnlyHint": False, "destructiveHint": True}

            tools = [
                Tool(
                    name="search_projects",
                    title="Search Projects",
                    description="Find projects by name. Use first when project is unknown.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search": {"type": "string", "description": "Project name or partial name"},
                            "membership": {"type": "boolean", "default": True},
                            "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100},
                        },
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="list_my_projects",
                    title="List All Projects",
                    description="List all accessible projects. Slow — use search_projects if you know the name.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owned": {"type": "boolean", "default": False},
                            "limit": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
                        },
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="list_merge_requests",
                    title="List Merge Requests",
                    description="List MRs with optional filters.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "state": {
                                "type": "string",
                                "enum": ["opened", "closed", "merged", "all"],
                                "default": "opened",
                            },
                            "target_branch": {"type": "string"},
                            "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100},
                        },
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_merge_request_reviews",
                    title="Get MR Reviews",
                    description="Get MR reviews and discussions. Returns discussion IDs.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_merge_request_details",
                    title="Get MR Details",
                    description="Get MR status, approvals, and merge readiness.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_merge_request_pipeline",
                    title="Get MR Pipeline",
                    description="Get pipeline jobs and statuses. Returns job IDs for get_job_log.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_merge_request_test_report",
                    title="Get MR Test Report",
                    description="Get test failures with error messages and stack traces.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_pipeline_test_summary",
                    title="Get Test Summary",
                    description="Get test pass/fail counts. Faster than full test report.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_job_log",
                    title="Get Job Log",
                    description="Get CI job log. Use job IDs from get_merge_request_pipeline.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "job_id": {"type": "integer", "minimum": 1, "description": "Job ID"},
                        },
                        "required": ["job_id"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_branch_merge_requests",
                    title="Get Branch MRs",
                    description="Get MRs for a branch.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "branch_name": {"type": "string"},
                        },
                        "required": ["branch_name"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="reply_to_review_comment",
                    title="Reply to Discussion",
                    description="Reply to a discussion thread.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "discussion_id": {"type": "string"},
                            "body": {"type": "string"},
                        },
                        "required": ["merge_request_iid", "discussion_id", "body"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="create_review_comment",
                    title="Create Discussion",
                    description="Create a new discussion thread on an MR.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "body": {"type": "string"},
                        },
                        "required": ["merge_request_iid", "body"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="resolve_review_discussion",
                    title="Resolve Discussion",
                    description="Resolve or unresolve a discussion thread.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "discussion_id": {"type": "string"},
                            "resolved": {"type": "boolean", "default": True},
                        },
                        "required": ["merge_request_iid", "discussion_id"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_commit_discussions",
                    title="Get Commit Discussions",
                    description="Get discussions on commits within an MR.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="list_project_members",
                    title="List Project Members",
                    description="List project members and access levels.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {"project_id": PROJECT_ID_SCHEMA},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="list_project_labels",
                    title="List Project Labels",
                    description="List project labels including inherited ones.",
                    annotations=read_only,
                    inputSchema={
                        "type": "object",
                        "properties": {"project_id": PROJECT_ID_SCHEMA},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="create_merge_request",
                    title="Create Merge Request",
                    description="Create an MR. Accepts usernames for assignees/reviewers.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "source_branch": {"type": "string"},
                            "target_branch": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "draft": {"type": "boolean", "default": False},
                            "squash": {"type": "boolean"},
                            "remove_source_branch": {"type": "boolean"},
                            "labels": {"type": "array", "items": {"type": "string"}},
                            "create_missing_labels": {"type": "boolean", "default": False},
                            "assignees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Usernames e.g. ['john.doe']",
                            },
                            "reviewers": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["source_branch", "target_branch", "title"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="update_merge_request",
                    title="Update Merge Request",
                    description="Update an MR. Pass empty arrays to clear assignees/reviewers/labels.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "target_branch": {"type": "string"},
                            "draft": {"type": "boolean"},
                            "squash": {"type": "boolean"},
                            "remove_source_branch": {"type": "boolean"},
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Replaces existing. Empty array clears.",
                            },
                            "assignees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Replaces existing. Empty array clears.",
                            },
                            "reviewers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Replaces existing. Empty array clears.",
                            },
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="merge_merge_request",
                    title="Merge MR",
                    description="Merge an MR. Check status with get_merge_request_details first.",
                    annotations=destructive,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "squash": {"type": "boolean", "default": False},
                            "should_remove_source_branch": {"type": "boolean", "default": False},
                            "merge_when_pipeline_succeeds": {"type": "boolean", "default": False},
                            "sha": {
                                "type": "string",
                                "description": "HEAD SHA for safety check (ensures no new commits)",
                            },
                            "merge_commit_message": {"type": "string"},
                            "squash_commit_message": {"type": "string"},
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="approve_merge_request",
                    title="Approve MR",
                    description="Approve an MR. Cannot approve your own.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                            "sha": {
                                "type": "string",
                                "description": "HEAD SHA to ensure approving the right version",
                            },
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="unapprove_merge_request",
                    title="Unapprove MR",
                    description="Revoke approval from an MR.",
                    annotations=write_op,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": PROJECT_ID_SCHEMA,
                            "merge_request_iid": MR_IID,
                        },
                        "required": ["merge_request_iid"],
                        "additionalProperties": False,
                    },
                ),
            ]
            tool_names = [t.name for t in tools]
            logging.info(f"Returning {len(tools)} tools: {tool_names}")
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            logging.info(f"call_tool called: {name} with arguments: {arguments}")

            try:
                valid_tools = [
                    "search_projects",
                    "list_my_projects",
                    "list_merge_requests",
                    "get_merge_request_reviews",
                    "get_merge_request_details",
                    "get_merge_request_pipeline",
                    "get_merge_request_test_report",
                    "get_pipeline_test_summary",
                    "get_job_log",
                    "get_branch_merge_requests",
                    "reply_to_review_comment",
                    "create_review_comment",
                    "resolve_review_discussion",
                    "get_commit_discussions",
                    "list_project_members",
                    "list_project_labels",
                    "create_merge_request",
                    "update_merge_request",
                    "merge_merge_request",
                    "approve_merge_request",
                    "unapprove_merge_request",
                ]

                if name not in valid_tools:
                    logging.warning(f"Unknown tool called: {name}")
                    raise McpError(error=ErrorData(code=METHOD_NOT_FOUND, message=f"Unknown tool: {name}"))

                gitlab_url = self.config["gitlab_url"]
                access_token = self.config["access_token"]
                default_project_id = self.config["project_id"]

                if name == "search_projects":
                    return await search_projects(gitlab_url, access_token, arguments)
                elif name == "list_my_projects":
                    return await list_my_projects(gitlab_url, access_token, arguments)

                project_id = resolve_project_id(arguments, default_project_id)

                if name == "list_merge_requests":
                    return await list_merge_requests(gitlab_url, project_id, access_token, arguments)
                elif name == "get_merge_request_reviews":
                    return await get_merge_request_reviews(gitlab_url, project_id, access_token, arguments)
                elif name == "get_merge_request_details":
                    return await get_merge_request_details(gitlab_url, project_id, access_token, arguments)
                elif name == "get_merge_request_pipeline":
                    return await get_merge_request_pipeline(gitlab_url, project_id, access_token, arguments)
                elif name == "get_merge_request_test_report":
                    return await get_merge_request_test_report(gitlab_url, project_id, access_token, arguments)
                elif name == "get_pipeline_test_summary":
                    return await get_pipeline_test_summary(gitlab_url, project_id, access_token, arguments)
                elif name == "get_job_log":
                    return await get_job_log(gitlab_url, project_id, access_token, arguments)
                elif name == "get_branch_merge_requests":
                    return await get_branch_merge_requests(gitlab_url, project_id, access_token, arguments)
                elif name == "reply_to_review_comment":
                    return await reply_to_review_comment(gitlab_url, project_id, access_token, arguments)
                elif name == "create_review_comment":
                    return await create_review_comment(gitlab_url, project_id, access_token, arguments)
                elif name == "resolve_review_discussion":
                    return await resolve_review_discussion(gitlab_url, project_id, access_token, arguments)
                elif name == "get_commit_discussions":
                    return await get_commit_discussions(gitlab_url, project_id, access_token, arguments)
                elif name == "list_project_members":
                    return await list_project_members(gitlab_url, project_id, access_token, arguments)
                elif name == "list_project_labels":
                    return await list_project_labels(gitlab_url, project_id, access_token, arguments)
                elif name == "create_merge_request":
                    return await create_merge_request(gitlab_url, project_id, access_token, arguments)
                elif name == "update_merge_request":
                    return await update_merge_request(gitlab_url, project_id, access_token, arguments)
                elif name == "merge_merge_request":
                    return await merge_merge_request(gitlab_url, project_id, access_token, arguments)
                elif name == "approve_merge_request":
                    return await approve_merge_request(gitlab_url, project_id, access_token, arguments)
                elif name == "unapprove_merge_request":
                    return await unapprove_merge_request(gitlab_url, project_id, access_token, arguments)

            except ValueError as e:
                logging.error(f"Validation error in {name}: {e}")
                raise McpError(error=ErrorData(code=INVALID_PARAMS, message=f"Invalid parameters: {str(e)}"))
            except Exception as e:
                logging.error(f"Unexpected error in call_tool for {name}: {e}", exc_info=True)
                raise McpError(error=ErrorData(code=INTERNAL_ERROR, message=f"Internal server error: {str(e)}"))

        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            return [Prompt(name=name, description=data["description"]) for name, data in PROMPTS.items()]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
            if name not in PROMPTS:
                raise McpError(error=ErrorData(code=METHOD_NOT_FOUND, message=f"Unknown prompt: {name}"))
            prompt_data = PROMPTS[name]
            return GetPromptResult(
                description=prompt_data["description"],
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt_data["content"]),
                    )
                ],
            )

    async def run(self):
        logging.info("Starting MCP stdio server")
        try:
            async with stdio_server() as (read_stream, write_stream):
                logging.info("stdio_server context entered successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config["server_name"],
                        server_version=self.config["server_version"],
                        capabilities={"tools": {}, "prompts": {}, "logging": {}},
                    ),
                )
        except Exception as e:
            logging.error(f"Error in stdio_server: {e}", exc_info=True)
            raise


async def main():
    try:
        logging.info("Starting main function")
        server = GitLabMCPServer()
        logging.info("GitLabMCPServer created successfully")
        await server.run()
    except Exception as e:
        logging.error(f"Error starting server: {e}", exc_info=True)
        print(f"Error starting server: {e}")  # noqa: T201
        return 1


def main_sync():
    """Synchronous entry point for console script."""
    return asyncio.run(main())


if __name__ == "__main__":
    main_sync()
