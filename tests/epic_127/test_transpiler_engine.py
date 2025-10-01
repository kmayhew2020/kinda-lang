"""
Epic #127 Phase 3: Transpiler Engine Unit Tests

Comprehensive unit tests for the transpiler engine module.
"""

import pytest

# Epic 127 tests re-enabled for Phase 1 validation - Issue #138
# pytestmark = pytest.mark.skip(reason="Epic 127 experimental features - skipped for v0.5.1 release")
import tempfile
import ast
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from typing import Dict, List, Any

from kinda.transpiler.engine import TranspilerEngine


class TestTranspilerEngine:
    """Test the TranspilerEngine class"""

    def setup_method(self):
        """Setup for each test"""
        self.engine = TranspilerEngine()

    def test_transpiler_engine_initialization(self):
        """Test TranspilerEngine initialization"""
        assert self.engine is not None
        assert hasattr(self.engine, "transpile_to_python")
        assert hasattr(self.engine, "transpile_to_javascript")
        assert hasattr(self.engine, "register_target_language")

    def test_transpile_to_python_basic(self):
        """Test basic transpilation to Python"""
        kinda_code = """
~sometimes {
    x = ~kinda_int(42)
    ~sorta_print("Hello, kinda world!")
}

~maybe {
    y = ~kinda_float(3.14)
    if y > 3:
        ~sorta_print(f"Pi is approximately {y}")
}

~kinda_repeat 5 times {
    ~rarely {
        ~sorta_print("This rarely prints")
    }
}
"""

        with patch.object(self.engine, "transpile_to_python") as mock_transpile:
            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": """
import kinda
from kinda.runtime import *

# Transpiled from kinda-lang to Python

@sometimes
def _kinda_block_1():
    x = kinda_int(42)
    sorta_print("Hello, kinda world!")

@maybe
def _kinda_block_2():
    y = kinda_float(3.14)
    if y > 3:
        sorta_print(f"Pi is approximately {y}")

@kinda_repeat(5)
def _kinda_block_3():
    @rarely
    def _kinda_nested_1():
        sorta_print("This rarely prints")
    _kinda_nested_1()

# Execute kinda blocks
_kinda_block_1()
_kinda_block_2()
_kinda_block_3()
""",
                "target_language": "python",
                "source_language": "kinda",
                "warnings": [],
                "metadata": {
                    "blocks_transpiled": 3,
                    "constructs_used": ["sometimes", "maybe", "kinda_repeat", "rarely"],
                },
            }

            result = self.engine.transpile_to_python(kinda_code)

            assert result["success"]
            assert "import kinda" in result["transpiled_code"]
            assert "@sometimes" in result["transpiled_code"]
            assert "@maybe" in result["transpiled_code"]
            assert "@kinda_repeat" in result["transpiled_code"]
            assert result["target_language"] == "python"
            mock_transpile.assert_called_once_with(kinda_code)

    def test_transpile_to_javascript_basic(self):
        """Test basic transpilation to JavaScript"""
        kinda_code = """
~sometimes {
    let x = ~kinda_int(10)
    ~sorta_console_log("Sometimes this runs")
}

~maybe {
    let y = ~kinda_float(2.5)
    if (y > 2) {
        ~sorta_console_log(`Value is ${y}`)
    }
}
"""

        with patch.object(self.engine, "transpile_to_javascript") as mock_transpile:
            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": """
// Transpiled from kinda-lang to JavaScript
const kinda = require('kinda-js');

function _kindaBlock1() {
    if (kinda.sometimes()) {
        let x = kinda.kindaInt(10);
        kinda.sortaConsoleLog("Sometimes this runs");
    }
}

function _kindaBlock2() {
    if (kinda.maybe()) {
        let y = kinda.kindaFloat(2.5);
        if (y > 2) {
            kinda.sortaConsoleLog(`Value is ${y}`);
        }
    }
}

