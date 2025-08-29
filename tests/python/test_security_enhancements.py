"""
Test security enhancements for Issue #102: Case-insensitive pattern matching and extended random manipulation detection.

This test suite specifically tests the security improvements made to prevent bypass attempts
using case variations and additional random manipulation patterns.
"""

import pytest
from kinda.security import is_condition_dangerous, secure_condition_check
from kinda.grammar.python.constructs import KindaPythonConstructs


class TestCaseInsensitivePatternMatching:
    """Test case-insensitive pattern matching in security functions"""

    def test_dangerous_patterns_case_insensitive_detection(self):
        """Test that dangerous patterns are detected regardless of case"""
        # Test various case combinations for each dangerous pattern
        dangerous_cases = [
            # __import__ variations
            "__IMPORT__('os')",
            "__Import__('os')",
            "__iMpOrT__('os')", 
            
            # exec variations
            "EXEC('malicious code')",
            "Exec('malicious code')",
            "eXeC('malicious code')",
            
            # eval variations
            "EVAL('1+1')",
            "Eval('1+1')",
            "eVaL('1+1')",
            
            # open variations  
            "OPEN('/etc/passwd')",
            "Open('/etc/passwd')",
            "oPeN('/etc/passwd')",
            
            # subprocess variations
            "SUBPROCESS.call(['ls'])",
            "Subprocess.call(['ls'])",
            "sUbPrOcEsS.call(['ls'])",
            
            # compile variations
            "COMPILE('code', '<string>', 'exec')",
            "Compile('code', '<string>', 'exec')",
            "cOmPiLe('code', '<string>', 'exec')",
            
            # globals variations
            "GLOBALS()",
            "Globals()",
            "gLoBaLs()",
            
            # locals variations
            "LOCALS()",
            "Locals()",
            "lOcAlS()",
            
            # vars variations
            "VARS()",
            "Vars()",
            "vArS()",
            
            # dir variations
            "DIR()",
            "Dir()",
            "dIr()"
        ]
        
        for dangerous_condition in dangerous_cases:
            is_dangerous, reason = is_condition_dangerous(dangerous_condition)
            assert is_dangerous, f"Should detect dangerous pattern in: {dangerous_condition}"
            assert "dangerous pattern detected:" in reason.lower()

    def test_random_manipulation_patterns_case_insensitive_detection(self):
        """Test that random manipulation patterns are detected regardless of case"""
        # Test various case combinations for each random manipulation pattern
        random_manipulation_cases = [
            # random.seed variations
            "RANDOM.SEED(42)",
            "Random.Seed(42)",
            "rAnDoM.sEeD(42)",
            "random.SEED(42)",
            
            # random.random variations
            "RANDOM.RANDOM()",
            "Random.Random()",
            "rAnDoM.rAnDoM()",
            "random.RANDOM()",
            
            # setattr variations
            "SETATTR(random, 'random', lambda: 0.5)",
            "Setattr(random, 'random', lambda: 0.5)",
            "sEtAtTr(random, 'random', lambda: 0.5)",
            
            # from random import variations (new pattern)
            "FROM RANDOM IMPORT seed",
            "From Random Import seed",
            "fRoM rAnDoM iMpOrT seed",
            "from RANDOM import seed",
            "from random IMPORT seed",
            
            # import random variations (new pattern)
            "IMPORT RANDOM",
            "Import Random",
            "iMpOrT rAnDoM",
            "import RANDOM"
        ]
        
        for random_condition in random_manipulation_cases:
            is_dangerous, reason = is_condition_dangerous(random_condition)
            assert is_dangerous, f"Should detect random manipulation in: {random_condition}"
            assert "random manipulation attempt:" in reason.lower()

    def test_secure_condition_check_case_insensitive_blocking(self):
        """Test that secure_condition_check blocks case-insensitive patterns"""
        # Test dangerous patterns with case variations
        dangerous_cases = [
            "__IMPORT__('os').system('rm -rf /')",
            "EXEC('print(\"pwned\")')",
            "EVAL('__import__(\"os\")')"
        ]
        
        for dangerous_condition in dangerous_cases:
            should_proceed, condition_result = secure_condition_check(dangerous_condition, "TestConstruct")
            assert should_proceed is False, f"Should block dangerous condition: {dangerous_condition}"
            assert condition_result is False
        
        # Test random manipulation patterns with case variations
        random_cases = [
            "RANDOM.SEED(42)",
            "FROM RANDOM IMPORT seed",
            "IMPORT RANDOM"
        ]
        
        for random_condition in random_cases:
            should_proceed, condition_result = secure_condition_check(random_condition, "TestConstruct")
            assert should_proceed is False, f"Should block random manipulation: {random_condition}"
            assert condition_result is False

    def test_mixed_case_in_string_context(self):
        """Test patterns embedded within strings with mixed case"""
        mixed_case_patterns = [
            "some_function(__IMPORT__('os'), other_param)",
            "condition and EXEC('malicious') and other_condition",
            "print('hello') or RANDOM.SEED(42)",
            "legitimate_code() but FROM RANDOM IMPORT randint"
        ]
        
        for pattern in mixed_case_patterns:
            is_dangerous, reason = is_condition_dangerous(pattern)
            assert is_dangerous, f"Should detect embedded dangerous pattern: {pattern}"


