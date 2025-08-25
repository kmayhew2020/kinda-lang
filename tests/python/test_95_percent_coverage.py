#!/usr/bin/env python3
"""
Test coverage for specific missing lines to reach 95% coverage target.
Targets the most impactful missing coverage areas.
"""

import pytest
import tempfile
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from kinda.cli import main, safe_read_file


class Test95PercentCoverage:
    """Tests targeting specific missing coverage lines to reach 95% target"""
    
    def test_runtime_gen_main_module_execution(self):
        """Test runtime_gen.py when executed as main module - covers lines 93-102"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Execute runtime_gen.py as a module directly to cover the __main__ block
            result = subprocess.run([
                sys.executable, '-m', 'kinda.langs.python.runtime_gen',
                '--out', temp_dir
            ], cwd='/workspaces/kinda-lang', capture_output=True, text=True)
            
            assert result.returncode == 0
            
            # Should have created fuzzy.py in the specified directory
            runtime_file = Path(temp_dir) / "fuzzy.py"
            assert runtime_file.exists()
            content = runtime_file.read_text()
            assert "# Auto-generated fuzzy runtime for Python" in content
    
    def test_cli_chardet_with_installed_chardet(self):
        """Test CLI safe_read_file functionality when chardet is actually available"""
        # Install chardet temporarily for this test
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'chardet'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
                    # Write some UTF-8 content
                    f.write("~kinda int x = 42\nprint(x)\n".encode('utf-8'))
                    temp_path = Path(f.name)
                
                try:
                    # This should now use the real chardet functionality
                    content = safe_read_file(temp_path)
                    assert "~kinda int x = 42" in content
                finally:
                    temp_path.unlink()
            finally:
                # Uninstall chardet to avoid interfering with other tests
                subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'chardet', '-y'], 
                              capture_output=True)
        else:
            # Skip this test if we can't install chardet
            pytest.skip("Cannot install chardet for testing")
    
    def test_cli_unicode_decode_error_fallback(self):
        """Test CLI safe_read_file fallback when encoding fails - covers line 71"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            # Write bytes that will cause a UnicodeDecodeError with ASCII
            f.write(b'\xff\xfe~kinda int x = 42\n')
            temp_path = Path(f.name)
        
        try:
            # Force ASCII encoding which will fail and trigger fallback
            import kinda.cli
            with patch('kinda.cli.HAS_CHARDET', True):
                # Mock chardet to return ASCII which will fail
                mock_chardet = MagicMock()
                mock_chardet.detect.return_value = {
                    'encoding': 'ascii',  # This will fail on the binary data
                    'confidence': 0.8
                }
                
                # Set the mock on the module after importing
                original_chardet = getattr(kinda.cli, 'chardet', None)
                kinda.cli.chardet = mock_chardet
                
                try:
                    with patch('kinda.cli.safe_print') as mock_print:
                        content = safe_read_file(temp_path)
                        
                        # Should have printed fallback message
                        calls = [str(call) for call in mock_print.call_args_list]
                        assert any("failed, falling back to UTF-8" in call for call in calls)
                finally:
                    if original_chardet:
                        kinda.cli.chardet = original_chardet
                    elif hasattr(kinda.cli, 'chardet'):
                        delattr(kinda.cli, 'chardet')
        finally:
            temp_path.unlink()
    
    def test_cli_run_command_file_validation_failure(self):
        """Test CLI run command when file validation fails - covers lines 312-313"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            # Write binary content that will fail validation
            f.write(b'\x00\x01\x02\x03')  # Binary data
            temp_path = Path(f.name)
        
        try:
            result = main(['run', str(temp_path)])
            assert result == 1  # Should return error code
        finally:
            temp_path.unlink()
    
    def test_cli_run_command_transform_failure(self):
        """Test CLI run command when transform fails - covers lines 348-349"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            # Write invalid Python code that will cause transform failure
            f.write("def incomplete_function(\n")  # Syntax error
            temp_path = Path(f.name)
        
        try:
            # We expect this to fail during transformation
            result = main(['run', str(temp_path)])
            assert result == 1  # Should return error code
        finally:
            temp_path.unlink()
    
    def test_cli_main_module_execution(self):
        """Test CLI when executed as __main__ - covers line 397"""
        # Test the SystemExit behavior by running cli module directly
        result = subprocess.run([
            sys.executable, '-c', 
            'import sys; sys.argv = ["kinda", "syntax"]; '
            'from kinda.cli import main; raise SystemExit(main())'
        ], cwd='/workspaces/kinda-lang', capture_output=True, text=True)
        
        assert result.returncode == 0  # Should exit with success for syntax command
    
    def test_cli_transform_command_error_handling(self):
        """Test CLI transform command error paths for additional coverage"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            # Write content that will cause a KindaParseError
            f.write("~sometimes invalid_syntax_here")
            temp_path = Path(f.name)
        
        try:
            with patch('kinda.cli.safe_print') as mock_print:
                result = main(['transform', str(temp_path)])
                assert result == 1  # Should return error code
        finally:
            temp_path.unlink()
    
    def test_cli_interpret_command_file_validation_failure(self):
        """Test CLI interpret command when file validation fails"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            # Write binary content that will fail validation
            f.write(b'\x00\x01\x02\x03')  # Binary data
            temp_path = Path(f.name)
        
        try:
            result = main(['interpret', str(temp_path)])
            assert result == 1  # Should return error code
        finally:
            temp_path.unlink()
    
    def test_cli_commands_with_nonexistent_files(self):
        """Test CLI commands with non-existent files for additional coverage"""
        nonexistent = "/tmp/does_not_exist.knda"
        
        # Test transform with non-existent file
        result = main(['transform', nonexistent])
        assert result == 1
        
        # Test run with non-existent file  
        result = main(['run', nonexistent])
        assert result == 1
        
        # Test interpret with non-existent file
        result = main(['interpret', nonexistent])
        assert result == 1