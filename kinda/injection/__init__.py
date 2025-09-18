"""
Python Injection Framework for Kinda-Lang

Epic #127: Python Enhancement Bridge - Core injection system that allows
seamless integration of kinda-lang constructs into Python code.
"""

from .ast_analyzer import PythonASTAnalyzer
from .injection_engine import InjectionEngine, InjectionConfig
from .patterns import PatternLibrary
from .security import InjectionSecurityValidator

__all__ = [
    "PythonASTAnalyzer",
    "InjectionEngine",
    "InjectionConfig",
    "PatternLibrary",
    "InjectionSecurityValidator",
]

__version__ = "0.5.5-dev"
