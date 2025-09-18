"""
Security Validation for Python Injection

This module provides enhanced security validation specifically for injection
operations, extending the base kinda-lang security framework.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, TYPE_CHECKING

from ..security import secure_condition_check, is_condition_dangerous

if TYPE_CHECKING:
    from .ast_analyzer import InjectionPoint
    from .injection_engine import InjectionConfig


# Local type definitions to avoid circular imports
class SecurityLevel:
    SAFE = "safe"
    CAUTION = "caution"
    RISKY = "risky"
    DANGEROUS = "dangerous"


@dataclass
class SecurityResult:
    """Result of security validation"""
    is_safe: bool
    errors: List[str]
    warnings: List[str]
    risk_level: str
    recommendations: List[str]


@dataclass
class InjectionAuditEntry:
    """Single audit log entry for injection operations"""
    timestamp: str
    file_path: str
    patterns_applied: List[str]
    security_level: str
    user_context: Dict[str, Any]
    success: bool
    errors: List[str]


class InjectionSecurityValidator:
    """Enhanced security validation for injection operations"""

    def __init__(self):
        self.audit_logger = InjectionAuditLogger()

        # Define security policies
        self.dangerous_imports = {
            'os', 'subprocess', 'eval', 'exec', 'compile',
            'importlib', '__import__', 'globals', 'locals'
        }

        self.sensitive_attributes = {
            '__dict__', '__class__', '__bases__', '__mro__',
            '__subclasses__', '__globals__', '__code__'
        }

        self.critical_functions = {
            'setattr', 'delattr', 'hasattr', 'getattr',
            'open', 'file', 'input', 'raw_input'
        }

    def validate_injection_request(self, file_path: Path,
                                 injection_points: List['InjectionPoint'],
                                 config: 'InjectionConfig') -> SecurityResult:
        """Validate entire injection request for security"""
        errors = []
        warnings = []
        recommendations = []

        # Basic file security check
        file_result = self._validate_file_security(file_path)
        errors.extend(file_result.errors)
        warnings.extend(file_result.warnings)

        # Validate each injection point
        for point in injection_points:
            point_result = self._validate_injection_point_security(point, config)
            errors.extend(point_result.errors)
            warnings.extend(point_result.warnings)
            recommendations.extend(point_result.recommendations)

        # Check for dangerous pattern combinations
        combination_result = self._validate_pattern_combinations(injection_points)
        errors.extend(combination_result.errors)
        warnings.extend(combination_result.warnings)

        # Determine overall risk level
        risk_level = self._calculate_risk_level(errors, warnings, injection_points)

        is_safe = len(errors) == 0 and risk_level in ['low', 'medium']

        return SecurityResult(
            is_safe=is_safe,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level,
            recommendations=recommendations
        )

    def validate_ast_modification(self, original: ast.AST, modified: ast.AST) -> SecurityResult:
        """Validate that AST modifications are safe"""
        errors = []
        warnings = []
        recommendations = []

        # Check for new dangerous constructs introduced
        original_risks = self._analyze_ast_risks(original)
        modified_risks = self._analyze_ast_risks(modified)

        new_risks = modified_risks - original_risks

        if new_risks:
            for risk in new_risks:
                if risk['severity'] == 'high':
                    errors.append(f"High-risk construct introduced: {risk['description']}")
                else:
                    warnings.append(f"New risk introduced: {risk['description']}")

        # Check for integrity preservation
        if not self._verify_ast_integrity(original, modified):
            errors.append("AST integrity check failed - unexpected structural changes")

        risk_level = 'high' if errors else ('medium' if warnings else 'low')

        return SecurityResult(
            is_safe=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level,
            recommendations=recommendations
        )

    def authorize_pattern_usage(self, pattern_type: str, context: Dict[str, Any]) -> bool:
        """Authorize specific pattern usage based on context"""
        # Check user permissions
        user_level = context.get('user_level', 'basic')

        # Advanced patterns require higher permissions
        advanced_patterns = {'sometimes', 'kinda_repeat', 'welp', 'assert_probability'}

        if pattern_type in advanced_patterns and user_level == 'basic':
            return False

        # Check file context
        file_path = context.get('file_path', '')
        if self._is_critical_file(file_path):
            # Only allow safe patterns in critical files
            safe_patterns = {'kinda_int', 'kinda_float', 'sorta_print'}
            return pattern_type in safe_patterns

        return True

    def _validate_file_security(self, file_path: Path) -> SecurityResult:
        """Validate security aspects of the target file"""
        errors = []
        warnings = []
        recommendations = []

        # Check file permissions
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return SecurityResult(False, errors, warnings, 'high', recommendations)

        # Check if it's a critical system file
        if self._is_critical_file(str(file_path)):
            warnings.append(f"Injecting into critical file: {file_path}")
            recommendations.append("Consider testing in a non-critical environment first")

        # Check file content for dangerous patterns
        try:
            content = file_path.read_text(encoding='utf-8')
            dangerous_patterns = self._scan_dangerous_patterns(content)

            if dangerous_patterns:
                warnings.extend([f"Dangerous pattern found: {pattern}" for pattern in dangerous_patterns])
                recommendations.append("Review dangerous patterns before injection")

        except Exception as e:
            errors.append(f"Could not read file for security scan: {e}")

        risk_level = 'high' if errors else ('medium' if warnings else 'low')

        return SecurityResult(
            is_safe=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level,
            recommendations=recommendations
        )

    def _validate_injection_point_security(self, point: 'InjectionPoint',
                                         config: 'InjectionConfig') -> SecurityResult:
        """Validate security of individual injection point"""
        errors = []
        warnings = []
        recommendations = []

        # Check security level compatibility
        if point.safety_level == SecurityLevel.DANGEROUS:
            errors.append(f"Dangerous injection point at {point.location}")

        if point.safety_level == SecurityLevel.RISKY and config.safety_level == 'safe':
            warnings.append(f"Risky injection point at {point.location} with safe config")

        # Check node-specific security concerns
        node_risks = self._analyze_node_security(point.node)
        for risk in node_risks:
            if risk['severity'] == 'high':
                errors.append(f"High-risk node at {point.location}: {risk['description']}")
            else:
                warnings.append(f"Risk at {point.location}: {risk['description']}")

        # Check confidence level
        if point.confidence < 0.3:
            warnings.append(f"Low confidence injection at {point.location}")
            recommendations.append("Consider manual review for low-confidence injections")

        risk_level = 'high' if errors else ('medium' if warnings else 'low')

        return SecurityResult(
            is_safe=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level=risk_level,
            recommendations=recommendations
        )

    def _validate_pattern_combinations(self, points: List['InjectionPoint']) -> SecurityResult:
        """Validate security of pattern combinations"""
        errors = []
        warnings = []

        pattern_types = [point.pattern_type for point in points]

        # Check for dangerous combinations
        if len(pattern_types) > 10:
            warnings.append("High number of injection points may impact debugging")

        # Check for conflicting patterns
        # (Add specific pattern conflict checks as needed)

        return SecurityResult(
            is_safe=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_level='low',
            recommendations=[]
        )

    def _calculate_risk_level(self, errors: List[str], warnings: List[str],
                            points: List['InjectionPoint']) -> str:
        """Calculate overall risk level"""
        if errors:
            return 'high'

        risk_score = 0
        risk_score += len(warnings) * 1

        # Add risk based on injection points
        for point in points:
            if point.safety_level == SecurityLevel.RISKY:
                risk_score += 2
            elif point.safety_level == SecurityLevel.CAUTION:
                risk_score += 1

        if risk_score >= 10:
            return 'high'
        elif risk_score >= 5:
            return 'medium'
        else:
            return 'low'

    def _analyze_ast_risks(self, tree: ast.AST) -> Set[Dict[str, str]]:
        """Analyze AST for security risks"""
        risks = set()

        class RiskAnalyzer(ast.NodeVisitor):
            def visit_Import(self, node: ast.Import) -> None:
                for alias in node.names:
                    if alias.name in self.dangerous_imports:
                        risks.add({'severity': 'high', 'description': f'Dangerous import: {alias.name}'})

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Name) and node.func.id in self.critical_functions:
                    risks.add({'severity': 'medium', 'description': f'Critical function call: {node.func.id}'})

        analyzer = RiskAnalyzer()
        analyzer.visit(tree)
        return risks

    def _verify_ast_integrity(self, original: ast.AST, modified: ast.AST) -> bool:
        """Verify that AST modifications preserve integrity"""
        try:
            # Basic check - both should be compilable
            compile(original, '<original>', 'exec')
            compile(modified, '<modified>', 'exec')
            return True
        except:
            return False

    def _is_critical_file(self, file_path: str) -> bool:
        """Check if file is critical (system files, etc.)"""
        critical_patterns = [
            '__init__.py',
            'setup.py',
            'conftest.py',
            '/etc/',
            '/usr/',
            '/bin/',
            '/sbin/'
        ]

        return any(pattern in file_path for pattern in critical_patterns)

    def _scan_dangerous_patterns(self, content: str) -> List[str]:
        """Scan content for dangerous patterns"""
        dangerous_patterns = []

        # Check for eval/exec usage
        if 'eval(' in content:
            dangerous_patterns.append('eval() usage detected')
        if 'exec(' in content:
            dangerous_patterns.append('exec() usage detected')

        # Check for subprocess usage
        if 'subprocess' in content:
            dangerous_patterns.append('subprocess usage detected')

        # Check for file system operations
        if any(pattern in content for pattern in ['os.remove', 'os.rmdir', 'shutil.rmtree']):
            dangerous_patterns.append('File deletion operations detected')

        return dangerous_patterns

    def _analyze_node_security(self, node: ast.AST) -> List[Dict[str, str]]:
        """Analyze individual AST node for security risks"""
        risks = []

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.critical_functions:
                risks.append({
                    'severity': 'medium',
                    'description': f'Critical function call: {node.func.id}'
                })

        if isinstance(node, ast.Attribute):
            if node.attr in self.sensitive_attributes:
                risks.append({
                    'severity': 'high',
                    'description': f'Access to sensitive attribute: {node.attr}'
                })

        return risks


class InjectionAuditLogger:
    """Audit logging for injection operations"""

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
        self.entries: List[InjectionAuditEntry] = []

    def log_injection_attempt(self, file_path: str, patterns: List[str],
                            security_level: str, success: bool,
                            errors: List[str], user_context: Dict[str, Any] = None):
        """Log injection operation attempt"""
        from datetime import datetime

        entry = InjectionAuditEntry(
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            patterns_applied=patterns.copy(),
            security_level=security_level,
            user_context=user_context or {},
            success=success,
            errors=errors.copy()
        )

        self.entries.append(entry)

        # Write to log file if configured
        if self.log_file:
            self._write_log_entry(entry)

    def _write_log_entry(self, entry: InjectionAuditEntry):
        """Write audit entry to log file"""
        try:
            import json
            with open(self.log_file, 'a', encoding='utf-8') as f:
                log_data = {
                    'timestamp': entry.timestamp,
                    'file_path': entry.file_path,
                    'patterns': entry.patterns_applied,
                    'security_level': entry.security_level,
                    'success': entry.success,
                    'errors': entry.errors
                }
                f.write(json.dumps(log_data) + '\n')
        except Exception:
            # Silent fail for logging - don't break injection operations
            pass

    def get_recent_entries(self, count: int = 10) -> List[InjectionAuditEntry]:
        """Get recent audit entries"""
        return self.entries[-count:]

    def get_failed_injections(self) -> List[InjectionAuditEntry]:
        """Get entries for failed injections"""
        return [entry for entry in self.entries if not entry.success]