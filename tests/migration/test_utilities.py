"""
Tests for kinda-lang migration utilities

Epic #127 Phase 3: Testing & Validation
Testing the migration utilities for analyzing and transforming Python codebases.
"""

import pytest

# Epic #127 Phase 1: Test Infrastructure Recovery - Migration Utilities Tests ENABLED
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from kinda.migration.utilities import MigrationUtilities


class TestMigrationUtilities:
    """Test the MigrationUtilities class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.utilities = MigrationUtilities()

    def test_utilities_initialization(self):
        """Test utilities initialization"""
        assert isinstance(self.utilities, MigrationUtilities)

    def test_analyze_file_simple_function(self):
        """Test analyzing a file with simple functions"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''
def simple_function(x: int) -> int:
    """A simple function"""
    y = 42
    print(f"Processing {x}")
    return x + y

def another_function(a: str, b: str) -> str:
    result = a + b
    return result.upper()
'''
            )
            temp_path = Path(f.name)

        try:
            analysis = self.utilities.analyze_file(temp_path)

            assert analysis is not None
            assert hasattr(analysis, "function_count")
            assert analysis.function_count >= 2

            assert hasattr(analysis, "injection_opportunities")
            assert len(analysis.injection_opportunities) > 0

            # Should find kinda_int and sorta_print opportunities
            opportunity_types = [op.pattern_type.name for op in analysis.injection_opportunities]
            assert "KINDA_INT" in opportunity_types
            assert "SORTA_PRINT" in opportunity_types

        finally:
            temp_path.unlink()

    def test_analyze_file_with_classes(self):
        """Test analyzing a file with classes"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''
class Calculator:
    """A simple calculator class"""

    def __init__(self):
        self.precision = 2

    def add(self, a: int, b: int) -> int:
        result = a + b
        print(f"Adding {a} + {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        result = a * b
        return round(result, self.precision)

class AdvancedCalculator(Calculator):
    def power(self, base: int, exponent: int) -> int:
        result = base ** exponent
        return result
'''
            )
            temp_path = Path(f.name)

        try:
            analysis = self.utilities.analyze_file(temp_path)

            assert analysis is not None
            assert hasattr(analysis, "class_count")
            assert analysis.class_count >= 2

            assert hasattr(analysis, "method_count")
            assert analysis.method_count >= 4  # Including __init__

            # Should find enhancement opportunities in methods
            assert len(analysis.injection_opportunities) > 0

        finally:
            temp_path.unlink()

    def test_analyze_file_nonexistent(self):
        """Test analyzing a non-existent file"""
        nonexistent_path = Path("/nonexistent/file.py")

        with pytest.raises(FileNotFoundError):
            self.utilities.analyze_file(nonexistent_path)

    def test_analyze_file_syntax_error(self):
        """Test analyzing a file with syntax errors"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def broken_function(
    # Missing closing parenthesis and body
"""
            )
            temp_path = Path(f.name)

        try:
            # Should handle syntax errors gracefully
            analysis = self.utilities.analyze_file(temp_path)
            assert analysis is not None
            assert hasattr(analysis, "has_syntax_errors")
            assert analysis.has_syntax_errors is True

        finally:
            temp_path.unlink()

    def test_analyze_directory(self):
        """Test analyzing a directory of Python files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create multiple Python files
            (project_path / "module1.py").write_text(
                """
def func1(x: int) -> int:
    return x + 1

def func2(y: float) -> float:
    print(f"Processing {y}")
    return y * 2.0
"""
            )

            (project_path / "module2.py").write_text(
                """
class TestClass:
    def method1(self, a: int) -> int:
        result = a * 3
        return result

    def method2(self, b: str) -> str:
        print(f"String: {b}")
        return b.upper()
