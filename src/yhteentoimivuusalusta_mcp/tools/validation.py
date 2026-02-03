"""Text validation tools for terminology checking."""

import re
from typing import Any

from yhteentoimivuusalusta_mcp.clients.sanastot import SanastotClient
from yhteentoimivuusalusta_mcp.models.schemas import Concept, Language
from yhteentoimivuusalusta_mcp.utils.fuzzy import fuzzy_match, similarity_score


# Common Finnish stop words to ignore during validation
FINNISH_STOP_WORDS = {
    "ja", "on", "ei", "että", "se", "joka", "kun", "niin", "kuin", "tai",
    "mutta", "jos", "ovat", "ole", "oli", "olla", "sen", "hän", "he",
    "tämä", "tuo", "nämä", "ne", "me", "te", "minä", "sinä", "mikä",
    "mitä", "missä", "jossa", "jonka", "joita", "myös", "vain", "sekä",
    "sitten", "vielä", "kuitenkin", "jo", "nyt", "aina", "voi", "sitä",
    "niitä", "hänen", "heidän", "meidän", "teidän", "minun", "sinun",
    "ovat", "olisi", "voisi", "pitää", "täytyy", "mukaan", "kanssa",
    "ilman", "ennen", "jälkeen", "välillä", "kautta", "kohti", "yli",
    "alle", "sisällä", "ulkona", "edessä", "takana", "vieressä",
}


def tokenize_finnish(text: str) -> list[str]:
    """Extract potential terms from Finnish text.

    Args:
        text: Input text to tokenize.

    Returns:
        List of potential term tokens.
    """
    # Remove common punctuation but keep hyphenated words
    text = re.sub(r'[^\w\s\-äöåÄÖÅ]', ' ', text)

    # Split into words
    words = text.lower().split()

    # Filter out stop words and very short words
    tokens = []
    for word in words:
        word = word.strip('-')
        if len(word) >= 3 and word not in FINNISH_STOP_WORDS:
            tokens.append(word)

    # Also extract compound terms (2-3 word combinations)
    compound_terms = []
    for i in range(len(words) - 1):
        w1 = words[i].strip('-')
        w2 = words[i + 1].strip('-')
        if w1 not in FINNISH_STOP_WORDS and w2 not in FINNISH_STOP_WORDS:
            if len(w1) >= 2 and len(w2) >= 2:
                compound_terms.append(f"{w1} {w2}")

    return tokens + compound_terms


async def validate_terminology(
    client: SanastotClient,
    text: str,
    vocabularies: list[str] | None = None,
    suggest_corrections: bool = True,
    fuzzy_threshold: float = 0.8,
) -> dict[str, Any]:
    """Validate terminology usage in text against standards.

    Args:
        client: Sanastot API client.
        text: Text to validate (max 10000 characters).
        vocabularies: Vocabulary IDs to check against (default: all).
        suggest_corrections: Whether to suggest corrections for non-standard terms.
        fuzzy_threshold: Similarity threshold for fuzzy matching (0.0-1.0).

    Returns:
        Dictionary with validation results.
    """
    # Limit text length
    if len(text) > 10000:
        text = text[:10000]

    # Extract terms from text
    tokens = tokenize_finnish(text)
    unique_tokens = list(set(tokens))

    # Track results
    validated_terms: list[dict] = []
    suggestions: list[dict] = []
    unknown_terms: list[str] = []

    # Build a cache of concepts from the API
    concept_cache: dict[str, Concept] = {}

    # Search for each unique token
    for token in unique_tokens[:50]:  # Limit to prevent too many API calls
        # Search in specified vocabularies or all
        if vocabularies:
            for vocab_id in vocabularies:
                concepts = await client.search_concepts(
                    query=token,
                    vocabulary_id=vocab_id,
                    max_results=5,
                )
                for c in concepts:
                    concept_cache[c.id] = c
        else:
            concepts = await client.search_concepts(
                query=token,
                max_results=5,
            )
            for c in concepts:
                concept_cache[c.id] = c

    # Now validate each token against found concepts
    concept_labels = []
    for concept in concept_cache.values():
        if concept.preferred_label.fi:
            concept_labels.append(concept.preferred_label.fi.lower())
        for term in concept.terms:
            concept_labels.append(term.label.lower())

    for token in unique_tokens:
        token_lower = token.lower()

        # Check for exact match
        exact_match = None
        for concept in concept_cache.values():
            label_fi = (concept.preferred_label.fi or "").lower()
            if token_lower == label_fi:
                exact_match = concept
                break
            for term in concept.terms:
                if token_lower == term.label.lower():
                    exact_match = concept
                    break
            if exact_match:
                break

        if exact_match:
            validated_terms.append({
                "term": token,
                "status": "valid",
                "concept_id": exact_match.id,
                "vocabulary_id": exact_match.vocabulary_id,
                "preferred_label": exact_match.preferred_label.fi,
                "definition": exact_match.definition.fi if exact_match.definition else None,
            })
        elif suggest_corrections and concept_labels:
            # Try fuzzy matching
            matches = fuzzy_match(
                token_lower,
                concept_labels,
                threshold=fuzzy_threshold,
                limit=3,
            )

            if matches:
                # Find the concept for the best match
                best_match_label = matches[0][0]
                best_score = matches[0][1]
                best_concept = None

                for concept in concept_cache.values():
                    if (concept.preferred_label.fi or "").lower() == best_match_label:
                        best_concept = concept
                        break
                    for term in concept.terms:
                        if term.label.lower() == best_match_label:
                            best_concept = concept
                            break
                    if best_concept:
                        break

                if best_concept:
                    suggestions.append({
                        "term": token,
                        "status": "suggestion",
                        "similarity": round(best_score, 2),
                        "suggested_term": best_concept.preferred_label.fi,
                        "concept_id": best_concept.id,
                        "vocabulary_id": best_concept.vocabulary_id,
                        "alternatives": [m[0] for m in matches[1:3]],
                    })
                else:
                    unknown_terms.append(token)
            else:
                unknown_terms.append(token)
        else:
            unknown_terms.append(token)

    return {
        "text_length": len(text),
        "tokens_analyzed": len(unique_tokens),
        "vocabularies_checked": vocabularies or ["all"],
        "summary": {
            "valid_terms": len(validated_terms),
            "suggestions": len(suggestions),
            "unknown_terms": len(unknown_terms),
        },
        "validated_terms": validated_terms,
        "suggestions": suggestions if suggest_corrections else [],
        "unknown_terms": unknown_terms[:20],  # Limit output
    }
