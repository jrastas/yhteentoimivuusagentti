"""Code list tools for Koodistot API."""

import csv
import io

from yhteentoimivuusalusta_mcp.clients.koodistot import KoodistotClient
from yhteentoimivuusalusta_mcp.models.schemas import Language


async def search_codelist(
    client: KoodistotClient,
    query: str,
    registry: str | None = None,
    max_results: int = 10,
) -> dict:
    """Search for code lists.

    Args:
        client: Koodistot API client.
        query: Search term for code list name or content.
        registry: Optional registry ID to limit search.
        max_results: Maximum results to return.

    Returns:
        Dictionary with search results.
    """
    schemes = await client.search_code_schemes(
        query=query,
        registry=registry,
        max_results=max_results,
    )

    results = []
    for scheme in schemes:
        results.append({
            "id": scheme.id,
            "registry": scheme.registry,
            "label": scheme.label.get(Language.FI),
            "description": scheme.description.get(Language.FI) if scheme.description else None,
            "uri": str(scheme.uri),
            "version": scheme.version,
            "code_count": scheme.code_count,
        })

    return {
        "query": query,
        "registry": registry,
        "result_count": len(results),
        "results": results,
    }


async def get_codes(
    client: KoodistotClient,
    registry: str,
    scheme: str,
    status: str = "VALID",
    max_results: int = 100,
) -> dict:
    """Get codes from a code list.

    Args:
        client: Koodistot API client.
        registry: Code registry ID.
        scheme: Code scheme ID.
        status: Filter by status (VALID, DRAFT, DEPRECATED).
        max_results: Maximum codes to return.

    Returns:
        Dictionary with code values.
    """
    # Get scheme info first
    code_scheme = await client.get_code_scheme(registry, scheme)
    if not code_scheme:
        return {
            "error": f"Code scheme not found: {registry}/{scheme}",
            "registry": registry,
            "scheme": scheme,
        }

    # Get codes
    codes = await client.get_codes(
        registry=registry,
        scheme=scheme,
        status=status,
        page_size=max_results,
    )

    # Build hierarchical structure if there are broader codes
    code_results = []
    for code in codes:
        code_results.append({
            "code": code.code,
            "label": code.label.get(Language.FI),
            "definition": code.definition.get(Language.FI) if code.definition else None,
            "uri": str(code.uri),
            "status": code.status.value,
            "broader_code": code.broader_code,
            "order": code.order,
        })

    # Sort by order if available, otherwise by code
    code_results.sort(key=lambda x: (x.get("order") or 999999, x.get("code", "")))

    return {
        "registry": registry,
        "scheme": scheme,
        "scheme_label": code_scheme.label.get(Language.FI),
        "scheme_description": code_scheme.description.get(Language.FI)
        if code_scheme.description
        else None,
        "status_filter": status,
        "code_count": len(code_results),
        "codes": code_results,
    }


async def export_codes_csv(
    client: KoodistotClient,
    registry: str,
    scheme: str,
    status: str = "VALID",
    include_header: bool = True,
) -> dict:
    """Export codes from a code list as CSV format.

    Args:
        client: Koodistot API client.
        registry: Code registry ID.
        scheme: Code scheme ID.
        status: Filter by status (VALID, DRAFT, DEPRECATED).
        include_header: Include CSV header row.

    Returns:
        Dictionary with CSV content and metadata.
    """
    # Get scheme info first
    code_scheme = await client.get_code_scheme(registry, scheme)
    if not code_scheme:
        return {
            "error": f"Code scheme not found: {registry}/{scheme}",
            "registry": registry,
            "scheme": scheme,
        }

    # Get all codes (increased limit for export)
    codes = await client.get_codes(
        registry=registry,
        scheme=scheme,
        status=status,
        page_size=1000,
    )

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    if include_header:
        writer.writerow([
            "CODEVALUE",
            "URI",
            "STATUS",
            "PREFLABEL_FI",
            "PREFLABEL_EN",
            "PREFLABEL_SV",
            "DEFINITION_FI",
            "BROADERCODE",
            "ORDER",
        ])

    for code in codes:
        writer.writerow([
            code.code,
            str(code.uri),
            code.status.value,
            code.label.fi or "",
            code.label.en or "",
            code.label.sv or "",
            code.definition.fi if code.definition else "",
            code.broader_code or "",
            code.order or "",
        ])

    csv_content = output.getvalue()
    output.close()

    return {
        "registry": registry,
        "scheme": scheme,
        "scheme_label": code_scheme.label.get(Language.FI),
        "format": "csv",
        "code_count": len(codes),
        "csv_content": csv_content,
    }
