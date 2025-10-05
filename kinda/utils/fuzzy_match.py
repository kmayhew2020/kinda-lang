"""
Fuzzy string matching utilities for error messages and suggestions.

Provides Levenshtein distance calculation and "Did you mean?" suggestions
for typos in construct names and other identifiers.
"""

from typing import List, Tuple, Optional


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein (edit) distance between two strings.

    Uses dynamic programming with O(m*n) time and O(min(m,n)) space.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Minimum number of single-character edits (insertions, deletions,
        substitutions) needed to transform s1 into s2

    Examples:
        >>> levenshtein_distance("sometimes", "sometymes")
        1
        >>> levenshtein_distance("kinda", "kind")
        1
        >>> levenshtein_distance("", "hello")
        5
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    # Use rolling array to save space
    previous_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_closest_matches(
    target: str,
    candidates: List[str],
    max_distance: int = 3,
    max_results: int = 3,
) -> List[Tuple[str, int]]:
    """
    Find closest matching strings using Levenshtein distance.

    Args:
        target: String to match
        candidates: List of valid strings to match against
        max_distance: Maximum edit distance to consider (default 3)
        max_results: Maximum number of results to return

    Returns:
        List of (match, distance) tuples, sorted by distance (closest first)

    Examples:
        >>> candidates = ["sometimes", "maybe", "probably", "rarely"]
        >>> find_closest_matches("sometymes", candidates)
        [('sometimes', 1)]
        >>> find_closest_matches("probbly", candidates)
        [('probably', 1)]
    """
    matches = []

    for candidate in candidates:
        distance = levenshtein_distance(target.lower(), candidate.lower())
        if distance <= max_distance:
            matches.append((candidate, distance))

    # Sort by distance (ascending), then alphabetically
    matches.sort(key=lambda x: (x[1], x[0]))

    return matches[:max_results]


def format_did_you_mean(matches: List[Tuple[str, int]], add_tilde: bool = True) -> str:
    """
    Format "Did you mean?" suggestion from matches.

    Args:
        matches: List of (match, distance) tuples
        add_tilde: If True, prefix construct names with ~ (default True)

    Returns:
        Formatted suggestion string

    Examples:
        >>> format_did_you_mean([("sometimes", 1)])
        '~sometimes'

        >>> format_did_you_mean([("sometimes", 1), ("maybe", 2)])
        '~sometimes or ~maybe'

        >>> format_did_you_mean([("sometimes", 1), ("maybe", 2), ("probably", 3)])
        '~sometimes, ~maybe, or ~probably'

        >>> format_did_you_mean([("print", 1)], add_tilde=False)
        'print'
    """
    if not matches:
        return "no close matches found"

    # Add tilde prefix to construct names if requested
    if add_tilde:
        formatted = [f"~{match[0]}" for match in matches]
    else:
        formatted = [match[0] for match in matches]

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} or {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + f", or {formatted[-1]}"