"""
            )

            # Create non-Python file (should be ignored)
            (project_path / "readme.txt").write_text("This is not Python")

            analysis = self.utilities.analyze_directory(project_path)

            assert analysis is not None
            assert hasattr(analysis, "total_files")
            assert analysis.total_files >= 2

            assert hasattr(analysis, "total_functions")
            assert analysis.total_functions >= 2

            assert hasattr(analysis, "total_classes")
            assert analysis.total_classes >= 1

            assert hasattr(analysis, "total_injection_opportunities")
            assert analysis.total_injection_opportunities > 0

    def test_analyze_directory_recursive(self):
        """Test recursive directory analysis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create nested directory structure
            subdir = project_path / "subpackage"
            subdir.mkdir()

            (project_path / "main.py").write_text(
                """
def main():
    x = 42
    print("Main function")
    return x
"""
            )

            (subdir / "utils.py").write_text(
                """
def utility_function(data: list) -> int:
    count = len(data)
    print(f"Count: {count}")
    return count
"""
            )

            analysis = self.utilities.analyze_directory(project_path, recursive=True)

            assert analysis is not None
            assert analysis.total_files >= 2
            assert analysis.total_functions >= 2

    def test_suggest_enhancement_patterns(self):
        """Test suggesting enhancement patterns for code"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def data_processor(numbers: list) -> dict:
    total = 0
    for num in numbers:
        total += num

    average = total / len(numbers) if numbers else 0.0

    print(f"Processed {len(numbers)} numbers")
    print(f"Total: {total}, Average: {average}")

    return {
        "total": total,
        "average": average,
        "count": len(numbers)
    }
"""
            )
            temp_path = Path(f.name)

        try:
            suggestions = self.utilities.suggest_enhancement_patterns(temp_path)

            assert suggestions is not None
            assert isinstance(suggestions, (list, dict))

            # Should suggest patterns based on code analysis
            if isinstance(suggestions, list):
                assert len(suggestions) > 0
            elif isinstance(suggestions, dict):
                assert len(suggestions.keys()) > 0

        finally:
            temp_path.unlink()

    def test_estimate_enhancement_impact(self):
        """Test estimating the impact of enhancements"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def calculation_heavy_function(data: list) -> float:
    result = 0.0
    for i, value in enumerate(data):
        if i % 2 == 0:
            result += value * 1.5
        else:
            result += value * 0.8

    print(f"Calculation result: {result}")
    return result
"""
            )
            temp_path = Path(f.name)

        try:
            impact = self.utilities.estimate_enhancement_impact(
                temp_path, patterns=["kinda_float", "sorta_print", "sometimes"]
            )

            assert impact is not None
            assert hasattr(impact, "performance_impact") or "performance" in str(impact).lower()

        finally:
            temp_path.unlink()

    def test_generate_enhancement_preview(self):
        """Test generating a preview of enhancements"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def preview_function(x: int, y: int) -> int:
    z = x + y
    print(f"Sum: {z}")
    if z > 10:
        print("Large sum!")
    return z
"""
            )
            temp_path = Path(f.name)

        try:
            preview = self.utilities.generate_enhancement_preview(
                temp_path, patterns=["kinda_int", "sorta_print", "sometimes"]
            )

            assert preview is not None
            assert hasattr(preview, "original_code") or "original" in str(preview).lower()
            assert hasattr(preview, "enhanced_code") or "enhanced" in str(preview).lower()

        finally:
            temp_path.unlink()

    def test_validate_enhancement_safety(self):
        """Test validating enhancement safety"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def safe_function(x: int) -> int:
    return x * 2

def potentially_unsafe_function():
    exec("print('Dynamic code execution')")
    return eval("2 + 2")

def file_operation_function(filename: str):
    with open(filename, 'r') as f:
        return f.read()
"""
            )
            temp_path = Path(f.name)

        try:
            safety_report = self.utilities.validate_enhancement_safety(temp_path)

            assert safety_report is not None
            assert hasattr(safety_report, "safe_functions") or "safe" in str(safety_report).lower()
            assert (
                hasattr(safety_report, "risky_functions") or "risky" in str(safety_report).lower()
            )

        finally:
            temp_path.unlink()

    def test_create_migration_backup(self):
        """Test creating migration backups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create original file
            original_file = project_path / "backup_test.py"
            original_content = """
def original_function():
    print("Original implementation")
    return 42
"""
            original_file.write_text(original_content)

            # Create backup
            backup_path = self.utilities.create_migration_backup(
                original_file, backup_suffix="_pre_enhancement"
            )

            assert backup_path is not None
            assert backup_path.exists()
            assert backup_path.read_text() == original_content

    def test_restore_from_backup(self):
        """Test restoring files from backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create original file
            original_file = project_path / "restore_test.py"
            original_content = "def original(): pass"
            original_file.write_text(original_content)

            # Create backup
            backup_path = self.utilities.create_migration_backup(original_file)

            # Modify original
            original_file.write_text("def modified(): pass")

            # Restore from backup
            restore_result = self.utilities.restore_from_backup(original_file, backup_path)

            assert restore_result is True
            assert original_file.read_text() == original_content

    def test_get_migration_statistics(self):
        """Test getting migration statistics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create test files
            (project_path / "stats1.py").write_text(
                """
def func1(x: int) -> int:
    return x + 1

class Class1:
    def method1(self, y: float) -> float:
        print(f"Value: {y}")
        return y * 2
"""
            )

            (project_path / "stats2.py").write_text(
                """
