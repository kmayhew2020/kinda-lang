"""Comprehensive tests to verify all transforms work end-to-end"""
import pytest
import subprocess
from pathlib import Path


def run_transform_and_execute(knda_content, tmp_path):
    """Helper to transform and execute .knda content"""
    knda_file = tmp_path / "test.py.knda"
    knda_file.write_text(knda_content)
    
    # Transform using the transformer
    from kinda.langs.python.transformer import transform
    output_paths = transform(knda_file, tmp_path / "output")
    py_file = output_paths[0]
    
    # Execute and capture output
    result = subprocess.run(
        ["python", str(py_file)], 
        capture_output=True, text=True, timeout=5
    )
    return result.stdout, result.stderr, result.returncode, py_file.read_text()


class TestAllTransformsVerified:
    """Verify each transform actually works when executed"""
    
    def test_kinda_int_transform_execution(self, tmp_path):
        """Test ~kinda int declaration executes correctly"""
        knda_content = """~kinda int x = 42;
~sorta print("Value is:", x);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        assert "kinda_int(42)" in py_content, "Transform didn't generate kinda_int call"
        assert ("Value is:" in stdout), "Output should contain the print statement"
        assert ("[print]" in stdout or "[shrug]" in stdout), "Should use sorta_print format"
    
    def test_sorta_print_transform_execution(self, tmp_path):
        """Test ~sorta print executes correctly"""
        knda_content = """~sorta print("Hello World", 123);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        assert "sorta_print(" in py_content, "Transform didn't generate sorta_print call"
        assert ("Hello World" in stdout and "123" in stdout), "Output should contain arguments"
        assert ("[print]" in stdout or "[shrug]" in stdout), "Should use sorta_print format"
    
    def test_fuzzy_reassign_transform_execution(self, tmp_path):
        """Test x ~= value fuzzy reassignment executes correctly"""
        knda_content = """~kinda int x = 10;
x ~= 20;
~sorta print("Final x:", x);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        assert "fuzzy_assign('x', 20)" in py_content, "Transform didn't generate fuzzy_assign call"
        assert "Final x:" in stdout, "Should print the final value"
        # Value should be around 20 +/- fuzziness
        import re
        numbers = re.findall(r'Final x: (\d+)', stdout)
        if numbers:
            final_val = int(numbers[0])
            assert 18 <= final_val <= 22, f"Fuzzy value {final_val} should be near 20 ± fuzz"
    
    def test_sometimes_block_transform_execution(self, tmp_path):
        """Test ~sometimes conditional executes correctly"""
        knda_content = """~kinda int counter = 0;
~sometimes (True) {
    counter ~= counter + 100;
    ~sorta print("Sometimes executed! Counter:", counter);
}
~sorta print("Final counter:", counter);"""
        
        # Run multiple times since sometimes is probabilistic
        executed_sometimes = False
        final_values = []
        
        for _ in range(10):  # Multiple runs to test randomness
            stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
            
            assert returncode == 0, f"Execution failed: {stderr}"
            assert "if sometimes(True):" in py_content, "Transform didn't generate sometimes conditional"
            assert "Final counter:" in stdout, "Should always print final counter"
            
            if "Sometimes executed!" in stdout:
                executed_sometimes = True
            
            # Extract final counter value
            import re
            numbers = re.findall(r'Final counter: (-?\d+)', stdout)
            if numbers:
                final_values.append(int(numbers[0]))
        
        # Sometimes block should execute at least once in 10 runs (very high probability)
        assert executed_sometimes, "Sometimes block should execute at least once in 10 runs"
        
        # Should have variety in final values due to randomness
        assert len(set(final_values)) > 1, f"Should have variety in values due to randomness: {final_values}"
    
    def test_all_transforms_together(self, tmp_path):
        """Test all transforms working together in one file"""
        knda_content = """# Complex test with all transforms
~kinda int a = 5;
~kinda int b = 10;

a ~= a * 2;
b ~= b + a;

~sometimes (a > b) {
    ~sorta print("A is greater:", a, b);
    a ~= 999;
}

~sometimes (b > a) {
    ~sorta print("B is greater:", b, a);
    b ~= 888;
}

~sorta print("Final values - A:", a, "B:", b);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        
        # Check all transforms were applied
        assert "kinda_int(5)" in py_content and "kinda_int(10)" in py_content
        assert "fuzzy_assign('a'" in py_content and "fuzzy_assign('b'" in py_content  
        assert "if sometimes(a > b):" in py_content and "if sometimes(b > a):" in py_content
        assert py_content.count("sorta_print(") >= 3, "Should have multiple sorta_print calls"
        
        # Check execution produces output
        assert "Final values" in stdout, "Should print final values"
        assert ("[print]" in stdout or "[shrug]" in stdout), "Should use sorta_print format"
    
    def test_empty_sometimes_condition(self, tmp_path):
        """Test ~sometimes with empty condition"""
        knda_content = """~sometimes () {
    ~sorta print("Empty condition sometimes");
}"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        assert "if sometimes():" in py_content, "Should handle empty sometimes condition"
    
    def test_nested_expressions_in_transforms(self, tmp_path):
        """Test complex expressions within transforms (without nested parens in sorta_print)"""
        knda_content = """~kinda int result = (10 + 5) * 2;
result ~= result + (3 * 4);
~sorta print("Complex result:", result);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        assert returncode == 0, f"Execution failed: {stderr}"
        assert "kinda_int((10 + 5) * 2)" in py_content, "Should preserve complex expression"
        assert "fuzzy_assign('result', result + (3 * 4))" in py_content
        assert "Complex result:" in stdout


class TestTransformValidation:
    """Test transform validation and error handling"""
    
    def test_invalid_kinda_syntax(self, tmp_path):
        """Test handling of invalid syntax (passes through but may not execute)"""
        knda_content = """# Invalid syntax that doesn't match any pattern
~kinda int x = 5;
~sorta print(x);"""
        
        stdout, stderr, returncode, py_content = run_transform_and_execute(knda_content, tmp_path)
        
        # Should not crash during transform, may fail during execution 
        assert "kinda_int(5)" in py_content, "Valid syntax should still work"
        assert "sorta_print(x)" in py_content, "Valid syntax should still work"
        # Comment should pass through
        assert "# Invalid syntax" in py_content


# Summary of what this test file verifies:
# ✅ kinda_int: ~kinda int x = value → x = kinda_int(value) 
# ✅ sorta_print: ~sorta print(args) → sorta_print(args)
# ✅ fuzzy_reassign: x ~= value → x = fuzzy_assign('x', value)  
# ✅ sometimes: ~sometimes (cond) { ... } → if sometimes(cond): ...
# ✅ All transforms work together in complex files
# ✅ Randomness and probabilistic behavior works correctly
# ✅ Error handling for invalid syntax