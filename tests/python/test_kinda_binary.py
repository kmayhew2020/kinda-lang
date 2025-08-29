"""
Comprehensive tests for ~kinda binary three-state construct.
Tests default and custom probabilities, transformation, and runtime behavior.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.transformer import transform_line, transform_file


class TestKindaBinaryParsing:
    """Test ~kinda binary parsing and pattern matching"""

    def test_basic_kinda_binary_parsing(self):
        """Test basic ~kinda binary syntax parsing"""
        line = "~kinda binary decision"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "kinda_binary"
        assert groups[0] == "decision"
        assert groups[1] is None  # No custom probabilities

    def test_kinda_binary_with_custom_probabilities(self):
        """Test ~kinda binary with custom probability syntax"""
        line = "~kinda binary choice ~ probabilities(0.5, 0.3, 0.2)"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "kinda_binary"
        assert groups[0] == "choice"
        assert groups[1] == "0.5, 0.3, 0.2"

    def test_kinda_binary_with_semicolon(self):
        """Test ~kinda binary with semicolon terminator"""
        line = "~kinda binary vote;"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "kinda_binary"
        assert groups[0] == "vote"

    def test_invalid_kinda_binary_syntax(self):
        """Test that invalid syntax doesn't match"""
        invalid_lines = [
            "~kinda binary",  # Missing variable name
            "kinda binary test",  # Missing tilde
            "~kinda int binary",  # Wrong construct
        ]

        for line in invalid_lines:
            construct_type, groups = match_python_construct(line)
            assert construct_type != "kinda_binary", f"Should not match: {line}"


class TestKindaBinaryTransformation:
    """Test transformation of ~kinda binary to Python code"""

    def test_transform_basic_kinda_binary(self):
        """Test transformation with default probabilities"""
        line = "~kinda binary decision"
        result = transform_line(line)

        assert len(result) == 1
        assert result[0] == "decision = kinda_binary()"

    def test_transform_kinda_binary_with_custom_probs(self):
        """Test transformation with custom probabilities"""
        line = "~kinda binary choice ~ probabilities(0.5, 0.3, 0.2)"
        result = transform_line(line)

        assert len(result) == 1
        assert result[0] == "choice = kinda_binary(0.5, 0.3, 0.2)"

    def test_transform_multiple_kinda_binary(self):
        """Test file with multiple ~kinda binary declarations"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda binary first_choice
~kinda binary second_choice ~ probabilities(0.6, 0.3, 0.1)
~sorta print("Choices made:", first_choice, second_choice)
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            assert "from kinda.langs.python.runtime.fuzzy import" in result
            assert "kinda_binary" in result
            assert "first_choice = kinda_binary()" in result
            assert "second_choice = kinda_binary(0.6, 0.3, 0.1)" in result
            assert "sorta_print" in result

        finally:
            temp_path.unlink()


class TestKindaBinaryRuntime:
    """Test runtime behavior of kinda_binary function"""

    def test_kinda_binary_returns_valid_values(self):
        """Test that kinda_binary returns only 1, -1, or 0"""
        # Import the runtime generation to get the function definition
        from kinda.grammar.python.constructs import KindaPythonConstructs

        # Extract the function body and execute it
        func_body = KindaPythonConstructs["kinda_binary"]["body"]

        # Create a namespace with random module
        import random

        namespace = {"random": random}

        # Execute the function definition
        exec(func_body, namespace)
        kinda_binary = namespace["kinda_binary"]

        # Test multiple times to ensure valid values
        for _ in range(100):
            result = kinda_binary()
            assert result in [1, -1, 0], f"Invalid result: {result}"

    def test_kinda_binary_distribution(self):
        """Test that distribution roughly matches specified probabilities"""
        from kinda.grammar.python.constructs import KindaPythonConstructs

        func_body = KindaPythonConstructs["kinda_binary"]["body"]

        import random

        namespace = {"random": random}
        exec(func_body, namespace)
        kinda_binary = namespace["kinda_binary"]

        # Test with custom probabilities
        results = {"positive": 0, "negative": 0, "neutral": 0}
        iterations = 1000

        for _ in range(iterations):
            result = kinda_binary(pos_prob=0.5, neg_prob=0.3, neutral_prob=0.2)
            if result == 1:
                results["positive"] += 1
            elif result == -1:
                results["negative"] += 1
            else:
                results["neutral"] += 1

        # Check distribution is roughly correct (with 10% tolerance)
        assert abs(results["positive"] / iterations - 0.5) < 0.1
        assert abs(results["negative"] / iterations - 0.3) < 0.1
        assert abs(results["neutral"] / iterations - 0.2) < 0.1


class TestKindaBinaryIntegration:
    """Test integration with other kinda constructs"""

    def test_kinda_binary_with_conditionals(self):
        """Test ~kinda binary used with ~sometimes and ~maybe"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda binary mood
~sometimes (mood == 1) {
    ~sorta print("Feeling positive!")
}
~maybe (mood == -1) {
    ~sorta print("Feeling negative...")
}
~sorta print("Mood value:", mood)
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Check all constructs are transformed
            assert "mood = kinda_binary()" in result
            assert "if sometimes(mood == 1):" in result
            assert "if maybe(mood == -1):" in result
            assert 'sorta_print("Mood value:", mood)' in result

            # Check imports
            assert "kinda_binary" in result
            assert "sometimes" in result
            assert "maybe" in result

        finally:
            temp_path.unlink()

    def test_kinda_binary_with_fuzzy_reassignment(self):
        """Test ~kinda binary with fuzzy reassignment"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda binary state
state ~= state + 1
~sorta print("Fuzzy state:", state)
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            assert "state = kinda_binary()" in result
            assert "state = fuzzy_assign" in result and "state + 1)" in result
            assert "sorta_print" in result and "Fuzzy state:" in result

        finally:
            temp_path.unlink()


class TestKindaBinaryEdgeCases:
    """Test edge cases and error handling"""

    def test_variable_names_with_underscores(self):
        """Test variable names with underscores"""
        line = "~kinda binary user_decision_value"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "kinda_binary"
        assert groups[0] == "user_decision_value"

    def test_whitespace_variations(self):
        """Test various whitespace patterns"""
        test_cases = [
            "~kinda  binary  decision",  # Multiple spaces
            "   ~kinda binary decision",  # Leading whitespace
            "~kinda binary decision   ",  # Trailing whitespace
        ]

        for line in test_cases:
            result = transform_line(line)
            assert len(result) == 1
            assert "decision = kinda_binary()" in result[0]

    def test_probability_edge_values(self):
        """Test edge probability values"""
        test_cases = [
            "~kinda binary certain ~ probabilities(1.0, 0.0, 0.0)",  # Always positive
            "~kinda binary negative ~ probabilities(0.0, 1.0, 0.0)",  # Always negative
            "~kinda binary neutral ~ probabilities(0.0, 0.0, 1.0)",  # Always neutral
        ]

        for line in test_cases:
            result = transform_line(line)
            assert len(result) == 1
            assert "kinda_binary(" in result[0]