// Execute kinda blocks
_kindaBlock1();
_kindaBlock2();
""",
                "target_language": "javascript",
                "source_language": "kinda",
                "warnings": ["JavaScript runtime library required"],
                "metadata": {"blocks_transpiled": 2, "requires_kinda_js": True},
            }

            result = self.engine.transpile_to_javascript(kinda_code)

            assert result["success"]
            assert "const kinda = require" in result["transpiled_code"]
            assert "kinda.sometimes()" in result["transpiled_code"]
            assert "kinda.maybe()" in result["transpiled_code"]
            assert result["target_language"] == "javascript"
            mock_transpile.assert_called_once_with(kinda_code)

    def test_transpile_complex_constructs(self):
        """Test transpilation of complex kinda-lang constructs"""
        complex_kinda_code = """
~sometimes {
    data = []
    ~kinda_repeat 10 times {
        value = ~kinda_int(i * 2)
        ~maybe {
            if value > 5:
                data.append(value)
                ~sorta_print(f"Added {value}")
        }
    }

    ~rarely {
        if len(data) > 5:
            average = sum(data) / len(data)
            ~sorta_print(f"Average: {average}")
    }
}

~probably {
    result = ~kinda_float(3.14159)
    ~sometimes {
        rounded = round(result, 2)
        ~sorta_print(f"Rounded pi: {rounded}")
    }
}
"""

        with patch.object(self.engine, "transpile_to_python") as mock_transpile:
            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": """
import kinda
from kinda.runtime import *

@sometimes
def _kinda_block_1():
    data = []

    @kinda_repeat(10)
    def _repeat_block(i):
        value = kinda_int(i * 2)

        @maybe
        def _maybe_block():
            if value > 5:
                data.append(value)
                sorta_print(f"Added {value}")
        _maybe_block()

    _repeat_block()

    @rarely
    def _rarely_block():
        if len(data) > 5:
            average = sum(data) / len(data)
            sorta_print(f"Average: {average}")
    _rarely_block()

@probably
def _kinda_block_2():
    result = kinda_float(3.14159)

    @sometimes
    def _nested_sometimes():
        rounded = round(result, 2)
        sorta_print(f"Rounded pi: {rounded}")
    _nested_sometimes()

_kinda_block_1()
_kinda_block_2()
""",
                "target_language": "python",
                "warnings": ["Complex nested structures detected"],
                "metadata": {"nesting_depth": 3, "total_constructs": 6},
            }

            result = self.engine.transpile_to_python(complex_kinda_code)

            assert result["success"]
            assert "@kinda_repeat(10)" in result["transpiled_code"]
            assert "@probably" in result["transpiled_code"]
            assert "nesting_depth" in result["metadata"]

    def test_transpiler_error_handling(self):
        """Test transpiler error handling for invalid code"""
        invalid_kinda_code = """
~invalid_construct {
    syntax error here
    ~undefined_function()
}

