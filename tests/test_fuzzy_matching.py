"""
Test suite for fuzzy string matching utilities (Issue #113).

Tests Levenshtein distance calculation and "Did you mean?" suggestions
for construct name typos.
"""

import pytest
from kinda.utils.fuzzy_match import (
    levenshtein_distance,
    find_closest_matches,
    format_did_you_mean,
)


class TestLevenshteinDistance:
    """Test Levenshtein distance algorithm."""

    def test_identical_strings(self):
        """Identical strings have distance 0."""
        assert levenshtein_distance("hello", "hello") == 0
        assert levenshtein_distance("", "") == 0

    def test_single_insertion(self):
        """Single character insertion."""
        assert levenshtein_distance("hello", "hellos") == 1
        assert levenshtein_distance("cat", "cats") == 1

    def test_single_deletion(self):
        """Single character deletion."""
        assert levenshtein_distance("hello", "helo") == 1
        assert levenshtein_distance("world", "wold") == 1

    def test_single_substitution(self):
        """Single character substitution."""
        assert levenshtein_distance("hello", "hallo") == 1
        assert levenshtein_distance("cat", "bat") == 1

    def test_multiple_operations(self):
        """Multiple edits required."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3

    def test_empty_string(self):
        """Distance to empty string equals string length."""
        assert levenshtein_distance("", "hello") == 5
        assert levenshtein_distance("world", "") == 5

    def test_case_insensitive(self):
        """Algorithm is case-insensitive (handled by caller)."""
        # Note: Case sensitivity is handled in find_closest_matches
        assert levenshtein_distance("hello", "HELLO") == 5
        assert levenshtein_distance("hello".lower(), "HELLO".lower()) == 0

    def test_construct_typos(self):
        """Common construct typos."""
        assert levenshtein_distance("sometymes", "sometimes") == 1
        assert levenshtein_distance("probbly", "probably") == 1
        assert levenshtein_distance("mabye", "maybe") == 2  # Delete 'b', move 'b'
        assert levenshtein_distance("rarly", "rarely") == 1


class TestFindClosestMatches:
    """Test finding closest matching strings."""

    def setup_method(self):
        """Setup candidate construct names."""
        self.constructs = [
            "sometimes",
            "maybe",
            "probably",
            "rarely",
            "kinda_int",
            "kinda_float",
            "kinda_bool",
        ]

    def test_exact_match(self):
        """Exact match has distance 0."""
        matches = find_closest_matches("sometimes", self.constructs)
        assert len(matches) == 1
        assert matches[0] == ("sometimes", 0)

    def test_single_typo(self):
        """Single character typo finds correct match."""
        matches = find_closest_matches("sometymes", self.constructs)
        assert len(matches) >= 1
        assert matches[0] == ("sometimes", 1)

    def test_multiple_typos(self):
        """Multiple typos find closest match."""
        matches = find_closest_matches("probbly", self.constructs)
        assert len(matches) >= 1
        assert matches[0] == ("probably", 1)

    def test_max_distance_filter(self):
        """Max distance filters out distant matches."""
        # "xyz" is very different from all constructs
        matches = find_closest_matches("xyz", self.constructs, max_distance=1)
        assert len(matches) == 0  # No matches within distance 1

        matches = find_closest_matches("xyz", self.constructs, max_distance=10)
        assert len(matches) > 0  # Some matches within distance 10

    def test_max_results_limit(self):
        """Max results limits number of suggestions."""
        matches = find_closest_matches("kinda", self.constructs, max_results=2)
        assert len(matches) <= 2

        matches = find_closest_matches("kinda", self.constructs, max_results=5)
        assert len(matches) <= 5

    def test_case_insensitive_matching(self):
        """Matching is case-insensitive."""
        matches = find_closest_matches("SOMETIMES", self.constructs)
        assert len(matches) >= 1
        assert matches[0][0] == "sometimes"

    def test_sorted_by_distance(self):
        """Results sorted by distance (closest first)."""
        matches = find_closest_matches("mayb", self.constructs, max_results=3)
        # Check that distances are non-decreasing
        distances = [m[1] for m in matches]
        assert distances == sorted(distances)

    def test_no_matches(self):
        """No matches within distance threshold."""
        matches = find_closest_matches("completely_different", self.constructs, max_distance=2)
        assert len(matches) == 0


class TestFormatDidYouMean:
    """Test "Did you mean?" formatting."""

    def test_single_match(self):
        """Single match formatted correctly."""
        matches = [("sometimes", 1)]
        result = format_did_you_mean(matches)
        assert result == "~sometimes"

    def test_two_matches(self):
        """Two matches use 'or'."""
        matches = [("sometimes", 1), ("maybe", 2)]
        result = format_did_you_mean(matches)
        assert result == "~sometimes or ~maybe"

    def test_three_matches(self):
        """Three matches use comma and 'or'."""
        matches = [("sometimes", 1), ("maybe", 2), ("probably", 3)]
        result = format_did_you_mean(matches)
        assert result == "~sometimes, ~maybe, or ~probably"

    def test_no_matches(self):
        """No matches return helpful message."""
        matches = []
        result = format_did_you_mean(matches)
        assert result == "no close matches found"

    def test_without_tilde_prefix(self):
        """Can disable tilde prefix."""
        matches = [("print", 1)]
        result = format_did_you_mean(matches, add_tilde=False)
        assert result == "print"

    def test_preserves_order(self):
        """Preserves match order (should be sorted by caller)."""
        matches = [("sometimes", 1), ("maybe", 2), ("rarely", 3)]
        result = format_did_you_mean(matches)
        assert "~sometimes" in result
        assert result.index("~sometimes") < result.index("~maybe")
        assert result.index("~maybe") < result.index("~rarely")


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_typo_suggestion_pipeline(self):
        """Full pipeline: typo -> matches -> formatted suggestion."""
        constructs = ["sometimes", "maybe", "probably", "rarely"]

        # Typo: "sometymes" -> "sometimes"
        matches = find_closest_matches("sometymes", constructs)
        suggestion = format_did_you_mean(matches)
        assert "~sometimes" in suggestion

        # Typo: "probbly" -> "probably"
        matches = find_closest_matches("probbly", constructs)
        suggestion = format_did_you_mean(matches)
        assert "~probably" in suggestion

    def test_multiple_similar_matches(self):
        """Multiple constructs with similar distances."""
        constructs = ["kinda_int", "kinda_float", "kinda_bool"]

        # "kinda_" prefix matches all, but distances vary
        matches = find_closest_matches("kinda_", constructs, max_results=3)
        assert len(matches) >= 1

        # All should have "kinda_" prefix
        for match, _ in matches:
            assert match.startswith("kinda_")

    def test_edge_case_very_short_typo(self):
        """Very short input finds longer matches."""
        constructs = ["sometimes", "maybe", "probably"]

        matches = find_closest_matches("ma", constructs, max_distance=3)
        # "maybe" is closest (3 insertions)
        if matches:
            assert matches[0][0] == "maybe"
