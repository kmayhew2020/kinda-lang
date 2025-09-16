"""
Comprehensive tests for the ~maybe construct (60% execution probability).
Tests basic functionality, edge cases, and integration with other constructs.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import random

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime_helpers
from kinda.grammar.python.constructs import KindaPythonConstructs


class TestMaybeConstructParsing:
    """Test ~maybe construct parsing functionality"""

    def test_maybe_basic_syntax(self):
        """Test basic ~maybe syntax parsing"""
        line = "~maybe (x > 0) {"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "maybe"
        assert groups[0] == "x > 0"

    def test_maybe_empty_condition(self):
        """Test ~maybe with empty condition"""
        line = "~maybe () {"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "maybe"
        assert groups[0] == ""

    def test_maybe_no_condition(self):
        """Test ~maybe without parentheses (should not match)"""
        line = "~maybe {"
        construct_type, groups = match_python_construct(line)

        assert construct_type is None

    def test_maybe_complex_condition(self):
        """Test ~maybe with complex conditions"""
        test_cases = [
            "~maybe (x > 0 and y < 10)",
            "~maybe (func(a, b) == True)",
            "~maybe (len(items) > 0)",
            "~maybe (user.is_authenticated())",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "maybe", f"Failed for: {line}"
            assert groups is not None

    def test_maybe_whitespace_variations(self):
        """Test ~maybe with various whitespace patterns"""
        test_cases = [
            "~maybe(x > 0){",
            "~maybe (x > 0) {",
            "~maybe  (  x > 0  )  {",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "maybe", f"Failed for: {line}"

    def test_maybe_leading_whitespace(self):
        """Test ~maybe with leading whitespace (should not match - by design)"""
        line = "  ~maybe (x > 0) {"
        construct_type, groups = match_python_construct(line)

        # Leading whitespace should not match (consistent with ~sometimes behavior)
        assert construct_type is None


class TestMaybeTransformation:
    """Test ~maybe transformation functionality"""

    def test_maybe_line_transformation(self):
        """Test basic ~maybe line transformation"""
        line = "~maybe (x > 0) {"
        result = transform_line(line)

        assert len(result) == 1
        assert "if maybe(x > 0):" in result[0]

    def test_maybe_empty_condition_transformation(self):
        """Test ~maybe with empty condition transformation"""
        line = "~maybe () {"
        result = transform_line(line)

        assert len(result) == 1
        assert "if maybe():" in result[0]

    def test_maybe_preserves_indentation(self):
        """Test ~maybe preserves original indentation"""
        line = "    ~maybe (condition) {"
        result = transform_line(line)

        assert len(result) == 1
        assert result[0].startswith("    ")
        assert "if maybe(condition):" in result[0]


class TestMaybeFileTransformation:
    """Test file-level ~maybe transformation"""

    def test_maybe_block_transformation(self):
        """Test ~maybe block transformation with indented content"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int x = 5
~maybe (x > 0) {
    ~sorta print("x is positive")
    x ~= 10
}
print("done")
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should include import for maybe and other used helpers
            assert "from kinda.langs.python.runtime.fuzzy import" in result
            assert "maybe" in result

            # Should transform the block correctly
            assert "if maybe(x > 0):" in result
            assert "    sorta_print(" in result
            assert "    x = fuzzy_assign(" in result

            # Should preserve non-kinda code
            assert 'print("done")' in result

        finally:
            temp_path.unlink()

    def test_maybe_nested_constructs(self):
        """Test ~maybe with nested kinda constructs"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~maybe (True) {
    ~kinda int nested_var = 42
    ~sometimes (nested_var > 0) {
        ~sorta print("nested execution")
    }
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle nested constructs
            assert "if maybe(True):" in result
            assert "    nested_var = kinda_int(42)" in result
            assert "    if sometimes(nested_var > 0):" in result
            assert "        sorta_print(" in result

        finally:
            temp_path.unlink()

    def test_maybe_multiple_blocks(self):
        """Test multiple ~maybe blocks in same file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~maybe (condition1) {
    ~sorta print("first block")
}

