#!/usr/bin/env python3
"""
Comprehensive Example Audit Script for Issue #96
Tests all .knda example files for transformation and execution success
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class AuditResult:
    file_path: str
    category: str  # python, probabilistic_control_flow, c, other
    transform_status: str  # pass, fail
    transform_error: str
    execution_status: str  # pass, fail, partial
    execution_error: str
    generated_python_valid: str  # pass, fail, n/a
    python_compile_error: str
    failure_type: str  # syntax_error, runtime_error, math_error, import_error, timeout, none
    severity: str  # critical, high, medium, low, none


def categorize_file(file_path: str) -> str:
    """Categorize example file by directory"""
    if "/python/" in file_path:
        return "python"
    elif "/probabilistic_control_flow/" in file_path:
        return "probabilistic_control_flow"
    elif "/c/" in file_path:
        return "c"
    else:
        return "other"


def determine_failure_type(transform_err: str, exec_err: str, compile_err: str) -> str:
    """Categorize the type of failure"""
    all_errors = f"{transform_err} {exec_err} {compile_err}".lower()

    if "syntaxerror" in all_errors or "invalid syntax" in all_errors:
        return "syntax_error"
    elif "importerror" in all_errors or "modulenotfounderror" in all_errors:
        return "import_error"
    elif "math domain error" in all_errors or "zerodivisionerror" in all_errors:
        return "math_error"
    elif "timeout" in all_errors or "timed out" in all_errors:
        return "timeout"
    elif "runtimeerror" in all_errors or "valueerror" in all_errors or "keyerror" in all_errors:
        return "runtime_error"
    elif "attributeerror" in all_errors:
        return "attribute_error"
    elif "nameerror" in all_errors:
        return "name_error"
    elif any(err for err in [transform_err, exec_err, compile_err] if err.strip()):
        return "other_error"
    else:
        return "none"


def determine_severity(failure_type: str, file_path: str) -> str:
    """Determine severity of failure based on type and file"""
    if failure_type == "none":
        return "none"

    # Syntax errors are critical - examples should compile
    if failure_type == "syntax_error":
        return "critical"

    # Import errors are high - examples should be runnable
    if failure_type == "import_error":
        return "high"

    # Math errors could be medium or high depending on context
    if failure_type == "math_error":
        return "high"

    # Runtime errors in comprehensive examples are medium
    if "/comprehensive/" in file_path and failure_type == "runtime_error":
        return "medium"

    # Runtime errors in individual examples are high
    if "/individual/" in file_path and failure_type == "runtime_error":
        return "high"

    # Other errors are medium by default
    return "medium"


def test_transform(file_path: str) -> Tuple[str, str]:
    """Test if file transforms successfully"""
    try:
        result = subprocess.run(
            ["kinda", "transform", file_path], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            return "pass", ""
        else:
            error = result.stderr.strip() or result.stdout.strip()
            return "fail", error

    except subprocess.TimeoutExpired:
        return "fail", "Transform timeout after 10s"
    except Exception as e:
        return "fail", str(e)


def test_execution(file_path: str) -> Tuple[str, str]:
    """Test if transformed file executes successfully"""
    try:
        # Use --seed 42 for reproducibility
        result = subprocess.run(
            ["kinda", "run", file_path, "--seed", "42"], capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0:
            return "pass", ""
        else:
            error = result.stderr.strip() or result.stdout.strip()
            # Check if it's a "soft" failure (probabilistic behavior) or hard failure
            if "syntaxerror" in error.lower() or "error:" in error.lower():
                return "fail", error
            else:
                # Non-zero return but no explicit error might be probabilistic
                return "partial", error

    except subprocess.TimeoutExpired:
        return "fail", "Execution timeout after 15s"
    except Exception as e:
        return "fail", str(e)


def test_python_compile(file_path: str) -> Tuple[str, str]:
    """Test if generated Python compiles"""
    # Determine generated Python file path
    build_path = Path("/home/testuser/kinda-lang/build")

    # Extract relative path and construct build file path
    rel_path = Path(file_path).relative_to("/home/testuser/kinda-lang/examples")

    # Generated files use .py extension
    if file_path.endswith(".py.knda"):
        generated = build_path / rel_path.with_suffix("")
    elif file_path.endswith(".c.knda"):
        # C files generate .c not .py
        return "n/a", "C file - not Python"
    elif file_path.endswith(".knda"):
        generated = build_path / (str(rel_path) + ".py")
    else:
        return "n/a", "Unknown file type"

    if not generated.exists():
        return "fail", f"Generated file not found: {generated}"

    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(generated)],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return "pass", ""
        else:
            error = result.stderr.strip() or result.stdout.strip()
            return "fail", error

    except subprocess.TimeoutExpired:
        return "fail", "Compile check timeout"
    except Exception as e:
        return "fail", str(e)


def audit_file(file_path: str) -> AuditResult:
    """Run complete audit on a single file"""
    print(f"  Testing: {Path(file_path).name}", end="", flush=True)

    category = categorize_file(file_path)

    # Test transformation
    transform_status, transform_error = test_transform(file_path)
    print(".", end="", flush=True)

    # Test execution
    execution_status, execution_error = test_execution(file_path)
    print(".", end="", flush=True)

    # Test Python compilation
    python_valid, python_error = test_python_compile(file_path)
    print(".", end="", flush=True)

    # Determine failure type and severity
    failure_type = determine_failure_type(transform_error, execution_error, python_error)
    severity = determine_severity(failure_type, file_path)

    status_icon = "✓" if failure_type == "none" else "✗"
    print(f" {status_icon}")

    return AuditResult(
        file_path=file_path,
        category=category,
        transform_status=transform_status,
        transform_error=transform_error,
        execution_status=execution_status,
        execution_error=execution_error,
        generated_python_valid=python_valid,
        python_compile_error=python_error,
        failure_type=failure_type,
        severity=severity,
    )


def main():
    """Run audit on all example files"""
    # Find all .knda files
    examples_dir = Path("/home/testuser/kinda-lang/examples")
    knda_files = sorted(examples_dir.rglob("*.knda"))

    print(f"Found {len(knda_files)} example files to audit\n")

    results = []

    # Test each file
    for file_path in knda_files:
        result = audit_file(str(file_path))
        results.append(result)

    # Save results as JSON
    output_file = "/home/testuser/kinda-lang/audit_results.json"
    with open(output_file, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\n✓ Audit complete! Results saved to: {output_file}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.failure_type == "none")
    failed = total - passed

    print(f"\nSummary:")
    print(f"  Total: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    # Failure breakdown
    if failed > 0:
        print(f"\nFailure Types:")
        failure_counts = {}
        for r in results:
            if r.failure_type != "none":
                failure_counts[r.failure_type] = failure_counts.get(r.failure_type, 0) + 1

        for ftype, count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ftype}: {count}")

        # Severity breakdown
        print(f"\nSeverity Breakdown:")
        severity_counts = {}
        for r in results:
            if r.severity != "none":
                severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

        for sev, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sev}: {count}")


if __name__ == "__main__":
    main()
