"""Fuzzy matching utilities for improved search."""

from typing import TypeVar

T = TypeVar("T")

# Try to import rapidfuzz, fall back to simple matching if not available
try:
    from rapidfuzz import fuzz, process

    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


def fuzzy_match(
    query: str,
    candidates: list[str],
    threshold: float = 0.8,
    limit: int = 10,
) -> list[tuple[str, float]]:
    """Find fuzzy matches for a query string.

    Args:
        query: The search query.
        candidates: List of candidate strings to match against.
        threshold: Minimum similarity score (0.0-1.0).
        limit: Maximum number of results.

    Returns:
        List of (candidate, score) tuples sorted by score.
    """
    if not candidates:
        return []

    if RAPIDFUZZ_AVAILABLE:
        # Use rapidfuzz for efficient fuzzy matching
        results = process.extract(
            query,
            candidates,
            scorer=fuzz.WRatio,
            limit=limit,
            score_cutoff=threshold * 100,
        )
        # Convert scores from 0-100 to 0-1
        return [(match, score / 100) for match, score, _ in results]
    else:
        # Fallback to simple substring matching
        return _simple_match(query, candidates, threshold, limit)


def fuzzy_match_items(
    query: str,
    items: list[T],
    key_func: callable,
    threshold: float = 0.8,
    limit: int = 10,
) -> list[tuple[T, float]]:
    """Find fuzzy matches for items using a key function.

    Args:
        query: The search query.
        items: List of items to match against.
        key_func: Function to extract string key from item.
        threshold: Minimum similarity score (0.0-1.0).
        limit: Maximum number of results.

    Returns:
        List of (item, score) tuples sorted by score.
    """
    if not items:
        return []

    # Create mapping from key to items (handle duplicates)
    key_to_items: dict[str, list[T]] = {}
    for item in items:
        key = key_func(item)
        if key:
            if key not in key_to_items:
                key_to_items[key] = []
            key_to_items[key].append(item)

    # Get fuzzy matches on keys
    candidates = list(key_to_items.keys())
    matches = fuzzy_match(query, candidates, threshold, limit)

    # Map back to items
    results = []
    for key, score in matches:
        for item in key_to_items[key]:
            results.append((item, score))
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    return results


def _simple_match(
    query: str,
    candidates: list[str],
    threshold: float,
    limit: int,
) -> list[tuple[str, float]]:
    """Simple substring matching fallback.

    Args:
        query: The search query.
        candidates: List of candidates.
        threshold: Minimum similarity (ignored in simple mode).
        limit: Maximum results.

    Returns:
        List of (candidate, score) tuples.
    """
    query_lower = query.lower()
    results = []

    for candidate in candidates:
        candidate_lower = candidate.lower()

        # Exact match
        if query_lower == candidate_lower:
            results.append((candidate, 1.0))
        # Starts with query
        elif candidate_lower.startswith(query_lower):
            results.append((candidate, 0.9))
        # Contains query
        elif query_lower in candidate_lower:
            results.append((candidate, 0.7))
        # Query contains candidate (partial)
        elif candidate_lower in query_lower:
            results.append((candidate, 0.6))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


def similarity_score(s1: str, s2: str) -> float:
    """Calculate similarity score between two strings.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if not s1 or not s2:
        return 0.0

    if s1 == s2:
        return 1.0

    if RAPIDFUZZ_AVAILABLE:
        return fuzz.WRatio(s1, s2) / 100
    else:
        # Simple fallback
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0
        if s1_lower in s2_lower or s2_lower in s1_lower:
            shorter = min(len(s1), len(s2))
            longer = max(len(s1), len(s2))
            return shorter / longer
        return 0.0
