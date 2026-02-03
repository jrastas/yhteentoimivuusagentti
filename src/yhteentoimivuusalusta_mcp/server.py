"""MCP Server for Yhteentoimivuusalusta.

This server provides tools for accessing Finland's Interoperability Platform:
- Sanastot (Terminologies)
- Tietomallit (Data Models)
- Koodistot (Code Lists)
"""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from yhteentoimivuusalusta_mcp.clients.koodistot import KoodistotClient
from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.clients.tietomallit import TietomalditClient
from yhteentoimivuusalusta_mcp.tools.codelist import export_codes_csv, get_codes, search_codelist
from yhteentoimivuusalusta_mcp.tools.datamodel import (
    get_datamodel_classes,
    get_model_vocabulary_links,
    search_datamodel,
)
from yhteentoimivuusalusta_mcp.tools.terminology import (
    get_concept_details,
    list_vocabularies,
    search_terminology,
)
from yhteentoimivuusalusta_mcp.tools.unified import (
    get_codelist_for_attribute,
    suggest_references,
    unified_search,
)
from yhteentoimivuusalusta_mcp.tools.validation import validate_terminology
from yhteentoimivuusalusta_mcp.utils.cache import CacheManager
from yhteentoimivuusalusta_mcp.utils.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when tool arguments fail validation."""

    pass


def validate_required(arguments: dict[str, Any], *required_params: str) -> None:
    """Validate that required parameters are present and non-empty.

    Args:
        arguments: The tool arguments dict.
        *required_params: Names of required parameters.

    Raises:
        ValidationError: If a required parameter is missing or empty.
    """
    for param in required_params:
        if param not in arguments:
            raise ValidationError(f"Missing required parameter: '{param}'")
        value = arguments[param]
        if value is None:
            raise ValidationError(f"Parameter '{param}' cannot be null")
        if isinstance(value, str) and not value.strip():
            raise ValidationError(f"Parameter '{param}' cannot be empty")


def validate_max_results(arguments: dict[str, Any], param: str = "max_results") -> int:
    """Validate and constrain max_results parameter.

    Args:
        arguments: The tool arguments dict.
        param: Name of the parameter (default: 'max_results').

    Returns:
        Validated max_results value (1-1000).
    """
    value = arguments.get(param, 10)
    if not isinstance(value, int) or value < 1:
        return 10
    return min(value, 1000)  # Cap at 1000


def validate_text_length(arguments: dict[str, Any], param: str, max_length: int = 10000) -> str:
    """Validate text parameter length.

    Args:
        arguments: The tool arguments dict.
        param: Name of the text parameter.
        max_length: Maximum allowed length.

    Returns:
        The text value (truncated if needed).

    Raises:
        ValidationError: If the text parameter is missing.
    """
    if param not in arguments:
        raise ValidationError(f"Missing required parameter: '{param}'")
    text = arguments[param]
    if not isinstance(text, str):
        raise ValidationError(f"Parameter '{param}' must be a string")
    if len(text) > max_length:
        logger.warning(f"Text parameter '{param}' truncated from {len(text)} to {max_length} chars")
        return text[:max_length]
    return text

# Tool definitions
TOOLS = [
    Tool(
        name="search_terminology",
        description=(
            "Search for Finnish government standardized terms and concepts from "
            "sanastot.suomi.fi. Use this to find correct terminology for design "
            "documentation, technical specifications, or architecture descriptions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term in Finnish or English",
                },
                "vocabulary_id": {
                    "type": "string",
                    "description": (
                        "Optional: Limit to specific vocabulary (e.g., 'rakymp' for "
                        "built environment, 'jhka' for public admin)"
                    ),
                },
                "language": {
                    "type": "string",
                    "enum": ["fi", "en", "sv"],
                    "default": "fi",
                    "description": "Search language",
                },
                "max_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum results to return",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_concept_details",
        description=(
            "Get detailed information about a concept including all terms, "
            "definitions in multiple languages, and relationships to other concepts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "vocabulary_id": {
                    "type": "string",
                    "description": "The vocabulary containing the concept (e.g., 'rakymp')",
                },
                "concept_id": {
                    "type": "string",
                    "description": "The concept identifier",
                },
                "include_relations": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include broader/narrower/related concepts",
                },
            },
            "required": ["vocabulary_id", "concept_id"],
        },
    ),
    Tool(
        name="list_vocabularies",
        description=(
            "List all available vocabularies from sanastot.suomi.fi with optional "
            "filtering by domain or status. Useful for discovering relevant "
            "terminology collections."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": (
                        "Filter by domain (e.g., 'Rakennettu ympäristö', 'Koulutus')"
                    ),
                },
                "status": {
                    "type": "string",
                    "enum": ["VALID", "DRAFT", "INCOMPLETE"],
                    "description": "Filter by status",
                },
            },
        },
    ),
    Tool(
        name="search_datamodel",
        description=(
            "Search for data models and schemas from tietomallit.suomi.fi. "
            "Find standardized data structures for Finnish government systems."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term for model name or content",
                },
                "model_type": {
                    "type": "string",
                    "enum": ["PROFILE", "LIBRARY"],
                    "description": (
                        "PROFILE = application profile, LIBRARY = reusable components"
                    ),
                },
                "domain": {
                    "type": "string",
                    "description": "Filter by domain (e.g., 'Rakennettu ympäristö')",
                },
                "max_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum results to return",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_datamodel_classes",
        description=(
            "Get class definitions from a data model including properties and "
            "associations. Use this to understand the structure of a data model."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model_id": {
                    "type": "string",
                    "description": "The data model identifier (e.g., 'rytj-kaava')",
                },
                "class_name": {
                    "type": "string",
                    "description": "Optional: filter to specific class",
                },
                "include_properties": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include class properties",
                },
                "include_associations": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include class associations",
                },
            },
            "required": ["model_id"],
        },
    ),
    Tool(
        name="get_model_vocabulary_links",
        description=(
            "Get vocabulary concepts linked to a data model. Shows which "
            "terminology concepts are referenced by the model's classes and properties."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model_id": {
                    "type": "string",
                    "description": "The data model identifier (e.g., 'rytj-kaava')",
                },
            },
            "required": ["model_id"],
        },
    ),
    Tool(
        name="search_codelist",
        description=(
            "Search for code lists from koodistot.suomi.fi. Find enumerated "
            "value sets and classifications used in Finnish systems."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term for code list name or content",
                },
                "registry": {
                    "type": "string",
                    "description": "Limit to specific code registry",
                },
                "max_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum results to return",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_codes",
        description=(
            "Get all code values from a specific code list. Use this to get "
            "valid enumeration values for a particular domain."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "registry": {
                    "type": "string",
                    "description": "Code registry ID (e.g., 'rakennustieto')",
                },
                "scheme": {
                    "type": "string",
                    "description": "Code scheme ID (e.g., 'RakennuksenKayttotarkoitus')",
                },
                "status": {
                    "type": "string",
                    "enum": ["VALID", "DRAFT", "DEPRECATED"],
                    "default": "VALID",
                    "description": "Filter by status",
                },
                "max_results": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum codes to return",
                },
            },
            "required": ["registry", "scheme"],
        },
    ),
    Tool(
        name="export_codes_csv",
        description=(
            "Export all codes from a code list as CSV format. Useful for "
            "importing into spreadsheets or other systems."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "registry": {
                    "type": "string",
                    "description": "Code registry ID (e.g., 'rakennustieto')",
                },
                "scheme": {
                    "type": "string",
                    "description": "Code scheme ID (e.g., 'RakennuksenKayttotarkoitus')",
                },
                "status": {
                    "type": "string",
                    "enum": ["VALID", "DRAFT", "DEPRECATED"],
                    "default": "VALID",
                    "description": "Filter by status",
                },
                "include_header": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include CSV header row",
                },
            },
            "required": ["registry", "scheme"],
        },
    ),
    Tool(
        name="validate_terminology",
        description=(
            "Validate terminology usage in design documentation against Finnish "
            "government standards. Checks text for non-standard terms and suggests "
            "corrections using fuzzy matching."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to validate (max 10000 characters)",
                    "maxLength": 10000,
                },
                "vocabularies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Vocabulary IDs to check against (e.g., ['rakymp']). "
                        "Default: checks all vocabularies."
                    ),
                },
                "suggest_corrections": {
                    "type": "boolean",
                    "default": True,
                    "description": "Suggest corrections for non-standard terms",
                },
                "fuzzy_threshold": {
                    "type": "number",
                    "default": 0.8,
                    "minimum": 0.5,
                    "maximum": 1.0,
                    "description": "Similarity threshold for fuzzy matching (0.5-1.0)",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="unified_search",
        description=(
            "Search across all Yhteentoimivuusalusta platforms simultaneously. "
            "Finds related terminologies, data models, and code lists in one query."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to find across all platforms",
                },
                "search_terminologies": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include terminology search (sanastot.suomi.fi)",
                },
                "search_datamodels": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include data model search (tietomallit.suomi.fi)",
                },
                "search_codelists": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include code list search (koodistot.suomi.fi)",
                },
                "max_results_per_platform": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum results per platform",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="suggest_references",
        description=(
            "Analyze text and suggest relevant standards to reference. "
            "Extracts key terms and finds matching vocabularies, data models, and code lists."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze (e.g., design document excerpt)",
                },
                "max_suggestions": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum suggestions per category",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="get_codelist_for_attribute",
        description=(
            "Find code lists that could be used for data model attributes. "
            "Analyzes a data model and suggests relevant code lists for its properties."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model_id": {
                    "type": "string",
                    "description": "The data model identifier (e.g., 'rytj-kaava')",
                },
                "class_name": {
                    "type": "string",
                    "description": "Optional: filter to specific class",
                },
            },
            "required": ["model_id"],
        },
    ),
]


class YhteentoimivuusalustaServer:
    """MCP Server for Yhteentoimivuusalusta APIs."""

    def __init__(self) -> None:
        """Initialize the server."""
        self.config = load_config()
        self.cache = CacheManager(
            enabled=self.config.cache.enabled,
            directory=self.config.cache.directory,
        )

        # Initialize API clients
        self.sanastot = SanastotClient(
            base_url=self.config.sanastot.base_url,
            timeout=self.config.sanastot.timeout,
            retry_count=self.config.sanastot.retry_count,
            cache=self.cache,
        )
        self.tietomallit = TietomalditClient(
            base_url=self.config.tietomallit.base_url,
            timeout=self.config.tietomallit.timeout,
            retry_count=self.config.tietomallit.retry_count,
            cache=self.cache,
        )
        self.koodistot = KoodistotClient(
            base_url=self.config.koodistot.base_url,
            timeout=self.config.koodistot.timeout,
            retry_count=self.config.koodistot.retry_count,
            cache=self.cache,
        )

        # Create MCP server
        self.server = Server("yhteentoimivuusalusta-mcp")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP request handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return TOOLS

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                result = await self._handle_tool_call(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                error_result = {"error": str(e), "tool": name, "arguments": arguments}
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def _handle_tool_call(self, name: str, arguments: dict[str, Any]) -> dict:
        """Route tool calls to appropriate handlers.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            Tool result dictionary.
        """
        if name == "search_terminology":
            validate_required(arguments, "query")
            return await search_terminology(
                client=self.sanastot,
                query=arguments["query"].strip(),
                vocabulary_id=arguments.get("vocabulary_id"),
                language=arguments.get("language", "fi"),
                max_results=validate_max_results(arguments),
            )

        elif name == "get_concept_details":
            validate_required(arguments, "vocabulary_id", "concept_id")
            return await get_concept_details(
                client=self.sanastot,
                vocabulary_id=arguments["vocabulary_id"].strip(),
                concept_id=arguments["concept_id"].strip(),
                include_relations=arguments.get("include_relations", True),
            )

        elif name == "list_vocabularies":
            return await list_vocabularies(
                client=self.sanastot,
                domain=arguments.get("domain"),
                status=arguments.get("status"),
            )

        elif name == "search_datamodel":
            validate_required(arguments, "query")
            return await search_datamodel(
                client=self.tietomallit,
                query=arguments["query"].strip(),
                model_type=arguments.get("model_type"),
                domain=arguments.get("domain"),
                max_results=validate_max_results(arguments),
            )

        elif name == "get_datamodel_classes":
            validate_required(arguments, "model_id")
            return await get_datamodel_classes(
                client=self.tietomallit,
                model_id=arguments["model_id"].strip(),
                class_name=arguments.get("class_name"),
                include_properties=arguments.get("include_properties", True),
                include_associations=arguments.get("include_associations", True),
            )

        elif name == "get_model_vocabulary_links":
            validate_required(arguments, "model_id")
            return await get_model_vocabulary_links(
                tietomallit_client=self.tietomallit,
                sanastot_client=self.sanastot,
                model_id=arguments["model_id"].strip(),
            )

        elif name == "search_codelist":
            validate_required(arguments, "query")
            return await search_codelist(
                client=self.koodistot,
                query=arguments["query"].strip(),
                registry=arguments.get("registry"),
                max_results=validate_max_results(arguments),
            )

        elif name == "get_codes":
            validate_required(arguments, "registry", "scheme")
            return await get_codes(
                client=self.koodistot,
                registry=arguments["registry"].strip(),
                scheme=arguments["scheme"].strip(),
                status=arguments.get("status", "VALID"),
                max_results=validate_max_results(arguments, "max_results"),
            )

        elif name == "export_codes_csv":
            validate_required(arguments, "registry", "scheme")
            return await export_codes_csv(
                client=self.koodistot,
                registry=arguments["registry"].strip(),
                scheme=arguments["scheme"].strip(),
                status=arguments.get("status", "VALID"),
                include_header=arguments.get("include_header", True),
            )

        elif name == "validate_terminology":
            text = validate_text_length(arguments, "text", max_length=50000)
            return await validate_terminology(
                client=self.sanastot,
                text=text,
                vocabularies=arguments.get("vocabularies"),
                suggest_corrections=arguments.get("suggest_corrections", True),
                fuzzy_threshold=arguments.get("fuzzy_threshold", 0.8),
            )

        elif name == "unified_search":
            validate_required(arguments, "query")
            return await unified_search(
                sanastot_client=self.sanastot,
                tietomallit_client=self.tietomallit,
                koodistot_client=self.koodistot,
                query=arguments["query"].strip(),
                search_terminologies=arguments.get("search_terminologies", True),
                search_datamodels=arguments.get("search_datamodels", True),
                search_codelists=arguments.get("search_codelists", True),
                max_results_per_platform=min(arguments.get("max_results_per_platform", 5), 50),
            )

        elif name == "suggest_references":
            text = validate_text_length(arguments, "text", max_length=50000)
            return await suggest_references(
                sanastot_client=self.sanastot,
                tietomallit_client=self.tietomallit,
                koodistot_client=self.koodistot,
                text=text,
                max_suggestions=min(arguments.get("max_suggestions", 10), 100),
            )

        elif name == "get_codelist_for_attribute":
            validate_required(arguments, "model_id")
            return await get_codelist_for_attribute(
                tietomallit_client=self.tietomallit,
                koodistot_client=self.koodistot,
                model_id=arguments["model_id"].strip(),
                class_name=arguments.get("class_name"),
            )

        else:
            return {"error": f"Unknown tool: {name}"}

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.sanastot.close()
        await self.tietomallit.close()
        await self.koodistot.close()
        self.cache.close()

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            try:
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
            finally:
                await self.cleanup()


def main() -> None:
    """Main entry point."""
    server = YhteentoimivuusalustaServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
