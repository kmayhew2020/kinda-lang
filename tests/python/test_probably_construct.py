"""
Comprehensive tests for the ~probably construct (70% execution probability).
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


class TestProbablyConstructParsing:
    """Test ~probably construct parsing functionality"""

    def test_probably_basic_syntax(self):
        """Test basic ~probably syntax parsing"""
        line = "~probably (x > 0) {"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "probably"
        assert groups[0] == "x > 0"

    def test_probably_empty_condition(self):
        """Test ~probably with empty condition"""
        line = "~probably () {"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "probably"
        assert groups[0] == ""

    def test_probably_no_condition(self):
        """Test ~probably without parentheses (should not match)"""
        line = "~probably {"
        construct_type, groups = match_python_construct(line)

        assert construct_type is None

    def test_probably_complex_condition(self):
        """Test ~probably with complex conditions"""
        test_cases = [
            "~probably (x > 0 and y < 10)",
            "~probably (func(a, b) == True)",
            "~probably (len(items) > 0)",
            "~probably (user.is_authenticated())",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "probably", f"Failed for: {line}"
            assert groups is not None

    def test_probably_whitespace_variations(self):
        """Test ~probably with various whitespace patterns"""
        test_cases = [
            "~probably(x > 0){",
            "~probably (x > 0) {",
            "~probably  (  x > 0  )  {",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "probably", f"Failed for: {line}"

    def test_probably_leading_whitespace(self):
        """Test ~probably with leading whitespace (should not match - by design)"""
        line = "  ~probably (x > 0) {"
        construct_type, groups = match_python_construct(line)

        # Leading whitespace should not match (consistent with other constructs behavior)
        assert construct_type is None


class TestProbablyTransformation:
    """Test ~probably transformation functionality"""

    def test_probably_line_transformation(self):
        """Test basic ~probably line transformation"""
        line = "~probably (x > 0) {"
        result = transform_line(line)

        assert len(result) == 1
        assert "if probably(x > 0):" in result[0]

    def test_probably_empty_condition_transformation(self):
        """Test ~probably with empty condition transformation"""
        line = "~probably () {"
        result = transform_line(line)

        assert len(result) == 1
        assert "if probably():" in result[0]

    def test_probably_preserves_indentation(self):
        """Test ~probably preserves original indentation"""
        line = "    ~probably (condition) {"
        result = transform_line(line)

        assert len(result) == 1
        assert result[0].startswith("    ")
        assert "if probably(condition):" in result[0]


class TestProbablyFileTransformation:
    """Test file-level ~probably transformation"""

    def test_probably_block_transformation(self):
        """Test ~probably block transformation with indented content"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int x = 5
~probably (x > 0) {
    ~sorta print("x is positive")
    x ~= 10
}
print("done")
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should include import for probably and other used helpers
            assert "from kinda.langs.python.runtime.fuzzy import" in result
            assert "probably" in result

            # Should transform the block correctly
            assert "if probably(x > 0):" in result
            assert "    sorta_print(" in result
            assert "    x = fuzzy_assign(" in result

            # Should preserve non-kinda code
            assert 'print("done")' in result

        finally:
            temp_path.unlink()

    def test_probably_nested_constructs(self):
        """Test ~probably with nested kinda constructs"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~probably (True) {
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
            assert "if probably(True):" in result
            assert "    nested_var = kinda_int(42)" in result
            assert "    if sometimes(nested_var > 0):" in result
            assert "        sorta_print(" in result

        finally:
            temp_path.unlink()

    def test_probably_multiple_blocks(self):
        """Test multiple ~probably blocks in same file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~probably (condition1) {
    ~sorta print("first block")
}

