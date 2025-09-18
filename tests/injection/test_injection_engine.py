"""
Tests for Python Injection Engine

This module tests the injection engine that transforms Python code
with kinda-lang constructs.
"""

import pytest
from pathlib import Path
import tempfile

from kinda.injection.injection_engine import (
    InjectionEngine,
    InjectionConfig,
    TransformResult,
    CodeTransformer,
)
from kinda.injection.ast_analyzer import PatternType


class TestInjectionConfig:
    """Test injection configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})

        assert config.safety_level == "safe"
        assert config.preserve_comments is True
        assert config.add_kinda_imports is True
        assert config.probability_overrides == {}

    def test_config_with_overrides(self):
        """Test configuration with probability overrides"""
        overrides = {"sometimes": 0.9, "maybe": 0.3}
        config = InjectionConfig(
            enabled_patterns={PatternType.SOMETIMES}, probability_overrides=overrides
        )

        assert config.probability_overrides == overrides


class TestInjectionEngine:
    """Test the main injection engine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = InjectionEngine()

    def test_inject_source_simple_integer(self):
        """Test injection of simple integer assignment"""
        source = "x = 42"
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})

        result = self.engine.inject_source(source, config)

        assert result.success
        assert "kinda_int" in result.applied_patterns
        assert "import kinda" in result.transformed_code

    def test_inject_source_simple_float(self):
        """Test injection of simple float assignment"""
        source = "pi = 3.14159"
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_FLOAT})

        result = self.engine.inject_source(source, config)

        assert result.success
        assert "kinda_float" in result.applied_patterns

    def test_inject_source_print_statement(self):
        """Test injection of print statements"""
        source = 'print("Hello world")'
        config = InjectionConfig(enabled_patterns={PatternType.SORTA_PRINT})

        result = self.engine.inject_source(source, config)

        assert result.success
        assert "sorta_print" in result.applied_patterns

    def test_inject_source_multiple_patterns(self):
        """Test injection with multiple enabled patterns"""
        source = """
x = 42
print("Hello")
y = 3.14
"""
        config = InjectionConfig(
            enabled_patterns={
                PatternType.KINDA_INT,
                PatternType.KINDA_FLOAT,
                PatternType.SORTA_PRINT,
            }
        )

        result = self.engine.inject_source(source, config)

        assert result.success
        assert len(result.applied_patterns) >= 2
        assert result.performance_estimate > 0

    def test_inject_source_safety_filtering(self):
        """Test that safety level filters dangerous patterns"""
        source = """
if dangerous_condition():
    delete_everything()
"""
        config = InjectionConfig(enabled_patterns={PatternType.SOMETIMES}, safety_level="safe")

        result = self.engine.inject_source(source, config)

        # Should succeed but with limited patterns applied
        assert result.success

    def test_inject_source_no_imports(self):
        """Test injection without adding imports"""
        source = "x = 42"
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT}, add_kinda_imports=False)

        result = self.engine.inject_source(source, config)

        assert result.success
        assert "import kinda" not in result.transformed_code

    def test_inject_file_nonexistent(self):
        """Test injection on non-existent file"""
        fake_path = Path("/nonexistent/file.py")
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})

        result = self.engine.inject_file(fake_path, config)

        assert not result.success
        assert len(result.errors) > 0

    def test_inject_file_valid(self):
        """Test injection on valid file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 42\nprint('hello')")
            temp_path = Path(f.name)

        try:
            config = InjectionConfig(
                enabled_patterns={PatternType.KINDA_INT, PatternType.SORTA_PRINT}
            )

            result = self.engine.inject_file(temp_path, config)

            assert result.success
            assert len(result.applied_patterns) >= 1

        finally:
            temp_path.unlink()  # Clean up

    def test_inject_source_syntax_error(self):
        """Test handling of source with syntax errors"""
        source = "x = 42 +"  # Incomplete expression
        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})

        result = self.engine.inject_source(source, config)

        assert not result.success
        assert len(result.errors) > 0


class TestCodeTransformer:
    """Test the AST transformer"""

    def test_transform_with_no_patterns(self):
        """Test transformer with no matching patterns"""
        import ast
        from kinda.personality import PersonalityContext

        source = "z = 'hello'"
        tree = ast.parse(source)

        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})
        transformer = CodeTransformer([], config, PersonalityContext())

        # Transform should return original tree
        new_tree = transformer.visit(tree)
        assert new_tree is not None

    def test_transform_applied_patterns_tracking(self):
        """Test that transformer tracks applied patterns"""
        import ast
        from kinda.personality import PersonalityContext
        from kinda.injection.ast_analyzer import InjectionPoint, SecurityLevel, CodeLocation

        # Create a simple injection point
        assign_node = ast.parse("x = 42").body[0]
        point = InjectionPoint(
            location=CodeLocation(line=1, column=0),
            pattern_type=PatternType.KINDA_INT,
            safety_level=SecurityLevel.SAFE,
            confidence=0.9,
            node=assign_node,
            context={},
        )

        config = InjectionConfig(enabled_patterns={PatternType.KINDA_INT})
        transformer = CodeTransformer([point], config, PersonalityContext())

        tree = ast.parse("x = 42")
        transformer.visit(tree)

        # Should have applied the kinda_int pattern
        assert "kinda_int" in transformer.applied_patterns


class TestTransformResult:
    """Test the TransformResult dataclass"""

    def test_successful_result(self):
        """Test creation of successful result"""
        result = TransformResult(
            success=True,
            transformed_code="x = kinda.kinda_int(42)",
            applied_patterns=["kinda_int"],
            errors=[],
            warnings=[],
            performance_estimate=2.5,
        )

        assert result.success
        assert result.performance_estimate == 2.5
        assert "kinda_int" in result.applied_patterns

    def test_failed_result(self):
        """Test creation of failed result"""
        result = TransformResult(
            success=False,
            transformed_code="",
            applied_patterns=[],
            errors=["Syntax error"],
            warnings=["Deprecated pattern"],
            performance_estimate=0.0,
        )

        assert not result.success
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
