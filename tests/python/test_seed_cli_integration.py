#!/usr/bin/env python3
"""
CLI Integration tests for seed functionality
Tests the --seed flag and KINDA_SEED environment variable
"""

import unittest
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch

# Add the kinda package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kinda.cli import setup_personality
from kinda.personality import PersonalityContext, get_seed_info


class TestSeedCLIIntegration(unittest.TestCase):
    """Test CLI seed functionality integration"""

    def setUp(self):
        """Reset personality context before each test"""
        PersonalityContext._instance = None
        # Clear environment variable
        if "KINDA_SEED" in os.environ:
            del os.environ["KINDA_SEED"]

    def tearDown(self):
        """Clean up after each test"""
        PersonalityContext._instance = None
        if "KINDA_SEED" in os.environ:
            del os.environ["KINDA_SEED"]

    def test_setup_personality_with_cli_seed(self):
        """Test setup_personality function with CLI seed argument"""
        setup_personality("playful", 5, seed=12345)
        
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 12345)
        
        seed_info = get_seed_info()
        self.assertEqual(seed_info["seed"], 12345)
        self.assertTrue(seed_info["has_seed"])
        self.assertTrue(seed_info["reproducible"])

    def test_setup_personality_with_env_seed(self):
        """Test setup_personality function with environment variable seed"""
        os.environ["KINDA_SEED"] = "54321"
        
        setup_personality("playful", 5, seed=None)
        
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 54321)

    def test_setup_personality_cli_overrides_env(self):
        """Test that CLI seed overrides environment variable"""
        os.environ["KINDA_SEED"] = "11111"
        
        setup_personality("playful", 5, seed=99999)
        
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 99999)  # CLI should override env

    def test_setup_personality_invalid_env_seed(self):
        """Test handling of invalid environment variable seed"""
        os.environ["KINDA_SEED"] = "not_a_number"
        
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=None)
        
        # Should print warning about invalid environment variable
        mock_print.assert_any_call("[?] Invalid KINDA_SEED value 'not_a_number' - ignoring environment variable")
        
        personality = PersonalityContext.get_instance()
        self.assertIsNone(personality.seed)  # Should fall back to None

    def test_setup_personality_no_seed(self):
        """Test setup_personality function without any seed"""
        setup_personality("playful", 5, seed=None)
        
        personality = PersonalityContext.get_instance()
        self.assertIsNone(personality.seed)
        
        seed_info = get_seed_info()
        self.assertIsNone(seed_info["seed"])
        self.assertFalse(seed_info["has_seed"])
        self.assertFalse(seed_info["reproducible"])

    def test_seed_message_cli_source(self):
        """Test that CLI seed shows correct source message"""
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=42)
        
        # Should show CLI as source
        mock_print.assert_any_call("🌱 Using random seed 42 for reproducible chaos (CLI)")

    def test_seed_message_env_source(self):
        """Test that environment seed shows correct source message"""
        os.environ["KINDA_SEED"] = "789"
        
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=None)
        
        # Should show environment as source
        mock_print.assert_any_call("🌱 Using random seed 789 for reproducible chaos (environment)")

    def test_seed_with_different_moods(self):
        """Test seed functionality with different mood settings"""
        # Test with reliable mood
        setup_personality("reliable", 5, seed=1337)
        reliable_personality = PersonalityContext.get_instance()
        self.assertEqual(reliable_personality.seed, 1337)
        self.assertEqual(reliable_personality.mood, "reliable")
        
        # Test with chaotic mood and same seed
        setup_personality("chaotic", 5, seed=1337)
        chaotic_personality = PersonalityContext.get_instance()
        self.assertEqual(chaotic_personality.seed, 1337)
        self.assertEqual(chaotic_personality.mood, "chaotic")

    def test_seed_with_different_chaos_levels(self):
        """Test seed functionality with different chaos levels"""
        # Test with low chaos
        setup_personality("playful", 2, seed=2020)
        low_chaos = PersonalityContext.get_instance()
        self.assertEqual(low_chaos.seed, 2020)
        self.assertEqual(low_chaos.chaos_level, 2)
        
        # Test with high chaos and same seed
        setup_personality("playful", 9, seed=2020)
        high_chaos = PersonalityContext.get_instance()
        self.assertEqual(high_chaos.seed, 2020)
        self.assertEqual(high_chaos.chaos_level, 9)

    def test_environment_variable_parsing(self):
        """Test various environment variable formats"""
        # Test positive integer
        os.environ["KINDA_SEED"] = "12345"
        setup_personality("playful", 5, seed=None)
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 12345)
        
        # Test negative integer (should work)
        PersonalityContext._instance = None
        os.environ["KINDA_SEED"] = "-9999"
        setup_personality("playful", 5, seed=None)
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, -9999)
        
        # Test zero (should work)
        PersonalityContext._instance = None
        os.environ["KINDA_SEED"] = "0"
        setup_personality("playful", 5, seed=None)
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 0)

    def test_environment_variable_edge_cases(self):
        """Test edge cases for environment variable parsing"""
        # Test with whitespace
        os.environ["KINDA_SEED"] = "  123  "
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=None)
        
        # This should fail because int("  123  ") would actually work in Python
        # but our implementation might be stricter
        personality = PersonalityContext.get_instance()
        # Python's int() handles whitespace, so this should work
        self.assertEqual(personality.seed, 123)

    def create_test_kinda_file(self, content: str) -> str:
        """Helper to create a temporary .knda file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py.knda', delete=False) as f:
            f.write(content)
            return f.name

    def test_cli_seed_integration_basic(self):
        """Test basic CLI integration with --seed flag"""
        # Create a simple test file
        test_content = '''~kinda int x = 42
~sorta print(x)'''
        test_file = self.create_test_kinda_file(test_content)
        
        try:
            # Test that the CLI accepts --seed argument (this would need actual CLI testing)
            # For now, we'll test the argument parsing logic
            from kinda.cli import main
            
            # Test transform with seed
            with patch('sys.argv', ['kinda', 'transform', test_file, '--seed', '12345']):
                with patch('kinda.cli.get_transformer') as mock_transformer:
                    mock_transformer.return_value = None  # Skip actual transformation
                    try:
                        result = main()
                        # Should fail because transformer is None, but seed should be processed
                    except SystemExit:
                        pass  # Expected due to mocked transformer
            
            # Verify seed was set
            personality = PersonalityContext.get_instance()
            self.assertEqual(personality.seed, 12345)
            
        finally:
            # Clean up
            os.unlink(test_file)

    def test_cli_environment_integration(self):
        """Test CLI integration with KINDA_SEED environment variable"""
        # Create a simple test file
        test_content = '''~sometimes (True) {
    ~sorta print("Hello seeded world!")
}'''
        test_file = self.create_test_kinda_file(test_content)
        
        try:
            os.environ["KINDA_SEED"] = "98765"
            
            from kinda.cli import main
            
            # Test transform with env seed
            with patch('sys.argv', ['kinda', 'transform', test_file]):
                with patch('kinda.cli.get_transformer') as mock_transformer:
                    mock_transformer.return_value = None  # Skip actual transformation
                    try:
                        result = main()
                    except SystemExit:
                        pass  # Expected due to mocked transformer
            
            # Verify env seed was used
            personality = PersonalityContext.get_instance()
            self.assertEqual(personality.seed, 98765)
            
        finally:
            # Clean up
            os.unlink(test_file)

    def test_multiple_cli_commands_seed_support(self):
        """Test that all CLI commands (transform, run, interpret) support --seed"""
        test_content = '''~kinda int result = 100
~sorta print("Result:", result)'''
        test_file = self.create_test_kinda_file(test_content)
        
        try:
            from kinda.cli import main
            
            # Test transform command
            with patch('sys.argv', ['kinda', 'transform', test_file, '--seed', '111']):
                with patch('kinda.cli.get_transformer') as mock_transformer:
                    mock_transformer.return_value = None
                    try:
                        main()
                    except SystemExit:
                        pass
            
            personality = PersonalityContext.get_instance()
            self.assertEqual(personality.seed, 111)
            
            # Reset for next test
            PersonalityContext._instance = None
            
            # Test run command
            with patch('sys.argv', ['kinda', 'run', test_file, '--seed', '222']):
                with patch('kinda.cli.get_transformer') as mock_transformer:
                    mock_transformer.return_value = None
                    try:
                        main()
                    except SystemExit:
                        pass
            
            personality = PersonalityContext.get_instance()
            self.assertEqual(personality.seed, 222)
            
            # Reset for next test
            PersonalityContext._instance = None
            
            # Test interpret command
            with patch('sys.argv', ['kinda', 'interpret', test_file, '--seed', '333']):
                with patch('kinda.cli.detect_language', return_value='python'):
                    with patch('kinda.interpreter.repl.run_interpreter') as mock_interpreter:
                        mock_interpreter.return_value = None
                        try:
                            main()
                        except SystemExit:
                            pass
            
            personality = PersonalityContext.get_instance()
            self.assertEqual(personality.seed, 333)
            
        finally:
            # Clean up
            os.unlink(test_file)

    def test_seed_preserves_other_functionality(self):
        """Test that seed functionality doesn't break existing features"""
        # Test with mood and chaos-level combined
        setup_personality("chaotic", 8, seed=55555)
        
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, 55555)
        self.assertEqual(personality.mood, "chaotic")
        self.assertEqual(personality.chaos_level, 8)
        
        # Test that chaos multiplier calculation still works
        self.assertIsNotNone(personality.chaos_multiplier)
        self.assertGreater(personality.chaos_multiplier, 1.0)  # High chaos level

    def test_seed_validation_bounds_checking(self):
        """Test seed validation with bounds checking for security"""
        from kinda.cli import validate_seed
        
        # Test valid seeds
        self.assertEqual(validate_seed(42), 42)
        self.assertEqual(validate_seed(-42), -42)
        self.assertEqual(validate_seed(0), 0)
        self.assertEqual(validate_seed(None), None)
        
        # Test boundary values
        MAX_SEED = 2**31 - 1
        MIN_SEED = -(2**31)
        self.assertEqual(validate_seed(MAX_SEED), MAX_SEED)
        self.assertEqual(validate_seed(MIN_SEED), MIN_SEED)
        
        # Test out of bounds values (should be clamped)
        with patch('kinda.cli.safe_print') as mock_print:
            result = validate_seed(MAX_SEED + 1)
            self.assertEqual(result, MAX_SEED)  # Should be clamped
            mock_print.assert_any_call(f"[?] Seed value {MAX_SEED + 1} is outside safe range ({MIN_SEED} to {MAX_SEED})")
            
        with patch('kinda.cli.safe_print') as mock_print:
            result = validate_seed(MIN_SEED - 1)
            self.assertEqual(result, MIN_SEED)  # Should be clamped
            mock_print.assert_any_call(f"[?] Seed value {MIN_SEED - 1} is outside safe range ({MIN_SEED} to {MAX_SEED})")

    def test_seed_validation_integration(self):
        """Test that seed validation is integrated into setup_personality"""
        MAX_SEED = 2**31 - 1
        
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=MAX_SEED + 1000)
        
        personality = PersonalityContext.get_instance()
        self.assertEqual(personality.seed, MAX_SEED)  # Should be clamped
        
        # Should show validation warning
        mock_print.assert_any_call(f"[?] Seed value {MAX_SEED + 1000} is outside safe range ({-(2**31)} to {MAX_SEED})")

    def test_invalid_seed_type_handling(self):
        """Test handling of invalid seed types from environment"""
        os.environ["KINDA_SEED"] = "definitely_not_a_number"
        
        with patch('kinda.cli.safe_print') as mock_print:
            setup_personality("playful", 5, seed=None)
        
        # Should print warning and ignore invalid env var
        mock_print.assert_any_call("[?] Invalid KINDA_SEED value 'definitely_not_a_number' - ignoring environment variable")
        
        personality = PersonalityContext.get_instance()
        self.assertIsNone(personality.seed)  # Should fall back to None


if __name__ == "__main__":
    unittest.main()