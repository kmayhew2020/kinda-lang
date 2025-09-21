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
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "MigrationReport":
        """Load report from JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class CodeAnalysis:
    """Analysis of code complexity and migration readiness"""

    file_path: str
    function_count: int
    class_count: int
    method_count: int
    complexity_score: int
    injection_opportunities: List[InjectionPoint]
    risks: List[str]
    recommendations: List[str]
    estimated_enhancement_impact: float
    has_syntax_errors: bool = False


@dataclass
class DirectoryAnalysis:
    """Analysis of a directory of Python files"""

    directory_path: str
    timestamp: str
    files_analyzed: int
    total_files: int
    total_functions: int
    total_classes: int
    total_methods: int
    total_opportunities: int
    total_injection_opportunities: int
    file_analyses: List[CodeAnalysis]
    summary: Dict[str, Any]


class MigrationUtilities:
    """Utility class for migration operations"""

    def __init__(self):
        self.injection_engine = InjectionEngine()

    def analyze_project_readiness(
        self, project_path: Path, exclude_patterns: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze project readiness for kinda-lang migration.

        Args:
            project_path: Path to the Python project
            exclude_patterns: File patterns to exclude from analysis

        Returns:
            Dictionary with analysis results and recommendations
        """
        exclude_patterns = exclude_patterns or {".git", ".venv", "__pycache__", "*.pyc"}

        analysis = {
            "project_path": str(project_path),
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": 0,
            "total_functions": 0,
            "total_classes": 0,
            "complexity_distribution": {},
            "injection_opportunities": [],
            "risk_assessment": {},
            "recommendations": [],
            "estimated_migration_effort": "unknown",
        }

        python_files = self._find_python_files(project_path, exclude_patterns)

        for file_path in python_files:
            file_analysis = self.analyze_file(file_path)
            if file_analysis:
                analysis["files_analyzed"] += 1
                analysis["total_functions"] += file_analysis.function_count
                analysis["total_classes"] += file_analysis.class_count
                analysis["injection_opportunities"].extend(file_analysis.injection_opportunities)

        # Calculate complexity distribution
        analysis["complexity_distribution"] = self._calculate_complexity_distribution(python_files)

        # Generate risk assessment
        analysis["risk_assessment"] = self._assess_migration_risks(analysis)

        # Generate recommendations
        analysis["recommendations"] = self._generate_readiness_recommendations(analysis)

        # Estimate migration effort
        analysis["estimated_migration_effort"] = self._estimate_migration_effort(analysis)

        return analysis

    def analyze_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """
        Analyze a single Python file for migration readiness.

        Args:
            file_path: Path to Python file

        Returns:
            CodeAnalysis object or None if analysis fails

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read due to permissions
            UnicodeDecodeError: If file contains non-text data
            ValueError: If file contains null bytes or other invalid content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            # Count functions, classes, and methods
            function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

            # Count methods (functions inside classes)
            method_count = 0
            for class_node in ast.walk(tree):
                if isinstance(class_node, ast.ClassDef):
                    for node in class_node.body:
                        if isinstance(node, ast.FunctionDef):
                            method_count += 1

            # Calculate complexity
            complexity = self._calculate_complexity(tree)

            # Find injection opportunities
            injection_points = self.injection_engine.analyzer.find_injection_points(tree)
            opportunities = injection_points  # Return actual InjectionPoint objects

            # Identify risks
            risks = self._identify_file_risks(tree, source)

            # Generate recommendations
            recommendations = self._generate_file_recommendations(
                function_count, class_count, method_count, complexity, opportunities, risks
            )

            # Estimate impact
            impact = self._estimate_enhancement_impact(opportunities)

            return CodeAnalysis(
                file_path=str(file_path),
                function_count=function_count,
                class_count=class_count,
                method_count=method_count,
                complexity_score=complexity,
                injection_opportunities=opportunities,
                risks=risks,
                recommendations=recommendations,
                estimated_enhancement_impact=impact,
            )

        except FileNotFoundError:
            # Re-raise FileNotFoundError as expected by tests
            raise
        except PermissionError:
            # Re-raise PermissionError as expected by tests
            raise
        except UnicodeDecodeError:
            # Re-raise UnicodeDecodeError for binary files as expected by tests
            raise
        except ValueError as e:
            # Re-raise ValueError for files with null bytes as expected by tests
            if "null bytes" in str(e).lower():
                raise
            # For other ValueError cases (like syntax errors), return None
            print(f"Failed to analyze {file_path}: {e}")
            return None
        except SyntaxError:
            # For syntax errors, return CodeAnalysis with has_syntax_errors=True
            print(f"Failed to analyze {file_path}: Syntax error")
            return CodeAnalysis(
                file_path=str(file_path),
                function_count=0,
                class_count=0,
                method_count=0,
                complexity_score=0,
                injection_opportunities=[],
                risks=["Syntax error in file"],
                recommendations=["Fix syntax errors before migration"],
                estimated_enhancement_impact=0.0,
                has_syntax_errors=True,
            )
        except Exception as e:
            print(f"Failed to analyze {file_path}: {e}")
            return None

    def analyze_directory(
        self,
        directory_path: Path,
        recursive: bool = False,
        exclude_patterns: Optional[Set[str]] = None,
    ) -> DirectoryAnalysis:
        """
        Analyze all Python files in a directory.

        Args:
            directory_path: Path to directory to analyze
            recursive: Whether to search recursively
            exclude_patterns: File patterns to exclude

        Returns:
            DirectoryAnalysis object with aggregated analysis results
        """
        exclude_patterns = exclude_patterns or {".git", ".venv", "__pycache__", "*.pyc"}

        if recursive:
            python_files = list(directory_path.rglob("*.py"))
        else:
            python_files = list(directory_path.glob("*.py"))

        # Filter out excluded patterns
        python_files = [
            f for f in python_files if not any(pattern in str(f) for pattern in exclude_patterns)
        ]

        file_analyses = []
        files_analyzed = 0
        total_functions = 0
        total_classes = 0
        total_methods = 0
        total_opportunities = 0

        for file_path in python_files:
            file_analysis = self.analyze_file(file_path)
            if file_analysis:
                files_analyzed += 1
                total_functions += file_analysis.function_count
                total_classes += file_analysis.class_count
                total_methods += file_analysis.method_count
                total_opportunities += len(file_analysis.injection_opportunities)
                file_analyses.append(file_analysis)

        # Generate summary
        summary = {
            "avg_complexity": sum(fa.complexity_score for fa in file_analyses)
            / max(len(file_analyses), 1),
            "files_with_opportunities": len(
                [fa for fa in file_analyses if fa.injection_opportunities]
            ),
            "files_with_risks": len([fa for fa in file_analyses if fa.risks]),
        }

        return DirectoryAnalysis(
            directory_path=str(directory_path),
            timestamp=datetime.now().isoformat(),
            files_analyzed=files_analyzed,
            total_files=len(python_files),
            total_functions=total_functions,
            total_classes=total_classes,
            total_methods=total_methods,
            total_opportunities=total_opportunities,
            total_injection_opportunities=total_opportunities,  # Same as total_opportunities
            file_analyses=file_analyses,
            summary=summary,
        )

    def suggest_enhancement_patterns(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Suggest enhancement patterns for a file based on analysis.

        Args:
            file_path: Path to Python file

        Returns:
            List of suggested enhancement patterns
        """
        analysis = self.analyze_file(file_path)
        if not analysis:
            return []

        suggestions = []

        for injection_point in analysis.injection_opportunities:
            suggestion = {
                "pattern_type": injection_point.pattern_type.value,
                "location": f"line {injection_point.location.line}",
                "confidence": injection_point.confidence,
                "safety_level": injection_point.safety_level.value,
                "suggested_replacement": self._generate_pattern_suggestion(injection_point),
                "impact_estimate": (
                    "low"
                    if injection_point.confidence < 0.7
                    else "medium" if injection_point.confidence < 0.9 else "high"
                ),
            }
            suggestions.append(suggestion)

        return suggestions

    def estimate_enhancement_impact(
        self, file_path: Path, patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Estimate the impact of applying enhancement patterns to a file.

        Args:
            file_path: Path to Python file
            patterns: Optional list of specific patterns to consider

        Returns:
            Dictionary with impact estimates
        """
        analysis = self.analyze_file(file_path)
        if not analysis:
            return {"error": "Failed to analyze file"}

        opportunities = analysis.injection_opportunities
        if patterns:
            opportunities = [op for op in opportunities if op.pattern_type.value in patterns]

        return {
            "file_path": str(file_path),
            "total_opportunities": len(opportunities),
            "performance_impact_estimate": self._estimate_enhancement_impact(opportunities),
            "safety_assessment": self._assess_enhancement_safety(opportunities),
            "complexity_change": self._estimate_complexity_change(opportunities),
            "recommended_approach": self._recommend_enhancement_approach(analysis),
        }

    def generate_enhancement_preview(
        self, file_path: Path, patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a preview of what the enhanced code would look like.

        Args:
            file_path: Path to Python file
            patterns: Optional list of specific patterns to apply

        Returns:
            Dictionary with preview information
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_source = f.read()

            # Create an injection config
            from ..injection.ast_analyzer import PatternType

            enabled_patterns = set()
            if patterns:
                for pattern in patterns:
                    try:
                        enabled_patterns.add(PatternType(pattern))
                    except ValueError:
                        pass  # Skip invalid pattern types
            else:
                # Default patterns
                enabled_patterns = {PatternType.SOMETIMES, PatternType.MAYBE, PatternType.RARELY}

            config = InjectionConfig(
                enabled_patterns=enabled_patterns,
                safety_level="safe",
                preserve_comments=True,
                add_kinda_imports=True,
            )

            # Use injection engine to transform the code
            result = self.injection_engine.inject_source(original_source, config)

            preview = {
                "file_path": str(file_path),
                "original_lines": len(original_source.splitlines()),
                "enhanced_lines": (
                    len(result.transformed_code.splitlines()) if result.success else 0
                ),
                "patterns_applied": result.applied_patterns if result.success else [],
                "enhancement_successful": result.success,
                "preview_snippet": self._generate_preview_snippet(
                    original_source,
                    result.transformed_code if result.success else original_source,
                ),
                "warnings": result.warnings if hasattr(result, "warnings") else [],
            }

            return preview

        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": f"Failed to generate preview: {e}",
                "enhancement_successful": False,
            }

    def validate_enhancement_safety(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate the safety of applying enhancements to a file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with safety validation results
        """
        analysis = self.analyze_file(file_path)
        if not analysis:
            return {"error": "Failed to analyze file", "safe": False}

        safety_report = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "overall_safety": "safe",
            "risk_factors": [],
            "recommendations": [],
            "safe_patterns": [],
            "risky_patterns": [],
        }

        for opportunity in analysis.injection_opportunities:
            if opportunity.safety_level.value in ["safe", "caution"]:
                safety_report["safe_patterns"].append(
                    {
                        "pattern": opportunity.pattern_type.value,
                        "location": f"line {opportunity.location.line}",
                        "safety_level": opportunity.safety_level.value,
                    }
                )
            else:
                safety_report["risky_patterns"].append(
                    {
                        "pattern": opportunity.pattern_type.value,
                        "location": f"line {opportunity.location.line}",
                        "safety_level": opportunity.safety_level.value,
                    }
                )
                safety_report["overall_safety"] = "risky"

        # Add risk factors from file analysis
        if analysis.risks:
            safety_report["risk_factors"].extend(analysis.risks)
            if safety_report["overall_safety"] == "safe":
                safety_report["overall_safety"] = "caution"

        # Generate recommendations
        if safety_report["risky_patterns"]:
            safety_report["recommendations"].append(
                "Review risky patterns manually before applying"
            )
        if analysis.complexity_score > 20:
            safety_report["recommendations"].append(
                "High complexity file - consider refactoring first"
            )

        return safety_report

    def get_migration_statistics(self, project_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive migration statistics for a project.

        Args:
            project_path: Path to project

        Returns:
            Dictionary with migration statistics
        """
        directory_analysis = self.analyze_directory(project_path, recursive=True)

        stats = {
            "project_path": str(project_path),
            "timestamp": datetime.now().isoformat(),
            "file_count": directory_analysis.files_analyzed,
            "files_analyzed": directory_analysis.files_analyzed,  # Add this for test compatibility
            "function_count": directory_analysis.total_functions,
            "class_count": directory_analysis.total_classes,
            "method_count": directory_analysis.total_methods,
            "enhancement_opportunities": directory_analysis.total_opportunities,
            "pattern_distribution": {},
            "complexity_distribution": {},
            "safety_distribution": {},
            "readiness_score": 0.0,
        }

        # Calculate pattern distribution
        all_opportunities = []
        for fa in directory_analysis.file_analyses:
            all_opportunities.extend(fa.injection_opportunities)

        pattern_counts = {}
        safety_counts = {"safe": 0, "caution": 0, "risky": 0, "dangerous": 0}

        for opp in all_opportunities:
            pattern_type = opp.pattern_type.value
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
            safety_counts[opp.safety_level.value] = safety_counts.get(opp.safety_level.value, 0) + 1

        stats["pattern_distribution"] = pattern_counts
        stats["safety_distribution"] = safety_counts

        # Calculate complexity distribution
        complexities = [fa.complexity_score for fa in directory_analysis.file_analyses]
        stats["complexity_distribution"] = {
            "low": len([c for c in complexities if c <= 5]),
            "medium": len([c for c in complexities if 5 < c <= 15]),
            "high": len([c for c in complexities if 15 < c <= 30]),
            "very_high": len([c for c in complexities if c > 30]),
        }

        # Calculate readiness score (0-100)
        readiness_factors = [
            min(
                stats["enhancement_opportunities"] / max(stats["file_count"], 1) * 10, 30
            ),  # Opportunity density
            min(safety_counts["safe"] / max(len(all_opportunities), 1) * 40, 40),  # Safety ratio
            max(0, 30 - stats["complexity_distribution"]["very_high"] * 5),  # Complexity penalty
        ]
        stats["readiness_score"] = sum(readiness_factors)

        return stats

    def create_migration_backup(
        self,
        project_path: Path,
        backup_name: Optional[str] = None,
        backup_suffix: Optional[str] = None,
    ) -> Path:
        """
        Create a complete backup of the project before migration.

        Args:
            project_path: Path to the project to backup
            backup_name: Optional name for backup directory
            backup_suffix: Optional suffix to add to backup name

        Returns:
            Path to the backup directory
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"kinda_migration_backup_{timestamp}"
            if backup_suffix:
                base_name += backup_suffix
            backup_name = base_name

        backup_path = project_path.parent / backup_name

        # Create backup - handle both files and directories
        if project_path.is_file():
            # For single files, create a backup file directly
            backup_file_path = backup_path.with_suffix(project_path.suffix)
            shutil.copy2(project_path, backup_file_path)
            actual_backup_path = backup_file_path
        else:
            # For directories, copy the entire directory tree
            shutil.copytree(
                project_path,
                backup_path,
                ignore=shutil.ignore_patterns(
                    ".git", ".venv", "__pycache__", "*.pyc", ".pytest_cache"
                ),
            )
            actual_backup_path = backup_path

        # Create backup metadata (only for directories)
        if actual_backup_path.is_dir():
            metadata = {
                "backup_timestamp": datetime.now().isoformat(),
                "original_path": str(project_path),
                "backup_path": str(actual_backup_path),
                "kinda_lang_version": "0.5.5-dev",  # Should get from actual version
                "purpose": "Pre-migration backup",
            }

            with open(actual_backup_path / ".kinda_backup_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

        return actual_backup_path

    def restore_from_backup(self, target_path: Path, backup_path: Path) -> bool:
        """
        Restore project from backup.

        Args:
            target_path: Target restoration path where backup should be restored
            backup_path: Path to backup file or directory

        Returns:
            True if restoration successful
        """
        try:
            if backup_path.is_file():
                # Restoring a single file
                # Remove existing file if it exists
                if target_path.exists():
                    target_path.unlink()

                # Copy backup file to target location
                shutil.copy2(backup_path, target_path)

            else:
                # Restoring a directory
                # Remove existing directory if it exists
                if target_path.exists():
                    shutil.rmtree(target_path)

                # Copy backup to target location
                shutil.copytree(
                    backup_path,
                    target_path,
                    ignore=shutil.ignore_patterns(".kinda_backup_metadata.json"),
                )

            return True

        except Exception as e:
            print(f"Failed to restore from backup: {e}")
            return False

    def generate_migration_report(
        self, migration_plan: MigrationPlan, results: List[MigrationResult]
    ) -> MigrationReport:
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
                "success": result.success,
                "files_processed": result.files_processed,
                "functions_enhanced": result.functions_enhanced,
                "patterns_applied": result.patterns_applied,
                "errors": result.errors,
                "warnings": result.warnings,
                "performance_impact": result.performance_impact,
            }

        # Calculate summary
        summary = {
            "total_phases_completed": len([r for r in results if r.success]),
            "total_phases_planned": len(migration_plan.phases),
            "total_files_processed": sum(r.files_processed for r in results),
            "total_functions_enhanced": sum(r.functions_enhanced for r in results),
            "total_errors": sum(len(r.errors) for r in results),
            "total_warnings": sum(len(r.warnings) for r in results),
            "overall_success": all(r.success for r in results),
            "estimated_performance_impact": max(
                (r.performance_impact for r in results), default=0.0
            ),
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
            rollback_instructions=rollback_instructions,
        )

    def validate_enhanced_code(
        self, file_path: Path, original_backup: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Validate enhanced code against original version.

        Args:
            file_path: Path to enhanced file
            original_backup: Path to original file backup

        Returns:
            Validation results
        """
        validation = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "syntax_valid": False,
            "imports_preserved": False,
            "function_signatures_preserved": False,
            "enhancement_markers_present": False,
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }

        try:
            # Check syntax validity
            with open(file_path, "r", encoding="utf-8") as f:
                enhanced_source = f.read()

            try:
                ast.parse(enhanced_source)
                validation["syntax_valid"] = True
            except SyntaxError as e:
                validation["errors"].append(f"Syntax error: {e}")

            # Check for enhancement markers
            if "kinda" in enhanced_source or "@enhance" in enhanced_source:
                validation["enhancement_markers_present"] = True

            # Compare with original if available
            if original_backup and original_backup.exists():
                with open(original_backup, "r", encoding="utf-8") as f:
                    original_source = f.read()

                comparison = self._compare_code_versions(original_source, enhanced_source)
                validation.update(comparison)

        except Exception as e:
            validation["errors"].append(f"Validation failed: {e}")

        return validation

    def _find_python_files(self, project_path: Path, exclude_patterns: Set[str]) -> List[Path]:
        """Find all Python files in project"""
        python_files = []

        for file_path in project_path.rglob("*.py"):
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
        distribution = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)
                complexity = self._calculate_complexity(tree)

                if complexity <= 5:
                    distribution["low"] += 1
                elif complexity <= 15:
                    distribution["medium"] += 1
                elif complexity <= 30:
                    distribution["high"] += 1
                else:
                    distribution["very_high"] += 1

            except Exception:
                continue

        return distribution

    def _assess_migration_risks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess migration risks based on analysis"""
        risks = {"overall_risk": "low", "specific_risks": [], "mitigation_strategies": []}

        # Check complexity distribution
        complexity_dist = analysis["complexity_distribution"]
        high_complexity_files = complexity_dist.get("high", 0) + complexity_dist.get("very_high", 0)

        if high_complexity_files > analysis["files_analyzed"] * 0.3:
            risks["overall_risk"] = "high"
            risks["specific_risks"].append("High proportion of complex files")
            risks["mitigation_strategies"].append("Consider manual review of complex files")

        # Check injection opportunities
        opportunities = analysis["injection_opportunities"]
        risky_opportunities = [
            o for o in opportunities if o.safety_level.value in ["risky", "dangerous"]
        ]

        if len(risky_opportunities) > 10:
            risks["overall_risk"] = "medium" if risks["overall_risk"] == "low" else "high"
            risks["specific_risks"].append("Many risky injection opportunities detected")
            risks["mitigation_strategies"].append("Use conservative migration plan")

        return risks

    def _generate_readiness_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on readiness analysis"""
        recommendations = []

        # File count recommendations
        if analysis["files_analyzed"] > 100:
            recommendations.append(
                "Large project detected - consider incremental migration strategy"
            )
        elif analysis["files_analyzed"] < 5:
            recommendations.append("Small project - suitable for aggressive migration")

        # Complexity recommendations
        complexity_dist = analysis["complexity_distribution"]
        if complexity_dist.get("very_high", 0) > 0:
            recommendations.append("Very high complexity files found - manual review recommended")

        # Opportunity recommendations
        opportunities = analysis["injection_opportunities"]
        if len(opportunities) < 10:
            recommendations.append(
                "Limited injection opportunities - migration impact may be minimal"
            )
        elif len(opportunities) > 100:
            recommendations.append(
                "Many injection opportunities - significant enhancement potential"
            )

        return recommendations

    def _estimate_migration_effort(self, analysis: Dict[str, Any]) -> str:
        """Estimate migration effort based on analysis"""
        score = 0

        # File count factor
        file_count = analysis["files_analyzed"]
        if file_count > 100:
            score += 3
        elif file_count > 20:
            score += 2
        else:
            score += 1

        # Complexity factor
        complexity_dist = analysis["complexity_distribution"]
        score += complexity_dist.get("high", 0) + complexity_dist.get("very_high", 0) * 2

        # Opportunity factor
        opportunities = len(analysis["injection_opportunities"])
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
        dangerous_imports = {"os", "subprocess", "sys", "eval", "exec"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        risks.append(f"Dangerous import: {alias.name}")

        # Check for eval/exec usage
        if "eval(" in source or "exec(" in source:
            risks.append("Dynamic code execution detected")

        # Check for file operations
        if any(op in source for op in ["open(", "file(", "write(", "read("]):
            risks.append("File operations detected")

        return risks

    def _generate_file_recommendations(
        self,
        function_count: int,
        class_count: int,
        method_count: int,
        complexity: int,
        opportunities: List[InjectionPoint],
        risks: List[str],
    ) -> List[str]:
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
            if opp.pattern_type.value in ["kinda_repeat", "sometimes"]:
                total_impact += 1.0  # Higher impact patterns

        return min(total_impact, 25.0)  # Cap at 25%

    def _generate_migration_recommendations(
        self, results: List[MigrationResult], summary: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on migration results"""
        recommendations = []

        if not summary["overall_success"]:
            recommendations.append("Migration incomplete - review errors and retry failed phases")

        if summary["total_errors"] > 0:
            recommendations.append("Errors detected - manual review recommended")

        if summary["estimated_performance_impact"] > 15:
            recommendations.append("High performance impact - consider reducing enhancement scope")

        if summary["total_functions_enhanced"] == 0:
            recommendations.append("No functions enhanced - review migration configuration")

        return recommendations

    def _generate_rollback_instructions(
        self, migration_plan: MigrationPlan, results: List[MigrationResult]
    ) -> List[str]:
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
            "imports_preserved": True,
            "function_signatures_preserved": True,
            "additional_checks": [],
        }

        try:
            original_tree = ast.parse(original)
            enhanced_tree = ast.parse(enhanced)

            # Check imports
            original_imports = {
                node.names[0].name
                for node in ast.walk(original_tree)
                if isinstance(node, ast.Import)
            }
            enhanced_imports = {
                node.names[0].name
                for node in ast.walk(enhanced_tree)
                if isinstance(node, ast.Import)
            }

            if not original_imports.issubset(enhanced_imports):
                comparison["imports_preserved"] = False

            # Check function signatures (simplified check)
            original_functions = {
                node.name for node in ast.walk(original_tree) if isinstance(node, ast.FunctionDef)
            }
            enhanced_functions = {
                node.name for node in ast.walk(enhanced_tree) if isinstance(node, ast.FunctionDef)
            }

            if not original_functions.issubset(enhanced_functions):
                comparison["function_signatures_preserved"] = False

        except Exception as e:
            comparison["additional_checks"].append(f"Comparison failed: {e}")

        return comparison

    def _generate_pattern_suggestion(self, injection_point: InjectionPoint) -> str:
        """Generate a suggested replacement for an injection point"""
        pattern_type = injection_point.pattern_type.value

        if pattern_type == "kinda_int":
            return f"kinda_int({injection_point.node.value})"
        elif pattern_type == "kinda_float":
            return f"kinda_float({injection_point.node.value})"
        elif pattern_type == "sorta_print":
            return f"sorta_print(...)"
        elif pattern_type in ["sometimes", "maybe", "rarely"]:
            return f"~{pattern_type} {{ ... }}"
        else:
            return f"# Apply {pattern_type} pattern here"

    def _assess_enhancement_safety(self, opportunities: List[InjectionPoint]) -> str:
        """Assess the safety of enhancement opportunities"""
        if not opportunities:
            return "safe"

        risk_levels = [op.safety_level.value for op in opportunities]
        if "dangerous" in risk_levels:
            return "dangerous"
        elif "risky" in risk_levels:
            return "risky"
        elif "caution" in risk_levels:
            return "caution"
        else:
            return "safe"

    def _estimate_complexity_change(self, opportunities: List[InjectionPoint]) -> Dict[str, Any]:
        """Estimate how complexity will change with enhancements"""
        return {
            "base_complexity_increase": len(opportunities) * 0.1,
            "pattern_complexity": {
                op.pattern_type.value: (
                    0.2 if op.pattern_type.value in ["kinda_repeat", "sometimes"] else 0.1
                )
                for op in opportunities
            },
            "overall_assessment": (
                "minimal"
                if len(opportunities) < 5
                else "moderate" if len(opportunities) < 15 else "significant"
            ),
        }

    def _recommend_enhancement_approach(self, analysis: CodeAnalysis) -> str:
        """Recommend an enhancement approach based on analysis"""
        if analysis.complexity_score > 25:
            return "conservative - refactor first"
        elif len(analysis.risks) > 3:
            return "careful - manual review recommended"
        elif len(analysis.injection_opportunities) > 20:
            return "aggressive - good enhancement candidate"
        else:
            return "standard - proceed with normal caution"

    def _generate_preview_snippet(self, original: str, enhanced: str) -> Dict[str, Any]:
        """Generate a preview snippet showing changes"""
        original_lines = original.splitlines()
        enhanced_lines = enhanced.splitlines()

        return {
            "original_excerpt": original_lines[:10],  # First 10 lines
            "enhanced_excerpt": enhanced_lines[:10],  # First 10 lines
            "changes_detected": len(original_lines) != len(enhanced_lines) or original != enhanced,
            "line_count_change": len(enhanced_lines) - len(original_lines),
        }