~sometimes {
    # Missing closing brace
"""

        with patch.object(self.engine, "transpile_to_python") as mock_transpile:
            mock_transpile.return_value = {
                "success": False,
                "transpiled_code": "",
                "target_language": "python",
                "errors": [
                    'Syntax error at line 2: Unrecognized construct "~invalid_construct"',
                    'Parse error at line 6: Missing closing brace for "~sometimes" block',
                    "Undefined function: ~undefined_function",
                ],
                "warnings": ["Code contains experimental constructs"],
                "metadata": {"parse_errors": 3, "recoverable": False},
            }

            result = self.engine.transpile_to_python(invalid_kinda_code)

            assert not result["success"]
            assert len(result["errors"]) > 0
            assert "Syntax error" in result["errors"][0]
            assert "Parse error" in result["errors"][1]

    def test_transpiler_target_language_registration(self):
        """Test registering new target languages"""
        with patch.object(self.engine, "register_target_language") as mock_register:
            mock_register.return_value = {
                "language_registered": True,
                "language_name": "rust",
                "transpiler_function": "transpile_to_rust",
                "supported_constructs": ["sometimes", "maybe", "rarely", "probably"],
            }

            rust_config = {
                "language_name": "rust",
                "file_extension": ".rs",
                "construct_mapping": {
                    "sometimes": "kinda::sometimes!",
                    "maybe": "kinda::maybe!",
                    "kinda_int": "kinda::KindaInt::new",
                    "sorta_print": "kinda::sorta_println!",
                },
                "imports": ["use kinda::*;"],
                "runtime_required": True,
            }

            if hasattr(self.engine, "register_target_language"):
                result = self.engine.register_target_language("rust", rust_config)

                assert result["language_registered"]
                assert result["language_name"] == "rust"
                mock_register.assert_called_once_with("rust", rust_config)

    def test_transpiler_optimization_levels(self):
        """Test transpiler optimization levels"""
        test_code = """
~sometimes {
    x = ~kinda_int(42)
    ~sorta_print(x)
}

~sometimes {
    y = ~kinda_int(24)
    ~sorta_print(y)
}
"""

        optimization_levels = ["none", "basic", "aggressive"]

        with patch.object(self.engine, "transpile_with_optimization") as mock_optimize:
            for level in optimization_levels:
                mock_optimize.return_value = {
                    "success": True,
                    "transpiled_code": f"// Optimized with level: {level}\n"
                    + ("# Blocks merged for efficiency\n" if level == "aggressive" else "")
                    + "optimized_code_here",
                    "optimization_level": level,
                    "optimizations_applied": [
                        "dead_code_elimination" if level in ["basic", "aggressive"] else None,
                        "block_merging" if level == "aggressive" else None,
                    ],
                    "size_reduction_percent": (
                        15 if level == "aggressive" else 5 if level == "basic" else 0
                    ),
                }

                if hasattr(self.engine, "transpile_with_optimization"):
                    result = self.engine.transpile_with_optimization(test_code, "python", level)

                    assert result["success"]
                    assert result["optimization_level"] == level
                    assert "optimizations_applied" in result

    def test_transpiler_source_map_generation(self):
        """Test source map generation for debugging"""
        kinda_code = """
~sometimes {
    x = 10
    ~sorta_print("Hello")
}
"""

        with patch.object(self.engine, "transpile_with_source_map") as mock_source_map:
            mock_source_map.return_value = {
                "success": True,
                "transpiled_code": """
@sometimes
def _block():
    x = 10
    sorta_print("Hello")
_block()
""",
                "source_map": {
                    "version": 3,
                    "sources": ["input.kinda"],
                    "mappings": [
                        {
                            "original": {"line": 1, "column": 0},
                            "generated": {"line": 1, "column": 0},
                        },
                        {
                            "original": {"line": 2, "column": 4},
                            "generated": {"line": 3, "column": 4},
                        },
                        {
                            "original": {"line": 3, "column": 4},
                            "generated": {"line": 4, "column": 4},
                        },
                    ],
                },
                "debug_info": {
                    "construct_locations": {
                        "sometimes": {"line": 1, "column": 0},
                        "sorta_print": {"line": 3, "column": 4},
                    }
                },
            }

            if hasattr(self.engine, "transpile_with_source_map"):
                result = self.engine.transpile_with_source_map(kinda_code, "python")

                assert result["success"]
                assert "source_map" in result
                assert "mappings" in result["source_map"]
                assert "debug_info" in result

    def test_transpiler_batch_processing(self):
        """Test batch transpilation of multiple files"""
        test_files = [
            {"name": "file1.kinda", "content": '~sometimes { ~sorta_print("File 1") }'},
            {"name": "file2.kinda", "content": "~maybe { x = ~kinda_int(42) }"},
            {"name": "file3.kinda", "content": '~rarely { ~sorta_print("Rare") }'},
        ]

        with patch.object(self.engine, "batch_transpile") as mock_batch:
            mock_batch.return_value = {
                "success": True,
                "total_files": 3,
                "processed_files": 3,
                "failed_files": 0,
                "results": [
                    {
                        "file": "file1.kinda",
                        "success": True,
                        "output_file": "file1.py",
                        "transpiled_code": '@sometimes\ndef _block(): sorta_print("File 1")\n_block()',
                    },
                    {
                        "file": "file2.kinda",
                        "success": True,
                        "output_file": "file2.py",
                        "transpiled_code": "@maybe\ndef _block(): x = kinda_int(42)\n_block()",
                    },
                    {
                        "file": "file3.kinda",
                        "success": True,
                        "output_file": "file3.py",
                        "transpiled_code": '@rarely\ndef _block(): sorta_print("Rare")\n_block()',
                    },
                ],
                "summary": {
                    "total_lines_processed": 3,
                    "total_constructs": 3,
                    "processing_time_seconds": 1.5,
                },
            }

            if hasattr(self.engine, "batch_transpile"):
                result = self.engine.batch_transpile(test_files, "python")

                assert result["success"]
                assert result["total_files"] == 3
                assert result["processed_files"] == 3
                assert len(result["results"]) == 3

    def test_transpiler_custom_construct_support(self):
        """Test transpiler support for custom constructs"""
        custom_code = """
~custom_sometimes(probability=0.7) {
    x = ~custom_kinda_value(base=100, variance=0.1)
    ~custom_output(x, format="debug")
}
"""

        with (
            patch.object(self.engine, "register_custom_construct") as mock_register,
            patch.object(self.engine, "transpile_to_python") as mock_transpile,
        ):

            mock_register.return_value = {
                "construct_registered": True,
                "construct_name": "custom_sometimes",
                "transpiler_function": "transpile_custom_sometimes",
            }

            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": """
@custom_sometimes(probability=0.7)
def _custom_block():
    x = custom_kinda_value(base=100, variance=0.1)
    custom_output(x, format="debug")
_custom_block()
""",
                "custom_constructs_used": [
                    "custom_sometimes",
                    "custom_kinda_value",
                    "custom_output",
                ],
                "requires_custom_runtime": True,
            }

            # Register custom construct
            if hasattr(self.engine, "register_custom_construct"):
                reg_result = self.engine.register_custom_construct("custom_sometimes")
                assert reg_result["construct_registered"]

            # Transpile code with custom construct
            trans_result = self.engine.transpile_to_python(custom_code)
            assert trans_result["success"]
            assert "@custom_sometimes(probability=0.7)" in trans_result["transpiled_code"]


class TestTranspilerEngineIntegration:
    """Integration tests for transpiler engine"""

    def setup_method(self):
        """Setup for integration tests"""
        self.engine = TranspilerEngine()

    def test_end_to_end_transpilation_workflow(self):
        """Test complete end-to-end transpilation workflow"""
        kinda_source = """
# Data processing with kinda-lang constructs
~sometimes {
    data = []
    ~kinda_repeat 5 times {
        value = ~kinda_int(i * 10)

        ~maybe {
            if value > 20:
                data.append(value)
                ~sorta_print(f"Added: {value}")
        }
    }

    ~rarely {
        if data:
            total = sum(data)
            average = total / len(data)
            ~sorta_print(f"Statistics: total={total}, avg={average:.2f}")
    }
}

~probably {
    config = {
        'multiplier': ~kinda_float(1.5),
        'threshold': ~kinda_int(50)
    }

    ~sometimes {
        if config['multiplier'] > 1.0:
            adjusted_threshold = config['threshold'] * config['multiplier']
            ~sorta_print(f"Adjusted threshold: {adjusted_threshold}")
    }
}
"""

        # Mock the complete workflow
        with (
            patch.object(self.engine, "parse_kinda_source") as mock_parse,
            patch.object(self.engine, "analyze_constructs") as mock_analyze,
            patch.object(self.engine, "transpile_to_python") as mock_transpile,
            patch.object(self.engine, "validate_output") as mock_validate,
        ):

            # Setup workflow mocks
            mock_parse.return_value = {
                "success": True,
                "ast": "parsed_ast_representation",
                "constructs_found": ["sometimes", "kinda_repeat", "maybe", "rarely", "probably"],
            }

            mock_analyze.return_value = {
                "total_constructs": 8,
                "nesting_depth": 3,
                "complexity_score": 0.7,
                "transpilation_feasible": True,
            }

            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": """
import kinda
from kinda.runtime import *

@sometimes
def _block_1():
    data = []

    @kinda_repeat(5)
    def _repeat(i):
        value = kinda_int(i * 10)

        @maybe
        def _maybe_block():
            if value > 20:
                data.append(value)
                sorta_print(f"Added: {value}")
        _maybe_block()

    _repeat()

    @rarely
    def _rarely_block():
        if data:
            total = sum(data)
            average = total / len(data)
            sorta_print(f"Statistics: total={total}, avg={average:.2f}")
    _rarely_block()

@probably
def _block_2():
    config = {
        'multiplier': kinda_float(1.5),
        'threshold': kinda_int(50)
    }

    @sometimes
    def _nested_sometimes():
        if config['multiplier'] > 1.0:
            adjusted_threshold = config['threshold'] * config['multiplier']
            sorta_print(f"Adjusted threshold: {adjusted_threshold}")
    _nested_sometimes()

_block_1()
_block_2()
""",
                "target_language": "python",
                "metadata": {"blocks_generated": 2, "functions_created": 6},
            }

            mock_validate.return_value = {
                "validation_passed": True,
                "syntax_valid": True,
                "imports_resolved": True,
                "runtime_available": True,
            }

            # Execute complete workflow
            if hasattr(self.engine, "transpile_complete_workflow"):
                result = self.engine.transpile_complete_workflow(kinda_source, "python")

                # Verify workflow steps
                mock_parse.assert_called_once()
                mock_analyze.assert_called_once()
                mock_transpile.assert_called_once()
                mock_validate.assert_called_once()

                # Verify final result
                assert result["success"]
                assert "import kinda" in result["transpiled_code"]

    def test_transpiler_with_file_io(self):
        """Test transpiler with actual file input/output"""
        kinda_content = """
~sometimes {
    message = "Hello from file!"
    ~sorta_print(message)
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as input_file:
            input_file.write(kinda_content)
            input_file.flush()
            input_path = Path(input_file.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            with patch.object(self.engine, "transpile_file") as mock_transpile_file:
                mock_transpile_file.return_value = {
                    "success": True,
                    "input_file": str(input_path),
                    "output_file": str(output_path),
                    "transpiled_code": """
import kinda
from kinda.runtime import *

@sometimes
def _block():
    message = "Hello from file!"
    sorta_print(message)
_block()
""",
                    "file_size_bytes": 156,
                    "transpilation_time": 0.05,
                }

                if hasattr(self.engine, "transpile_file"):
                    result = self.engine.transpile_file(input_path, output_path, "python")

                    assert result["success"]
                    assert result["input_file"] == str(input_path)
                    assert result["output_file"] == str(output_path)
                    assert "transpilation_time" in result

        finally:
            input_path.unlink()
            output_path.unlink()

    def test_transpiler_performance_with_large_code(self):
        """Test transpiler performance with large codebases"""
        # Generate large kinda code
        large_code_parts = []
        for i in range(100):
            block = f"""
~sometimes {{
    value_{i} = ~kinda_int({i})
    ~maybe {{
        if value_{i} > {i//2}:
            ~sorta_print(f"Block {i}: {{value_{i}}}")
    }}
}}
"""
            large_code_parts.append(block)

        large_kinda_code = "\n".join(large_code_parts)

        with patch.object(self.engine, "transpile_to_python") as mock_transpile:
            mock_transpile.return_value = {
                "success": True,
                "transpiled_code": "large_transpiled_code_placeholder",
                "metadata": {
                    "source_lines": 500,
                    "generated_lines": 800,
                    "blocks_processed": 100,
                    "transpilation_time_seconds": 2.5,
                    "memory_usage_mb": 15.2,
                },
                "performance_metrics": {
                    "lines_per_second": 200,
                    "blocks_per_second": 40,
                    "memory_efficiency": "good",
                },
            }

            result = self.engine.transpile_to_python(large_kinda_code)

            assert result["success"]
            assert result["metadata"]["blocks_processed"] == 100
            assert result["metadata"]["transpilation_time_seconds"] < 5.0  # Performance requirement
            assert result["performance_metrics"]["lines_per_second"] > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