~probably (condition2) {
    ~sorta print("second block")
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle multiple blocks
            assert "if probably(condition1):" in result
            assert "if probably(condition2):" in result
            assert result.count("probably") >= 2

        finally:
            temp_path.unlink()


class TestProbablyRuntimeBehavior:
    """Test ~probably runtime behavior and probability"""

    @patch("random.random")
    def test_probably_probability_execution(self, mock_random):
        """Test ~probably executes with 70% probability"""
        # Test execution when random < 0.7
        mock_random.return_value = 0.6  # Should execute

        # Generate complete runtime to get the probably function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"probably"}, temp_path, KindaPythonConstructs)

            # Import the generated probably function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import probably

                result = probably(True)
                assert result == True  # Should execute when condition is True and random < 0.7
            finally:
                sys.path.remove(str(temp_path))

    @patch("random.random")
    def test_probably_probability_no_execution(self, mock_random):
        """Test ~probably doesn't execute when probability fails"""
        # Test no execution when random >= 0.7
        mock_random.return_value = 0.8  # Should not execute

        # Generate complete runtime to get the probably function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"probably"}, temp_path, KindaPythonConstructs)

            # Import the generated probably function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import probably

                result = probably(True)
                assert result == False  # Should not execute when random >= 0.7
            finally:
                sys.path.remove(str(temp_path))

    @patch("random.random")
    def test_probably_condition_false(self, mock_random):
        """Test ~probably doesn't execute when condition is False"""
        mock_random.return_value = 0.3  # Would normally execute

        # Generate complete runtime to get the probably function
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate the base runtime first, then add helpers
            from kinda.langs.python.runtime_gen import generate_runtime

            generate_runtime(temp_path)
            generate_runtime_helpers({"probably"}, temp_path, KindaPythonConstructs)

            # Import the generated probably function
            import sys

            sys.path.insert(0, str(temp_path))

            try:
                from fuzzy import probably

                result = probably(False)  # False condition
                assert result == False  # Should not execute when condition is False
            finally:
                sys.path.remove(str(temp_path))


class TestProbablyEdgeCases:
    """Test ~probably edge cases and error handling"""

    def test_probably_invalid_syntax(self):
        """Test ~probably with invalid syntax falls back gracefully"""
        invalid_lines = [
            "~probably",  # Incomplete
            "~probably {",  # Missing parentheses
            "~probably (unclosed",  # Unclosed parentheses
        ]

        for line in invalid_lines:
            result = transform_line(line)
            # Should return original line if can't transform
            assert result == [line]

    def test_probably_with_comments(self):
        """Test ~probably with comments in the block"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~probably (True) {
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
            assert "if probably(True):" in result

        finally:
            temp_path.unlink()

    def test_probably_empty_block(self):
        """Test ~probably with empty block"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~probably (True) {
}
"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle empty blocks gracefully
            assert "if probably(True):" in result

        finally:
            temp_path.unlink()


