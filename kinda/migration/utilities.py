"""
Migration Utilities for Kinda-Lang

Epic #127: Python Enhancement Bridge - Utility functions and tools for
managing incremental migration from Python to kinda-lang enhanced code.
"""

import ast
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

from ..injection.ast_analyzer import PatternType, InjectionPoint
from ..injection.injection_engine import InjectionEngine, InjectionConfig
from .strategy import MigrationPlan, MigrationResult, MigrationPhase


@dataclass
class MigrationReport:
    """Comprehensive migration report"""
    timestamp: str
    project_path: str
    migration_plan: Dict[str, Any]
    results_by_phase: Dict[int, Dict[str, Any]]
    summary: Dict[str, Any]
    recommendations: List[str]
    rollback_instructions: List[str]

    def save_to_file(self, output_path: Path):
        """Save report to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'MigrationReport':
        """Load report from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class CodeAnalysis:
    """Analysis of code complexity and migration readiness"""
    file_path: str
    function_count: int
    class_count: int
    complexity_score: int
    injection_opportunities: List[Dict[str, Any]]
    risks: List[str]
    recommendations: List[str]
    estimated_enhancement_impact: float


class MigrationUtilities:
    """Utility class for migration operations"""

    def __init__(self):
        self.injection_engine = InjectionEngine()

    def analyze_project_readiness(self, project_path: Path,
                                exclude_patterns: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Analyze project readiness for kinda-lang migration.

        Args:
            project_path: Path to the Python project
            exclude_patterns: File patterns to exclude from analysis

        Returns:
            Dictionary with analysis results and recommendations
        """
        exclude_patterns = exclude_patterns or {'.git', '.venv', '__pycache__', '*.pyc'}

        analysis = {
            'project_path': str(project_path),
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': 0,
            'total_functions': 0,
            'total_classes': 0,
            'complexity_distribution': {},
            'injection_opportunities': [],
            'risk_assessment': {},
            'recommendations': [],
            'estimated_migration_effort': 'unknown'
        }

        python_files = self._find_python_files(project_path, exclude_patterns)

        for file_path in python_files:
            file_analysis = self.analyze_file(file_path)
            if file_analysis:
                analysis['files_analyzed'] += 1
                analysis['total_functions'] += file_analysis.function_count
                analysis['total_classes'] += file_analysis.class_count
                analysis['injection_opportunities'].extend(file_analysis.injection_opportunities)

        # Calculate complexity distribution
        analysis['complexity_distribution'] = self._calculate_complexity_distribution(python_files)

        # Generate risk assessment
        analysis['risk_assessment'] = self._assess_migration_risks(analysis)

        # Generate recommendations
        analysis['recommendations'] = self._generate_readiness_recommendations(analysis)

        # Estimate migration effort
        analysis['estimated_migration_effort'] = self._estimate_migration_effort(analysis)

        return analysis

    def analyze_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """
        Analyze a single Python file for migration readiness.

        Args:
            file_path: Path to Python file

        Returns:
            CodeAnalysis object or None if analysis fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            # Count functions and classes
            function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

            # Calculate complexity
            complexity = self._calculate_complexity(tree)

            # Find injection opportunities
            injection_points = self.injection_engine.analyzer.find_injection_points(tree)
            opportunities = [
                {
                    'pattern': point.pattern_type.value,
                    'location': f"line {point.location.line}",
                    'confidence': point.confidence,
                    'safety_level': point.safety_level.value
                }
                for point in injection_points
            ]

            # Identify risks
            risks = self._identify_file_risks(tree, source)

            # Generate recommendations
            recommendations = self._generate_file_recommendations(
                function_count, class_count, complexity, opportunities, risks
            )

            # Estimate impact
            impact = self._estimate_enhancement_impact(opportunities)

            return CodeAnalysis(
                file_path=str(file_path),
                function_count=function_count,
                class_count=class_count,
                complexity_score=complexity,
                injection_opportunities=opportunities,
                risks=risks,
                recommendations=recommendations,
                estimated_enhancement_impact=impact
            )

        except Exception as e:
            print(f"Failed to analyze {file_path}: {e}")
            return None

    def create_migration_backup(self, project_path: Path, backup_name: Optional[str] = None) -> Path:
        """
        Create a complete backup of the project before migration.

        Args:
            project_path: Path to the project to backup
            backup_name: Optional name for backup directory

        Returns:
            Path to the backup directory
        """
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"kinda_migration_backup_{timestamp}"

        backup_path = project_path.parent / backup_name

        # Create backup
        shutil.copytree(project_path, backup_path, ignore=shutil.ignore_patterns(
            '.git', '.venv', '__pycache__', '*.pyc', '.pytest_cache'
        ))

        # Create backup metadata
        metadata = {
            'backup_timestamp': datetime.now().isoformat(),
            'original_path': str(project_path),
            'backup_path': str(backup_path),
            'kinda_lang_version': '0.5.5-dev',  # Should get from actual version
            'purpose': 'Pre-migration backup'
        }

        with open(backup_path / '.kinda_backup_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        return backup_path

    def restore_from_backup(self, backup_path: Path, target_path: Optional[Path] = None) -> bool:
        """
        Restore project from backup.

        Args:
            backup_path: Path to backup directory
            target_path: Target restoration path (uses original if None)

        Returns:
            True if restoration successful
        """
        try:
            # Read backup metadata
            metadata_file = backup_path / '.kinda_backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                original_path = Path(metadata['original_path'])
            else:
                if target_path is None:
                    raise ValueError("No metadata found and no target path specified")
                original_path = target_path

            restore_path = target_path or original_path

            # Remove existing directory if it exists
            if restore_path.exists():
                shutil.rmtree(restore_path)

            # Copy backup to target location
            shutil.copytree(backup_path, restore_path, ignore=shutil.ignore_patterns(
                '.kinda_backup_metadata.json'
            ))

            return True

        except Exception as e:
            print(f"Failed to restore from backup: {e}")
            return False

    def generate_migration_report(self, migration_plan: MigrationPlan,
                                results: List[MigrationResult]) -> MigrationReport:
        """
        Generate comprehensive migration report.

        Args:
            migration_plan: The migration plan that was executed
            results: Results from each migration phase

        Returns:
            MigrationReport object
        """
        # Convert results by phase
        results_by_phase = {}
        for result in results:
            phase_num = result.phase.value
            results_by_phase[phase_num] = {
                'success': result.success,
                'files_processed': result.files_processed,
                'functions_enhanced': result.functions_enhanced,
                'patterns_applied': result.patterns_applied,
                'errors': result.errors,
                'warnings': result.warnings,
                'performance_impact': result.performance_impact
            }

        # Calculate summary
        summary = {
            'total_phases_completed': len([r for r in results if r.success]),
            'total_phases_planned': len(migration_plan.phases),
            'total_files_processed': sum(r.files_processed for r in results),
            'total_functions_enhanced': sum(r.functions_enhanced for r in results),
            'total_errors': sum(len(r.errors) for r in results),
            'total_warnings': sum(len(r.warnings) for r in results),
            'overall_success': all(r.success for r in results),
            'estimated_performance_impact': max((r.performance_impact for r in results), default=0.0)
        }

        # Generate recommendations
        recommendations = self._generate_migration_recommendations(results, summary)

        # Generate rollback instructions
        rollback_instructions = self._generate_rollback_instructions(migration_plan, results)

        return MigrationReport(
            timestamp=datetime.now().isoformat(),
            project_path=str(migration_plan.target_directory),
            migration_plan=asdict(migration_plan),
            results_by_phase=results_by_phase,
            summary=summary,
            recommendations=recommendations,
            rollback_instructions=rollback_instructions
        )

    def validate_enhanced_code(self, file_path: Path,
                             original_backup: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate enhanced code against original version.

        Args:
            file_path: Path to enhanced file
            original_backup: Path to original file backup

        Returns:
            Validation results
        """
        validation = {
            'file_path': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'syntax_valid': False,
            'imports_preserved': False,
            'function_signatures_preserved': False,
            'enhancement_markers_present': False,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }

        try:
            # Check syntax validity
            with open(file_path, 'r', encoding='utf-8') as f:
                enhanced_source = f.read()

            try:
                ast.parse(enhanced_source)
                validation['syntax_valid'] = True
            except SyntaxError as e:
                validation['errors'].append(f"Syntax error: {e}")

            # Check for enhancement markers
            if 'kinda' in enhanced_source or '@enhance' in enhanced_source:
                validation['enhancement_markers_present'] = True

            # Compare with original if available
            if original_backup and original_backup.exists():
                with open(original_backup, 'r', encoding='utf-8') as f:
                    original_source = f.read()

                comparison = self._compare_code_versions(original_source, enhanced_source)
                validation.update(comparison)

        except Exception as e:
            validation['errors'].append(f"Validation failed: {e}")

        return validation

    def _find_python_files(self, project_path: Path, exclude_patterns: Set[str]) -> List[Path]:
        """Find all Python files in project"""
        python_files = []

        for file_path in project_path.rglob('*.py'):
            # Check exclusion patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            python_files.append(file_path)

        return python_files

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of AST"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)

        return complexity

    def _calculate_complexity_distribution(self, files: List[Path]) -> Dict[str, int]:
        """Calculate complexity distribution across files"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
                complexity = self._calculate_complexity(tree)

                if complexity <= 5:
                    distribution['low'] += 1
                elif complexity <= 15:
                    distribution['medium'] += 1
                elif complexity <= 30:
                    distribution['high'] += 1
                else:
                    distribution['very_high'] += 1

            except Exception:
                continue

        return distribution

    def _assess_migration_risks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess migration risks based on analysis"""
        risks = {
            'overall_risk': 'low',
            'specific_risks': [],
            'mitigation_strategies': []
        }

        # Check complexity distribution
        complexity_dist = analysis['complexity_distribution']
        high_complexity_files = complexity_dist.get('high', 0) + complexity_dist.get('very_high', 0)

        if high_complexity_files > analysis['files_analyzed'] * 0.3:
            risks['overall_risk'] = 'high'
            risks['specific_risks'].append('High proportion of complex files')
            risks['mitigation_strategies'].append('Consider manual review of complex files')

        # Check injection opportunities
        opportunities = analysis['injection_opportunities']
        risky_opportunities = [o for o in opportunities if o.get('safety_level') in ['risky', 'dangerous']]

        if len(risky_opportunities) > 10:
            risks['overall_risk'] = 'medium' if risks['overall_risk'] == 'low' else 'high'
            risks['specific_risks'].append('Many risky injection opportunities detected')
            risks['mitigation_strategies'].append('Use conservative migration plan')

        return risks

    def _generate_readiness_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on readiness analysis"""
        recommendations = []

        # File count recommendations
        if analysis['files_analyzed'] > 100:
            recommendations.append("Large project detected - consider incremental migration strategy")
        elif analysis['files_analyzed'] < 5:
            recommendations.append("Small project - suitable for aggressive migration")

        # Complexity recommendations
        complexity_dist = analysis['complexity_distribution']
        if complexity_dist.get('very_high', 0) > 0:
            recommendations.append("Very high complexity files found - manual review recommended")

        # Opportunity recommendations
        opportunities = analysis['injection_opportunities']
        if len(opportunities) < 10:
            recommendations.append("Limited injection opportunities - migration impact may be minimal")
        elif len(opportunities) > 100:
            recommendations.append("Many injection opportunities - significant enhancement potential")

        return recommendations

    def _estimate_migration_effort(self, analysis: Dict[str, Any]) -> str:
        """Estimate migration effort based on analysis"""
        score = 0

        # File count factor
        file_count = analysis['files_analyzed']
        if file_count > 100:
            score += 3
        elif file_count > 20:
            score += 2
        else:
            score += 1

        # Complexity factor
        complexity_dist = analysis['complexity_distribution']
        score += complexity_dist.get('high', 0) + complexity_dist.get('very_high', 0) * 2

        # Opportunity factor
        opportunities = len(analysis['injection_opportunities'])
        if opportunities > 100:
            score += 2
        elif opportunities > 50:
            score += 1

        # Convert score to effort estimate
        if score <= 3:
            return "low (1-2 days)"
        elif score <= 7:
            return "medium (3-7 days)"
        elif score <= 12:
            return "high (1-2 weeks)"
        else:
            return "very high (2+ weeks)"

    def _identify_file_risks(self, tree: ast.AST, source: str) -> List[str]:
        """Identify risks in a specific file"""
        risks = []

        # Check for dangerous imports
        dangerous_imports = {'os', 'subprocess', 'sys', 'eval', 'exec'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        risks.append(f"Dangerous import: {alias.name}")

        # Check for eval/exec usage
        if 'eval(' in source or 'exec(' in source:
            risks.append("Dynamic code execution detected")

        # Check for file operations
        if any(op in source for op in ['open(', 'file(', 'write(', 'read(']):
            risks.append("File operations detected")

        return risks

    def _generate_file_recommendations(self, function_count: int, class_count: int,
                                     complexity: int, opportunities: List[Dict[str, Any]],
                                     risks: List[str]) -> List[str]:
        """Generate recommendations for a specific file"""
        recommendations = []

        if complexity > 20:
            recommendations.append("High complexity - consider refactoring before enhancement")

        if len(risks) > 0:
            recommendations.append("Security risks detected - use conservative enhancement")

        if len(opportunities) == 0:
            recommendations.append("No enhancement opportunities found")
        elif len(opportunities) > 20:
            recommendations.append("Many enhancement opportunities - good candidate for migration")

        return recommendations

    def _estimate_enhancement_impact(self, opportunities: List[Dict[str, Any]]) -> float:
        """Estimate performance impact of enhancements"""
        base_impact = 2.0  # Base overhead percentage
        per_opportunity_impact = 0.5  # Additional impact per opportunity

        total_impact = base_impact + (len(opportunities) * per_opportunity_impact)

        # Adjust for opportunity types
        for opp in opportunities:
            if opp.get('pattern') in ['kinda_repeat', 'sometimes']:
                total_impact += 1.0  # Higher impact patterns

        return min(total_impact, 25.0)  # Cap at 25%

    def _generate_migration_recommendations(self, results: List[MigrationResult],
                                          summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on migration results"""
        recommendations = []

        if not summary['overall_success']:
            recommendations.append("Migration incomplete - review errors and retry failed phases")

        if summary['total_errors'] > 0:
            recommendations.append("Errors detected - manual review recommended")

        if summary['estimated_performance_impact'] > 15:
            recommendations.append("High performance impact - consider reducing enhancement scope")

        if summary['total_functions_enhanced'] == 0:
            recommendations.append("No functions enhanced - review migration configuration")

        return recommendations

    def _generate_rollback_instructions(self, migration_plan: MigrationPlan,
                                      results: List[MigrationResult]) -> List[str]:
        """Generate rollback instructions"""
        instructions = []

        if migration_plan.backup_enabled:
            instructions.append("1. Locate backup files created before migration")
            instructions.append("2. Use MigrationUtilities.restore_from_backup() to restore")
        else:
            instructions.append("1. Backup was not enabled - manual rollback required")
            instructions.append("2. Remove @enhance decorators from enhanced functions")
            instructions.append("3. Remove kinda imports added during migration")

        instructions.append("3. Run tests to verify rollback success")
        instructions.append("4. Consider creating backup before next migration attempt")

        return instructions

    def _compare_code_versions(self, original: str, enhanced: str) -> Dict[str, Any]:
        """Compare original and enhanced code versions"""
        comparison = {
            'imports_preserved': True,
            'function_signatures_preserved': True,
            'additional_checks': []
        }

        try:
            original_tree = ast.parse(original)
            enhanced_tree = ast.parse(enhanced)

            # Check imports
            original_imports = {node.names[0].name for node in ast.walk(original_tree)
                              if isinstance(node, ast.Import)}
            enhanced_imports = {node.names[0].name for node in ast.walk(enhanced_tree)
                              if isinstance(node, ast.Import)}

            if not original_imports.issubset(enhanced_imports):
                comparison['imports_preserved'] = False

            # Check function signatures (simplified check)
            original_functions = {node.name for node in ast.walk(original_tree)
                                if isinstance(node, ast.FunctionDef)}
            enhanced_functions = {node.name for node in ast.walk(enhanced_tree)
                                if isinstance(node, ast.FunctionDef)}

            if not original_functions.issubset(enhanced_functions):
                comparison['function_signatures_preserved'] = False

        except Exception as e:
            comparison['additional_checks'].append(f"Comparison failed: {e}")

        return comparison