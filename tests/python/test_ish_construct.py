#!/usr/bin/env python3

import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

# Import test modules  
from kinda.grammar.python.matchers import find_ish_constructs, match_python_construct
from kinda.langs.python.transformer import transform_line, _transform_ish_constructs


class TestIshMatching:
    """Test pattern matching for ~ish constructs."""
    
    def test_find_ish_value_patterns(self):
        """Test finding ~ish value patterns."""
        patterns = find_ish_constructs("x = 42~ish")
        assert len(patterns) == 1
        assert patterns[0][0] == "ish_value"  # construct type
        assert patterns[0][1].group() == "42~ish"  # matched pattern
        
    def test_find_ish_comparison_patterns(self):
        """Test finding ~ish comparison patterns."""  
        patterns = find_ish_constructs("if score ~ish 100:")
        assert len(patterns) == 1
        assert patterns[0][0] == "ish_comparison"  # construct type
        assert patterns[0][1].group() == "score ~ish 100"  # matched pattern


class TestIshTransformation:
    """Test transformation of ~ish constructs."""
    
    def test_transform_ish_value(self):
        """Test transformation of ~ish values."""
        result = transform_line("x = 42~ish")
        assert isinstance(result, list)
        assert "ish_value(42)" in result[0]
        
    def test_transform_ish_comparison(self):
        """Test transformation of ~ish comparisons."""
        result = transform_line("if score ~ish 100:")
        assert isinstance(result, list)
        assert "ish_comparison(score, 100)" in result[0]


class TestIshIntegration:
    """Test ~ish construct integration with existing features."""
    
    def test_ish_with_other_constructs(self):
        """Test ~ish working with other kinda constructs."""
        result = transform_line("~sorta print(42~ish)")
        assert isinstance(result, list)
        # Should only transform ~ish, not ~sorta since it's inline only
        assert "ish_value(42)" in result[0]
        
    def test_ish_in_expressions(self):
        """Test ~ish in complex expressions."""
        result = transform_line("result = x + 42~ish - y")
        assert isinstance(result, list)
        assert "ish_value(42)" in result[0]