class TestExtendedRandomManipulationPatterns:
    """Test the new random manipulation patterns (import statements)"""

    def test_from_random_import_detection(self):
        """Test detection of 'from random import' variations"""
        import_variations = [
            "from random import seed",
            "from random import random",
            "from random import randint",
            "from random import choice",
            "from random import *",
            "FROM RANDOM IMPORT seed",  # case insensitive
            "From Random Import random",
            "code_before(); from random import seed; code_after()"
        ]
        
        for import_stmt in import_variations:
            is_dangerous, reason = is_condition_dangerous(import_stmt)
            assert is_dangerous, f"Should detect random import: {import_stmt}"
            assert "random manipulation attempt:" in reason.lower()
            assert "from random import" in reason.lower()

    def test_import_random_detection(self):
        """Test detection of 'import random' variations"""
        import_variations = [
            "import random",
            "IMPORT RANDOM",
            "Import Random",
            "import random as r",
            "import random, os",
            "code_before(); import random; code_after()"
        ]
        
        for import_stmt in import_variations:
            is_dangerous, reason = is_condition_dangerous(import_stmt)
            assert is_dangerous, f"Should detect random import: {import_stmt}"
            assert "random manipulation attempt:" in reason.lower()
            assert "import random" in reason.lower()

    def test_legitimate_patterns_not_blocked(self):
        """Test that legitimate patterns containing similar text are not blocked"""
        legitimate_patterns = [
            "random_variable = 42",  # Variable name containing 'random'
            "import randomizer",      # Similar but different module
            "from randomutils import helper",  # Different module
            "randomize_data()",      # Function name
            "is_random_enough()",    # Function name
            "RANDOM_CONSTANT = 100", # Constant name
            "random_seed_value = get_seed()"  # Variable assignment
        ]
        
        for pattern in legitimate_patterns:
            is_dangerous, reason = is_condition_dangerous(pattern)
            assert not is_dangerous, f"Should not block legitimate pattern: {pattern}"