~maybe (condition2) {
    ~sorta print("second block")
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle multiple blocks
            assert "if maybe(condition1):" in result
            assert "if maybe(condition2):" in result
            assert result.count("maybe") >= 2

        finally:
            temp_path.unlink()


class TestMaybeRuntimeBehavior:
    """Test ~maybe runtime behavior and probability"""

    @patch("kinda.personality.chaos_random")
    @patch("kinda.personality.chaos_probability")
    def test_maybe_probability_execution(self, mock_chaos_prob, mock_random):
        """Test ~maybe executes with 60% probability"""
        # Test execution when random < probability threshold
        mock_random.return_value = 0.5  # Should execute
        mock_chaos_prob.return_value = 0.6  # Probability threshold

        # Generate complete runtime to get the maybe function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"maybe"}, temp_path, KindaPythonConstructs)

            # Import the generated maybe function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import maybe  # type: ignore[import-not-found]

                result = maybe(True)
                assert (
                    result == True
                )  # Should execute when condition is True and random < probability
            finally:
                sys.path.remove(str(temp_path))

    @patch("kinda.personality.chaos_random")
    @patch("kinda.personality.chaos_probability")
    def test_maybe_probability_no_execution(self, mock_chaos_prob, mock_random):
        """Test ~maybe doesn't execute when probability fails"""
        # Test no execution when random >= probability threshold
        mock_random.return_value = 0.7  # Should not execute
        mock_chaos_prob.return_value = 0.6  # Probability threshold

        # Generate complete runtime to get the maybe function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"maybe"}, temp_path, KindaPythonConstructs)

            # Import the generated maybe function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import maybe  # type: ignore[import-not-found]

                result = maybe(True)
                assert result == False  # Should not execute when random >= 0.6
            finally:
                sys.path.remove(str(temp_path))

    @patch("kinda.personality.chaos_random")
    @patch("kinda.personality.chaos_probability")
    def test_maybe_condition_false(self, mock_chaos_prob, mock_random):
        """Test ~maybe doesn't execute when condition is False"""
        mock_random.return_value = 0.3  # Would normally execute
        mock_chaos_prob.return_value = 0.6  # Probability threshold

        # Generate complete runtime to get the maybe function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"maybe"}, temp_path, KindaPythonConstructs)

            # Import the generated maybe function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import maybe  # type: ignore[import-not-found]

                result = maybe(False)  # False condition
                assert result == False  # Should not execute when condition is False
            finally:
                sys.path.remove(str(temp_path))


class TestMaybeEdgeCases:
    """Test ~maybe edge cases and error handling"""

    def test_maybe_invalid_syntax(self):
        """Test ~maybe with invalid syntax falls back gracefully"""
        invalid_lines = [
            "~maybe",  # Incomplete
            "~maybe {",  # Missing parentheses
            "~maybe (unclosed",  # Unclosed parentheses
        ]

        for line in invalid_lines:
            result = transform_line(line)
            # Should return original line if can't transform
            assert result == [line]

    def test_maybe_with_comments(self):
        """Test ~maybe with comments in the block"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~maybe (True) {
    # This is a comment
    ~sorta print("with comment")
    # Another comment
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should preserve comments
            assert "# This is a comment" in result
            assert "# Another comment" in result
            assert "if maybe(True):" in result

        finally:
            temp_path.unlink()

    def test_maybe_empty_block(self):
        """Test ~maybe with empty block"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~maybe (True) {
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle empty blocks gracefully
            assert "if maybe(True):" in result

        finally:
            temp_path.unlink()


class TestMaybeIntegration:
    """Test ~maybe integration with other constructs"""

    def test_maybe_with_all_constructs(self):
        """Test ~maybe works alongside all other kinda constructs"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int base_val = 10
base_val ~= 5

~maybe (base_val > 0) {
    ~sorta print("Maybe executing")
    ~sometimes (True) {
        ~kinda int inner_val = 20
        inner_val ~= 3
        ~sorta print("Sometimes in maybe")
    }
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should include all necessary imports
            import_line = [
                line
                for line in result.split("\n")
                if line.startswith("from kinda.langs.python.runtime.fuzzy import")
            ][0]
            assert "maybe" in import_line
            assert "sometimes" in import_line
            assert "kinda_int" in import_line
            assert "sorta_print" in import_line
            assert "fuzzy_assign" in import_line

            # Should transform all constructs correctly
            assert "base_val = kinda_int(10)" in result
            assert "base_val = fuzzy_assign(" in result
            assert "if maybe(base_val > 0):" in result
            assert "if sometimes(True):" in result

        finally:
            temp_path.unlink()

    def test_maybe_probability_difference_from_sometimes(self):
        """Test that ~maybe has different probability behavior than ~sometimes with personality system"""
        # This test verifies that both constructs use personality system but with different keys
        maybe_construct = KindaPythonConstructs["maybe"]
        sometimes_construct = KindaPythonConstructs["sometimes"]

        # Extract function bodies
        maybe_body = maybe_construct["body"]
        sometimes_body = sometimes_construct["body"]

        # Both should use personality system
        assert "chaos_probability" in maybe_body
        assert "chaos_probability" in sometimes_body

        # ~maybe should call chaos_probability with 'maybe' key
        assert "chaos_probability('maybe'" in maybe_body

        # ~sometimes should call chaos_probability with 'sometimes' key
        assert "chaos_probability('sometimes'" in sometimes_body

        # They should be different constructs
        assert maybe_body != sometimes_body