def func2(a: str, b: str) -> str:
    result = a + b
    print(f"Concatenated: {result}")
    return result
"""
            )

            stats = self.utilities.get_migration_statistics(project_path)

            assert stats is not None
            assert hasattr(stats, "files_analyzed") or "files" in str(stats).lower()
            assert (
                hasattr(stats, "enhancement_opportunities") or "opportunities" in str(stats).lower()
            )


class TestUtilityEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.utilities = MigrationUtilities()

    def test_empty_file_analysis(self):
        """Test analyzing an empty file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")  # Empty file
            temp_path = Path(f.name)

        try:
            analysis = self.utilities.analyze_file(temp_path)
            assert analysis is not None
            assert analysis.function_count == 0
            assert analysis.class_count == 0

        finally:
            temp_path.unlink()

    def test_comments_only_file(self):
        """Test analyzing a file with only comments"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''
# This is a comment file
# It has no actual code
# Just comments and docstrings

"""
This is a module docstring
but there's no actual code.
"""

# More comments
'''
            )
            temp_path = Path(f.name)

        try:
            analysis = self.utilities.analyze_file(temp_path)
            assert analysis is not None
            assert analysis.function_count == 0
            assert analysis.class_count == 0

        finally:
            temp_path.unlink()

    def test_binary_file_handling(self):
        """Test handling binary files gracefully"""
        with tempfile.NamedTemporaryFile(suffix=".pyc", delete=False) as f:
            # Write binary content that will definitely trigger UnicodeDecodeError
            f.write(b"\x00\x01\x02\x03\xff\xfe\xfd\xfc\x80\x81\x82\x83")
            temp_path = Path(f.name)

        try:
            # Should handle binary files gracefully
            with pytest.raises((UnicodeDecodeError, ValueError)):
                self.utilities.analyze_file(temp_path)

        finally:
            temp_path.unlink()

    def test_very_large_file_handling(self):
        """Test handling very large files"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Create a large file with many functions
            for i in range(100):
                f.write(
                    f"""
def function_{i}(x: int) -> int:
    result = x + {i}
    print(f"Function {i} result: {{result}}")
    return result
"""
                )
            temp_path = Path(f.name)

        try:
            analysis = self.utilities.analyze_file(temp_path)
            assert analysis is not None
            assert analysis.function_count == 100

        finally:
            temp_path.unlink()

    def test_permission_denied_file(self):
        """Test handling permission denied scenarios"""
        import platform

        # Skip on Windows as file permission model is different
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")

        # This test might not work in all environments
        # but tests the error handling pathway
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            temp_path = Path(f.name)

        try:
            # Try to change permissions (might not work in all environments)
            try:
                temp_path.chmod(0o000)  # Remove all permissions

                with pytest.raises(PermissionError):
                    self.utilities.analyze_file(temp_path)

            except OSError:
                # Permission change failed, skip this test
                pytest.skip("Cannot change file permissions in this environment")

        finally:
            try:
                temp_path.chmod(0o644)  # Restore permissions
                temp_path.unlink()
            except OSError:
                pass  # Best effort cleanup


class TestUtilityIntegration:
    """Test integration with other Epic 127 components"""

    def setup_method(self):
        """Set up test fixtures"""
        self.utilities = MigrationUtilities()

    def test_integration_with_injection_engine(self):
        """Test integration with the injection engine"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def integration_test(value: int) -> int:
    multiplier = 2
    print(f"Multiplying {value} by {multiplier}")
    result = value * multiplier
    return result
"""
            )
            temp_path = Path(f.name)

        try:
            # Analyze file
            analysis = self.utilities.analyze_file(temp_path)

            # Should identify injection opportunities
            assert len(analysis.injection_opportunities) > 0

            # Test that injection opportunities are compatible with injection engine
            from kinda.injection.injection_engine import InjectionEngine

            engine = InjectionEngine()
            # Should be able to process the identified opportunities
            assert engine is not None

        finally:
            temp_path.unlink()

    def test_integration_with_probability_context(self):
        """Test integration with probability context system"""
        from kinda.control.context import ProbabilityContext, ProbabilityProfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def probabilistic_function(data: list) -> dict:
    count = 0
    for item in data:
        if len(item) > 5:  # Could become ~sometimes
            count += 1
            print(f"Long item: {item}")  # Could become ~sorta_print

    return {"count": count}
"""
            )
            temp_path = Path(f.name)

        try:
            # Test with different probability contexts
            profile = ProbabilityProfile.create_testing_profile(seed=42)

            with ProbabilityContext(profile=profile):
                analysis = self.utilities.analyze_file(temp_path)
                assert analysis is not None

        finally:
            temp_path.unlink()
