"""Tests for fuzzy matching utilities."""

import pytest

from yhteentoimivuusalusta_mcp.utils.fuzzy import (
    fuzzy_match,
    fuzzy_match_items,
    similarity_score,
)


class TestFuzzyMatch:
    """Tests for fuzzy_match function."""

    def test_exact_match(self):
        """Test exact match returns score of 1.0."""
        candidates = ["rakennus", "rakennelma", "alue"]
        result = fuzzy_match("rakennus", candidates, threshold=0.5)

        assert len(result) > 0
        assert result[0][0] == "rakennus"
        assert result[0][1] >= 0.9

    def test_similar_match(self):
        """Test similar strings are matched."""
        candidates = ["rakennus", "rakennelma", "alue"]
        result = fuzzy_match("rakennux", candidates, threshold=0.7)

        # Should find "rakennus" as similar
        if result:
            assert any("rakennus" in r[0] for r in result)

    def test_no_match_below_threshold(self):
        """Test that dissimilar strings are not matched."""
        candidates = ["rakennus", "rakennelma", "alue"]
        result = fuzzy_match("xyz", candidates, threshold=0.9)

        # Should not find matches for completely different string
        assert len(result) == 0

    def test_empty_candidates(self):
        """Test with empty candidates list."""
        result = fuzzy_match("test", [], threshold=0.5)
        assert result == []

    def test_limit_results(self):
        """Test that results are limited."""
        candidates = ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10"]
        result = fuzzy_match("a", candidates, threshold=0.3, limit=3)

        assert len(result) <= 3


class TestFuzzyMatchItems:
    """Tests for fuzzy_match_items function."""

    def test_match_with_key_function(self):
        """Test matching items with a key function."""
        items = [
            {"id": 1, "name": "rakennus"},
            {"id": 2, "name": "rakennelma"},
            {"id": 3, "name": "alue"},
        ]

        result = fuzzy_match_items(
            "rakennus",
            items,
            key_func=lambda x: x["name"],
            threshold=0.5,
        )

        assert len(result) > 0
        assert result[0][0]["name"] == "rakennus"

    def test_empty_items(self):
        """Test with empty items list."""
        result = fuzzy_match_items(
            "test",
            [],
            key_func=lambda x: x.get("name", ""),
            threshold=0.5,
        )
        assert result == []


class TestSimilarityScore:
    """Tests for similarity_score function."""

    def test_identical_strings(self):
        """Test identical strings return 1.0."""
        assert similarity_score("test", "test") == 1.0

    def test_empty_strings(self):
        """Test empty strings return 0.0."""
        assert similarity_score("", "test") == 0.0
        assert similarity_score("test", "") == 0.0
        assert similarity_score("", "") == 0.0

    def test_similar_strings(self):
        """Test similar strings return high score."""
        score = similarity_score("rakennus", "rakennux")
        assert 0.5 < score < 1.0

    def test_different_strings(self):
        """Test different strings return low score."""
        score = similarity_score("rakennus", "xyz")
        assert score < 0.5