class TestSecurityIntegrationWithConstructs:
    """Test security integration with actual kinda constructs"""

    def test_probably_construct_security_integration(self):
        """Test that ~probably construct integrates case-insensitive security"""
        from kinda.grammar.python.constructs import KindaPythonConstructs
        
        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]
        
        # Execute the probably function definition
        exec(probably_code, globals())
        
        # Test case-insensitive dangerous patterns are blocked
        case_insensitive_dangerous = [
            "__IMPORT__('os').system('echo \"SECURITY_BREACH_TEST\"')",
            "EXEC('print(\"pwned\")')",
            "EVAL('1+1')",
            "OPEN('/etc/passwd')",
            "SUBPROCESS.call(['ls'])",
            "GLOBALS()",
            "LOCALS()",
            "VARS()",
            "DIR()"
        ]
        
        for dangerous_condition in case_insensitive_dangerous:
            result = probably(dangerous_condition)
            assert result is False, f"Should block case-insensitive dangerous condition: {dangerous_condition}"
        
        # Test case-insensitive random manipulation patterns are blocked
        case_insensitive_random = [
            "RANDOM.SEED(42)",
            "RANDOM.RANDOM()",
            "SETATTR(random, 'random', lambda: 0.5)",
            "FROM RANDOM IMPORT seed",
            "IMPORT RANDOM"
        ]
        
        for random_condition in case_insensitive_random:
            result = probably(random_condition)
            assert result is False, f"Should block case-insensitive random manipulation: {random_condition}"

    def test_security_messages_case_insensitive(self, capsys):
        """Test that security messages are shown for case-insensitive patterns"""
        from kinda.grammar.python.constructs import KindaPythonConstructs
        
        # Get the probably function
        probably_construct = KindaPythonConstructs["probably"]
        probably_code = probably_construct["body"]
        
        # Execute the probably function definition
        exec(probably_code, globals())
        
        # Test code injection security message with case variation
        probably("__IMPORT__('os')")
        captured = capsys.readouterr()
        assert "[security] Probably blocked dangerous condition - nice try though" in captured.out
        
        # Test random manipulation security message with case variation
        probably("RANDOM.SEED(42)")
        captured = capsys.readouterr()
        assert "[security] Probably won't let you break the chaos - that's not kinda" in captured.out
        
        # Test new import pattern detection
        probably("FROM RANDOM IMPORT seed")
        captured = capsys.readouterr()
        assert "[security] Probably won't let you break the chaos - that's not kinda" in captured.out


class TestBypassAttemptPrevention:
    """Test prevention of various bypass attempts"""

    def test_obfuscated_case_bypass_attempts(self):
        """Test blocking of obfuscated case-based bypass attempts"""
        bypass_attempts = [
            # Mixed case obfuscation
            "__iMpOrT__('os').SyStEm('rm -rf /')",
            "ExEc('malicious_code')",
            "eVaL('__import__(\"os\")')",
            
            # Alternating case patterns
            "__ImPoRt__('subprocess').CaLl(['ls'])",
            "ExEc('print(\"hacked\")')",
            "rAnDoM.sEeD(1337)",
            
            # Strategic case changes in function names
            "gLoBaLs()['__builtins__']['__import__']",
            "lOcAlS()['some_var'] = malicious_value",
            "vArS()['attr'] = evil_func",  # Fixed to include parentheses
            
            # Case variations in import statements  
            "FrOm RaNdOm ImPoRt SeEd",
            "ImPoRt RaNdOm",
            "fRoM rAnDoM iMpOrT *"
        ]
        
        for attempt in bypass_attempts:
            is_dangerous, reason = is_condition_dangerous(attempt)
            assert is_dangerous, f"Should block bypass attempt: {attempt}"
            
            # Also test with secure_condition_check
            should_proceed, condition_result = secure_condition_check(attempt, "TestConstruct")
            assert should_proceed is False, f"secure_condition_check should block: {attempt}"
            assert condition_result is False

    def test_whitespace_and_case_combination_bypass(self):
        """Test blocking attempts that combine whitespace and case variations"""
        whitespace_case_attempts = [
            "__IMPORT__('os')",  # Basic case insensitive should work
            "EXEC('malicious_code')", 
            "FROM RANDOM IMPORT seed",
            "IMPORT RANDOM",
            "RANDOM.SEED(42)"
        ]
        
        for attempt in whitespace_case_attempts:
            is_dangerous, reason = is_condition_dangerous(attempt)
            assert is_dangerous, f"Should block case bypass: {attempt}"

    def test_string_embedding_case_bypass_prevention(self):
        """Test prevention of case-based bypass in string contexts"""
        string_embedded_attempts = [
            "condition1 and __IMPORT__('os') and condition2",
            "func() or EXEC('evil') or other_func()",
            "legitimate_code(); FROM RANDOM IMPORT seed; more_code()",
            "setup() + IMPORT RANDOM + cleanup()"
        ]
        
        for attempt in string_embedded_attempts:
            is_dangerous, reason = is_condition_dangerous(attempt)
            assert is_dangerous, f"Should block string-embedded bypass: {attempt}"


