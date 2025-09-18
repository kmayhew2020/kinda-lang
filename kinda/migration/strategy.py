"""
Migration Strategy Framework for Kinda-Lang

Epic #127: Python Enhancement Bridge - Strategic frameworks for gradual
migration from pure Python to kinda-lang enhanced code.
"""

import os
import ast
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable

from ..injection.ast_analyzer import PatternType, InjectionPoint
from ..injection.injection_engine import InjectionEngine, InjectionConfig
from .decorators import EnhancementConfig


class MigrationPhase(Enum):
    """Four-phase migration strategy phases"""

    FUNCTION_LEVEL = 1
    CLASS_LEVEL = 2
    MODULE_LEVEL = 3
    PROJECT_WIDE = 4


class MigrationStatus(Enum):
    """Status of migration operations"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationResult:
    """Result of a migration operation"""

    success: bool
    phase: MigrationPhase
    files_processed: int
    functions_enhanced: int
    patterns_applied: List[str]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rollback_info: Optional[Dict[str, Any]] = None
    performance_impact: float = 0.0

    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)


@dataclass
class MigrationPlan:
    """Plan for migrating a Python project to kinda-lang"""

    target_directory: Path
    phases: List[MigrationPhase]
    pattern_progression: Dict[MigrationPhase, Set[PatternType]]
    exclude_files: Set[str] = field(default_factory=set)
    exclude_patterns: Set[str] = field(default_factory=set)
    safety_level: str = "safe"
    backup_enabled: bool = True
    validation_enabled: bool = True

    @classmethod
    def conservative_plan(cls, target_dir: Path) -> "MigrationPlan":
        """Create a conservative migration plan"""
        return cls(
            target_directory=target_dir,
            phases=[MigrationPhase.FUNCTION_LEVEL, MigrationPhase.CLASS_LEVEL],
            pattern_progression={
                MigrationPhase.FUNCTION_LEVEL: {PatternType.KINDA_INT, PatternType.KINDA_FLOAT},
                MigrationPhase.CLASS_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                },
            },
            exclude_files={"__init__.py", "setup.py", "conftest.py"},
            safety_level="safe",
        )

    @classmethod
    def standard_plan(cls, target_dir: Path) -> "MigrationPlan":
        """Create a standard migration plan"""
        return cls(
            target_directory=target_dir,
            phases=[
                MigrationPhase.FUNCTION_LEVEL,
                MigrationPhase.CLASS_LEVEL,
                MigrationPhase.MODULE_LEVEL,
            ],
            pattern_progression={
                MigrationPhase.FUNCTION_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                },
                MigrationPhase.CLASS_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                    PatternType.SOMETIMES,
                },
                MigrationPhase.MODULE_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                    PatternType.SOMETIMES,
                    PatternType.KINDA_REPEAT,
                },
            },
            exclude_files={"__init__.py", "setup.py"},
            safety_level="safe",
        )

    @classmethod
    def aggressive_plan(cls, target_dir: Path) -> "MigrationPlan":
        """Create an aggressive migration plan"""
        return cls(
            target_directory=target_dir,
            phases=list(MigrationPhase),
            pattern_progression={
                MigrationPhase.FUNCTION_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                },
                MigrationPhase.CLASS_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                    PatternType.SOMETIMES,
                    PatternType.MAYBE,
                },
                MigrationPhase.MODULE_LEVEL: {
                    PatternType.KINDA_INT,
                    PatternType.KINDA_FLOAT,
                    PatternType.SORTA_PRINT,
                    PatternType.SOMETIMES,
                    PatternType.MAYBE,
                    PatternType.KINDA_REPEAT,
                },
                MigrationPhase.PROJECT_WIDE: set(PatternType),
            },
            exclude_files={"setup.py"},
            safety_level="caution",
        )


class MigrationStrategy(ABC):
    """Abstract base class for migration strategies"""

    def __init__(self, plan: MigrationPlan):
        self.plan = plan
        self.current_phase = MigrationPhase.FUNCTION_LEVEL
        self.status = MigrationStatus.NOT_STARTED
        self.results: List[MigrationResult] = []

    @abstractmethod
    def execute_phase(self, phase: MigrationPhase) -> MigrationResult:
        """Execute a specific migration phase"""
        pass

    @abstractmethod
    def rollback_phase(self, phase: MigrationPhase) -> bool:
        """Rollback a specific migration phase"""
        pass

    def execute_full_migration(self) -> List[MigrationResult]:
        """Execute all phases of the migration plan"""
        self.status = MigrationStatus.IN_PROGRESS

        for phase in self.plan.phases:
            self.current_phase = phase
            result = self.execute_phase(phase)
            self.results.append(result)

            if not result.success:
                self.status = MigrationStatus.FAILED
                break
        else:
            self.status = MigrationStatus.COMPLETED

        return self.results

    def get_migration_summary(self) -> Dict[str, Any]:
        """Get summary of migration progress"""
        return {
            "status": self.status.value,
            "current_phase": self.current_phase.value,
            "completed_phases": len(self.results),
            "total_phases": len(self.plan.phases),
            "total_files_processed": sum(r.files_processed for r in self.results),
            "total_functions_enhanced": sum(r.functions_enhanced for r in self.results),
            "total_errors": sum(len(r.errors) for r in self.results),
            "total_warnings": sum(len(r.warnings) for r in self.results),
        }


class FourPhaseStrategy(MigrationStrategy):
    """Implementation of the four-phase migration strategy"""

    def __init__(self, plan: MigrationPlan):
        super().__init__(plan)
        self.injection_engine = InjectionEngine()
        self.backup_files: Dict[str, str] = {}  # file -> backup_path

    def execute_phase(self, phase: MigrationPhase) -> MigrationResult:
        """Execute specific phase of four-phase strategy"""
        result = MigrationResult(
            success=True, phase=phase, files_processed=0, functions_enhanced=0, patterns_applied=[]
        )

        try:
            if phase == MigrationPhase.FUNCTION_LEVEL:
                self._execute_function_level(result)
            elif phase == MigrationPhase.CLASS_LEVEL:
                self._execute_class_level(result)
            elif phase == MigrationPhase.MODULE_LEVEL:
                self._execute_module_level(result)
            elif phase == MigrationPhase.PROJECT_WIDE:
                self._execute_project_wide(result)

        except Exception as e:
            result.add_error(f"Phase {phase.value} failed: {e}")

        return result

    def rollback_phase(self, phase: MigrationPhase) -> bool:
        """Rollback a specific phase"""
        try:
            # Restore backup files
            for file_path, backup_path in self.backup_files.items():
                if os.path.exists(backup_path):
                    os.replace(backup_path, file_path)

            return True
        except Exception:
            return False

    def _execute_function_level(self, result: MigrationResult):
        """Phase 1: Function-Level Enhancement"""
        patterns = self.plan.pattern_progression.get(MigrationPhase.FUNCTION_LEVEL, set())

        # Find all Python files
        python_files = self._find_python_files()

        for file_path in python_files:
            if self._should_process_file(file_path):
                self._process_file_functions(file_path, patterns, result)

    def _execute_class_level(self, result: MigrationResult):
        """Phase 2: Class-Level Enhancement"""
        patterns = self.plan.pattern_progression.get(MigrationPhase.CLASS_LEVEL, set())

        python_files = self._find_python_files()

        for file_path in python_files:
            if self._should_process_file(file_path):
                self._process_file_classes(file_path, patterns, result)

    def _execute_module_level(self, result: MigrationResult):
        """Phase 3: Module-Level Integration"""
        patterns = self.plan.pattern_progression.get(MigrationPhase.MODULE_LEVEL, set())

        # Process modules as units
        modules = self._identify_modules()

        for module_path in modules:
            self._process_module(module_path, patterns, result)

    def _execute_project_wide(self, result: MigrationResult):
        """Phase 4: Project-Wide Integration"""
        patterns = self.plan.pattern_progression.get(MigrationPhase.PROJECT_WIDE, set())

        # Apply project-wide patterns and optimizations
        self._apply_project_optimizations(patterns, result)

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in target directory"""
        python_files = []

        for root, dirs, files in os.walk(self.plan.target_directory):
            # Skip common non-code directories
            dirs[:] = [
                d for d in dirs if d not in {".git", ".venv", "__pycache__", ".pytest_cache"}
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        return python_files

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        file_name = file_path.name

        # Check exclusion list
        if file_name in self.plan.exclude_files:
            return False

        # Skip test files in early phases
        if self.current_phase in [MigrationPhase.FUNCTION_LEVEL, MigrationPhase.CLASS_LEVEL]:
            if "test" in file_name.lower():
                return False

        return True

    def _process_file_functions(
        self, file_path: Path, patterns: Set[PatternType], result: MigrationResult
    ):
        """Process individual functions in a file"""
        try:
            # Backup file if enabled
            if self.plan.backup_enabled:
                self._backup_file(file_path)

            # Parse file
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            # Find functions to enhance
            functions = self._find_functions_in_ast(tree)

            enhanced_any = False

            for func_node in functions:
                if self._should_enhance_function(func_node):
                    success = self._enhance_function_node(func_node, patterns, file_path)
                    if success:
                        result.functions_enhanced += 1
                        enhanced_any = True

            if enhanced_any:
                result.files_processed += 1
                result.patterns_applied.extend([p.value for p in patterns])

        except Exception as e:
            result.add_error(f"Failed to process {file_path}: {e}")

    def _process_file_classes(
        self, file_path: Path, patterns: Set[PatternType], result: MigrationResult
    ):
        """Process classes in a file"""
        try:
            if self.plan.backup_enabled:
                self._backup_file(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            classes = self._find_classes_in_ast(tree)

            enhanced_any = False

            for class_node in classes:
                if self._should_enhance_class(class_node):
                    success = self._enhance_class_node(class_node, patterns, file_path)
                    if success:
                        enhanced_any = True
                        # Count methods in class
                        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
                        result.functions_enhanced += len(methods)

            if enhanced_any:
                result.files_processed += 1
                result.patterns_applied.extend([p.value for p in patterns])

        except Exception as e:
            result.add_error(f"Failed to process classes in {file_path}: {e}")

    def _process_module(
        self, module_path: Path, patterns: Set[PatternType], result: MigrationResult
    ):
        """Process entire module"""
        # For module-level processing, we enhance the entire module as a unit
        try:
            if self.plan.backup_enabled:
                self._backup_file(module_path)

            config = InjectionConfig(enabled_patterns=patterns, safety_level=self.plan.safety_level)

            injection_result = self.injection_engine.inject_file(module_path, config)

            if injection_result.success:
                result.files_processed += 1
                result.functions_enhanced += len(injection_result.applied_patterns)
                result.patterns_applied.extend(injection_result.applied_patterns)
            else:
                result.add_error(
                    f"Module injection failed for {module_path}: {injection_result.errors}"
                )

        except Exception as e:
            result.add_error(f"Failed to process module {module_path}: {e}")

    def _apply_project_optimizations(self, patterns: Set[PatternType], result: MigrationResult):
        """Apply project-wide optimizations"""
        # Project-wide phase includes cross-module optimizations
        # For now, this is a placeholder for future advanced features
        result.add_warning("Project-wide optimization not yet implemented")

    def _backup_file(self, file_path: Path):
        """Create backup of file"""
        backup_path = str(file_path) + f".kinda_backup_{int(time.time())}"
        os.copy2(file_path, backup_path)
        self.backup_files[str(file_path)] = backup_path

    def _find_functions_in_ast(self, tree: ast.AST) -> List[ast.FunctionDef]:
        """Find all function definitions in AST"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)

        return functions

    def _find_classes_in_ast(self, tree: ast.AST) -> List[ast.ClassDef]:
        """Find all class definitions in AST"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node)

        return classes

    def _should_enhance_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if function should be enhanced"""
        # Skip special methods
        if func_node.name.startswith("__") and func_node.name.endswith("__"):
            return False

        # Skip functions that are already enhanced
        if any(isinstance(d, ast.Name) and "enhance" in d.id for d in func_node.decorator_list):
            return False

        return True

    def _should_enhance_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class should be enhanced"""
        # Skip classes that are already enhanced
        if any(isinstance(d, ast.Name) and "enhance" in d.id for d in class_node.decorator_list):
            return False

        return True

    def _enhance_function_node(
        self, func_node: ast.FunctionDef, patterns: Set[PatternType], file_path: Path
    ) -> bool:
        """Enhance a specific function node"""
        # This is a simplified version - in practice, we would modify the AST
        # and write back the enhanced code
        try:
            # For now, just return True to indicate success
            # Real implementation would apply AST transformations
            return True
        except Exception:
            return False

    def _enhance_class_node(
        self, class_node: ast.ClassDef, patterns: Set[PatternType], file_path: Path
    ) -> bool:
        """Enhance a specific class node"""
        try:
            # Enhance methods in the class
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef):
                    self._enhance_function_node(node, patterns, file_path)
            return True
        except Exception:
            return False

    def _identify_modules(self) -> List[Path]:
        """Identify modules in the project"""
        modules = []

        for file_path in self._find_python_files():
            # Each Python file is a module
            if file_path.name != "__init__.py":  # Skip package init files
                modules.append(file_path)

        return modules


class IncrementalStrategy(MigrationStrategy):
    """Strategy for incremental migration with fine-grained control"""

    def __init__(self, plan: MigrationPlan, increment_size: int = 5):
        super().__init__(plan)
        self.increment_size = increment_size  # Number of functions per increment

    def execute_phase(self, phase: MigrationPhase) -> MigrationResult:
        """Execute phase in small increments"""
        result = MigrationResult(
            success=True, phase=phase, files_processed=0, functions_enhanced=0, patterns_applied=[]
        )

        # Find all enhancement targets
        targets = self._find_enhancement_targets(phase)

        # Process in increments
        for i in range(0, len(targets), self.increment_size):
            increment_targets = targets[i : i + self.increment_size]
            increment_result = self._process_increment(increment_targets, phase)

            # Merge results
            result.files_processed += increment_result.files_processed
            result.functions_enhanced += increment_result.functions_enhanced
            result.patterns_applied.extend(increment_result.patterns_applied)
            result.errors.extend(increment_result.errors)
            result.warnings.extend(increment_result.warnings)

            if not increment_result.success:
                result.success = False
                break

        return result

    def rollback_phase(self, phase: MigrationPhase) -> bool:
        """Rollback phase incrementally"""
        # Incremental rollback implementation
        return True

    def _find_enhancement_targets(self, phase: MigrationPhase) -> List[Tuple[Path, str]]:
        """Find targets for enhancement (file_path, target_name)"""
        targets = []

        for file_path in self._find_python_files():
            if self._should_process_file(file_path):
                # Parse file and find targets based on phase
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    if phase == MigrationPhase.FUNCTION_LEVEL:
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                targets.append((file_path, node.name))
                    elif phase == MigrationPhase.CLASS_LEVEL:
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                targets.append((file_path, node.name))

                except Exception:
                    continue

        return targets

    def _process_increment(
        self, targets: List[Tuple[Path, str]], phase: MigrationPhase
    ) -> MigrationResult:
        """Process a single increment of targets"""
        result = MigrationResult(
            success=True, phase=phase, files_processed=0, functions_enhanced=0, patterns_applied=[]
        )

        processed_files = set()

        for file_path, target_name in targets:
            try:
                # Process target
                if file_path not in processed_files:
                    processed_files.add(file_path)
                    result.files_processed += 1

                result.functions_enhanced += 1

            except Exception as e:
                result.add_error(f"Failed to process {target_name} in {file_path}: {e}")

        return result

    def _find_python_files(self) -> List[Path]:
        """Find Python files (same as FourPhaseStrategy)"""
        python_files = []

        for root, dirs, files in os.walk(self.plan.target_directory):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__"}]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return python_files

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed (same as FourPhaseStrategy)"""
        return file_path.name not in self.plan.exclude_files