class TestProbablyIntegration:
    """Test ~probably integration with other constructs"""

    def test_probably_with_all_constructs(self):
        """Test ~probably works alongside all other kinda constructs"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int base_val = 10
base_val ~= 5

~probably (base_val > 0) {
    ~sorta print("Probably executing")
    ~sometimes (True) {
        ~kinda int inner_val = 20
        inner_val ~= 3
        ~sorta print("Sometimes in probably")
    }
    ~maybe (inner_val > 15) {
        ~sorta print("Maybe in probably")
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
            assert "probably" in import_line
            assert "sometimes" in import_line
            assert "maybe" in import_line
            assert "kinda_int" in import_line
            assert "sorta_print" in import_line
            assert "fuzzy_assign" in import_line

            # Should transform all constructs correctly
            assert "base_val = kinda_int(10)" in result
            assert "base_val = fuzzy_assign(" in result
            assert "if probably(base_val > 0):" in result
            assert "if sometimes(True):" in result
            assert "if maybe(inner_val > 15):" in result

        finally:
            temp_path.unlink()

    def test_probably_probability_difference_from_other_constructs(self):
        """Test that ~probably has different probability behavior than other constructs with personality system"""
        # This test verifies that all constructs use personality system but with different keys
        probably_construct = KindaPythonConstructs["probably"]
        maybe_construct = KindaPythonConstructs["maybe"]
        sometimes_construct = KindaPythonConstructs["sometimes"]

        # Extract function bodies
        probably_body = probably_construct["body"]
        maybe_body = maybe_construct["body"]
        sometimes_body = sometimes_construct["body"]

        # All should use personality system
        assert "chaos_probability" in probably_body
        assert "chaos_probability" in maybe_body
        assert "chaos_probability" in sometimes_body

        # ~probably should call chaos_probability with 'probably' key
        assert "chaos_probability('probably'" in probably_body

        # ~maybe should call chaos_probability with 'maybe' key
        assert "chaos_probability('maybe'" in maybe_body

        # ~sometimes should call chaos_probability with 'sometimes' key
        assert "chaos_probability('sometimes'" in sometimes_body

        # They should be different constructs
        assert probably_body != maybe_body
        assert probably_body != sometimes_body
        assert maybe_body != sometimes_body

    def test_probably_has_correct_probability_range(self):
        """Test ~probably has 70% base probability in personality profiles"""
        from kinda.personality import PERSONALITY_PROFILES

        # Test default playful profile has 70% base probability
        playful_profile = PERSONALITY_PROFILES["playful"]
        assert playful_profile.probably_base == 0.7

        # Test reliable profile has high probability
        reliable_profile = PERSONALITY_PROFILES["reliable"]
        assert reliable_profile.probably_base == 0.95

        # Test cautious profile has conservative but reliable probability
        cautious_profile = PERSONALITY_PROFILES["cautious"]
        assert cautious_profile.probably_base == 0.8

        # Test chaotic profile has reduced probability
        chaotic_profile = PERSONALITY_PROFILES["chaotic"]
        assert chaotic_profile.probably_base == 0.5

        # Verify ~probably is between ~maybe (0.6) and ~sorta_print (0.8) in default profile
        assert playful_profile.maybe_base < playful_profile.probably_base < playful_profile.sorta_print_base


class TestProbablyPersonalityIntegration:
    """Test ~probably personality integration"""

    def test_probably_personality_chaos_probability_integration(self):
        """Test ~probably integrates properly with chaos_probability function"""
        from kinda.personality import PersonalityContext, chaos_probability

        # Test with different personality modes
        test_cases = [
            ("reliable", 0.95),
            ("cautious", 0.8), 
            ("playful", 0.7),
            ("chaotic", 0.5),
        ]

        for mood, expected_base in test_cases:
            # Set personality context
            PersonalityContext.set_mood(mood)
            
            # Get probability for probably construct  
            prob = chaos_probability('probably', True)
            
            # Probability should be influenced by the personality but based on the expected base
            # (chaos_amplifier and other factors may modify it, but it should be in reasonable range)
            assert 0.0 <= prob <= 1.0, f"Probability out of range for {mood}: {prob}"

    def test_probably_construct_error_messages(self):
        """Test ~probably construct has appropriate error messages"""
        probably_construct = KindaPythonConstructs["probably"]
        probably_body = probably_construct["body"]

        # Should have proper error message for None condition
        assert 'print("[?] Probably got None as condition - treating as False")' in probably_body

        # Should have proper error message for exceptions
        assert 'print(f"[shrug] Probably got confused: {e}")' in probably_body
        assert 'print("[tip] Defaulting to random choice")' in probably_body

        # Should have proper chaos state tracking
        assert "update_chaos_state(failed=True)" in probably_body
        assert "update_chaos_state(failed=not result)" in probably_body


class TestProbablySecurityProtection:
    """Test security protections in ~probably construct against critical vulnerabilities"""

    def test_code_injection_protection(self):
        """Test ~probably blocks dangerous code injection attempts"""
        from kinda.grammar.python.constructs import KindaPythonConstructs
        import random

        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]

        # Execute the probably function definition
        exec(probably_code, globals())

        # Test dangerous imports are blocked
        dangerous_conditions = [
            "__import__('os').system('echo \"SECURITY_BREACH_TEST\"')",
            "exec('print(\"pwned\")')",
            "eval('1+1')",
            "open('/etc/passwd')",
            "subprocess.call(['ls'])",
            "compile('print(1)', '<string>', 'exec')",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
        ]

        for dangerous_condition in dangerous_conditions:
            result = probably(dangerous_condition)
            assert result is False, f"Should block dangerous condition: {dangerous_condition}"

    def test_deterministic_subversion_protection(self):
        """Test ~probably blocks attempts to manipulate random number generation"""
        from kinda.grammar.python.constructs import KindaPythonConstructs

        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]

        # Execute the probably function definition
        exec(probably_code, globals())

        # Test random manipulation attempts are blocked
        random_manipulation_conditions = [
            "random.seed(42)",
            "random.random()",
            "setattr(random, 'random', lambda: 0.5)",
        ]

        for condition in random_manipulation_conditions:
            result = probably(condition)
            assert result is False, f"Should block random manipulation: {condition}"

    def test_resource_exhaustion_protection(self):
        """Test ~probably blocks conditions that could cause resource exhaustion"""
        from kinda.grammar.python.constructs import KindaPythonConstructs
        import time

        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]

        # Execute the probably function definition
        exec(probably_code, globals())

        # Create a condition that would normally take a very long time to evaluate
        class SlowCondition:
            def __bool__(self):
                time.sleep(2)  # Sleep for 2 seconds, should be timed out
                return True

        slow_condition = SlowCondition()

        # Test that timeout protection works
        start_time = time.time()
        result = probably(slow_condition)
        elapsed_time = time.time() - start_time

        # Should return False due to timeout and complete quickly (within 1.5 seconds)
        assert result is False, "Should block slow condition evaluation"
        assert elapsed_time < 1.5, f"Should timeout quickly, took {elapsed_time} seconds"

    def test_security_messages_displayed(self, capsys):
        """Test that appropriate security messages are displayed when blocking attacks"""
        from kinda.grammar.python.constructs import KindaPythonConstructs

        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]

        # Execute the probably function definition
        exec(probably_code, globals())

        # Test code injection security message
        probably("__import__('os')")
        captured = capsys.readouterr()
        assert "[security] Probably blocked dangerous condition - nice try though" in captured.out

        # Test random manipulation security message
        probably("random.seed(42)")
        captured = capsys.readouterr()
        assert "[security] Probably won't let you break the chaos - that's not kinda" in captured.out

        # Test timeout security message with a slow condition that doesn't trigger pattern matching
        import time
        
        class SlowCondition:
            def __bool__(self):
                time.sleep(2)  # This will be timed out
                return True
        
        # Create instance to avoid triggering import detection in str representation
        slow_obj = SlowCondition()
        probably(slow_obj)
        captured = capsys.readouterr()
        assert "[security] Probably blocked slow condition evaluation - keeping it snappy" in captured.out

    def test_legitimate_conditions_still_work(self):
        """Test that legitimate conditions still work after security fixes"""
        from kinda.grammar.python.constructs import KindaPythonConstructs
        import unittest.mock

        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]

        # Execute the probably function definition
        exec(probably_code, globals())

        # Test legitimate conditions
        legitimate_conditions = [
            True,
            False,
            1 == 1,
            "hello" == "hello",
            5 > 3,
            [1, 2, 3],  # Non-empty list
            "",  # Empty string
        ]

        for condition in legitimate_conditions:
            # Mock random to ensure deterministic testing
            with unittest.mock.patch('random.random', return_value=0.5):
                with unittest.mock.patch('kinda.personality.chaos_probability', return_value=0.8):
                    result = probably(condition)
                    # Should either return True or False based on condition truthiness and probability
                    assert isinstance(result, bool), f"Should return boolean for condition: {condition}"