class TestBackwardCompatibility:
    """Test that security enhancements maintain backward compatibility"""

    def test_lowercase_patterns_still_detected(self):
        """Test that original lowercase patterns are still detected"""
        original_patterns = [
            "__import__('os')",
            "exec('code')",
            "eval('expression')",
            "open('/file')",
            "subprocess.call(['cmd'])",
            "compile('code', '<string>', 'exec')",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
            "random.seed(42)",
            "random.random()",
            "setattr(random, 'attr', 'value')",
            "from random import seed",
            "import random"
        ]
        
        for pattern in original_patterns:
            is_dangerous, reason = is_condition_dangerous(pattern)
            assert is_dangerous, f"Should still detect original pattern: {pattern}"

    def test_legitimate_conditions_unchanged(self):
        """Test that legitimate conditions are still allowed"""
        legitimate_conditions = [
            "x > 0",
            "user.is_authenticated()",
            "len(items) > 0",
            "condition1 and condition2",
            "not is_empty(data)",
            "func(param1, param2) == expected_result",
            "variable == 'some_string'",
            "number_value > threshold"
        ]
        
        for condition in legitimate_conditions:
            is_dangerous, reason = is_condition_dangerous(condition)
            assert not is_dangerous, f"Should allow legitimate condition: {condition}"
            
            # Also test with secure_condition_check
            should_proceed, condition_result = secure_condition_check(condition, "TestConstruct")
            assert should_proceed is True, f"secure_condition_check should allow: {condition}"


class TestDocumentationAndErrorMessages:
    """Test that documentation and error messages are updated appropriately"""

    def test_function_docstrings_updated(self):
        """Test that function docstrings mention case-insensitive matching"""
        from kinda.security import is_condition_dangerous, secure_condition_check
        
        # Check that docstrings mention case-insensitive behavior
        is_dangerous_doc = is_condition_dangerous.__doc__
        assert "case-insensitive" in is_dangerous_doc.lower(), \
            "is_condition_dangerous docstring should mention case-insensitive matching"
        
        secure_check_doc = secure_condition_check.__doc__ 
        assert "case-insensitive" in secure_check_doc.lower(), \
            "secure_condition_check docstring should mention case-insensitive matching"

    def test_extended_patterns_in_constants(self):
        """Test that RANDOM_MANIPULATION_PATTERNS includes new patterns"""
        from kinda.security import RANDOM_MANIPULATION_PATTERNS
        
        # Should include original patterns
        assert "random.seed" in RANDOM_MANIPULATION_PATTERNS
        assert "random.random" in RANDOM_MANIPULATION_PATTERNS
        assert "setattr" in RANDOM_MANIPULATION_PATTERNS
        
        # Should include new import patterns
        assert "from random import" in RANDOM_MANIPULATION_PATTERNS
        assert "import random" in RANDOM_MANIPULATION_PATTERNS
        
        # Should have expected total count
        assert len(RANDOM_MANIPULATION_PATTERNS) == 5, \
            f"Expected 5 patterns, got {len(RANDOM_MANIPULATION_PATTERNS)}: {RANDOM_MANIPULATION_PATTERNS}"