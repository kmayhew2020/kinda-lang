import subprocess
import shutil
from pathlib import Path
import pytest
import sys

# ✅ Rename imported function to avoid name conflict
from kinda.langs.python.runtime_gen import generate_runtime as generate_runtime_code

# Import kinda meta-testing framework
sys.path.insert(0, str(Path(__file__).parent.parent))
from kinda_test_framework import KindaTestFramework
from kinda.personality import (
    PersonalityContext,
    get_personality,
    chaos_probability,
    chaos_random,
    chaos_uniform,
    chaos_randint,
)

SRC_DIRS = ["tests/python/input", "tests"]
BUILD_DIR = Path("build/python")
RUNTIME_OUT = Path("kinda/langs/python/runtime")


def safe_emoji_print(text):
    """Print text with emoji fallbacks for Windows compatibility."""
    # Emoji fallback mapping for Windows encoding issues
    emoji_fallbacks = {
        "🎯": "[TARGET]",
        "🎲": "[DICE]",
        "🎆": "[SPARKLE]",
        "🎭": "[MASKS]",
        "✨": "[STAR]",
        "🏆": "[TROPHY]",
        "📈": "[CHART]",
        "📚": "[BOOKS]",
        "🌪️": "[TORNADO]",
        "⚙️": "[GEAR]",
        "🌀": "[SPIRAL]",
    }

    try:
        print(text)
    except UnicodeEncodeError:
        # Replace emojis with text alternatives
        safe_text = text
        for emoji, fallback in emoji_fallbacks.items():
            safe_text = safe_text.replace(emoji, fallback)
        print(safe_text)


# Global meta-testing framework for ~kinda test environment configuration
GLOBAL_KINDA_FRAMEWORK = None


def generate_runtime():
    # Clean old runtime
    if RUNTIME_OUT.exists():
        shutil.rmtree(RUNTIME_OUT)
    RUNTIME_OUT.mkdir(parents=True, exist_ok=True)

    # Run Python runtime generation directly
    generate_runtime_code(RUNTIME_OUT)


@pytest.fixture(scope="session", autouse=True)
def setup_kinda_test_environment():
    """~maybe setup different test personalities and configurations using kinda constructs."""
    global GLOBAL_KINDA_FRAMEWORK

    # ~maybe use different personality for test session
    test_personalities = ["reliable", "playful", "cautious", "chaotic"]
    if chaos_random() < 0.7:  # ~maybe 70% chance to use non-default personality
        selected_personality = test_personalities[chaos_randint(0, len(test_personalities) - 1)]
    else:
        selected_personality = "playful"  # Default

    # ~sometimes vary chaos levels during testing
    if chaos_random() < chaos_probability("sometimes"):
        chaos_level = chaos_randint(3, 8)  # ~kinda_int chaos level
    else:
        chaos_level = 5  # Default

    # ~rarely use unseeded randomness (for true chaos testing)
    if chaos_random() < chaos_probability("rarely"):
        test_seed = None  # Unseeded chaos!
        safe_emoji_print(f"[CONFTEST] 🎲 ~rarely using unseeded chaos for test session!")
    else:
        test_seed = 42  # Reproducible by default

    safe_emoji_print(f"[CONFTEST] 🎆 Setting up kinda test environment:")
    print(f"   Personality: {selected_personality}")
    print(f"   Chaos Level: {chaos_level}/10")
    print(f"   Seed: {test_seed}")

    # Initialize global personality context
    PersonalityContext._instance = PersonalityContext(selected_personality, chaos_level, test_seed)

    # Create global kinda testing framework for meta-operations
    GLOBAL_KINDA_FRAMEWORK = KindaTestFramework(selected_personality, chaos_level, test_seed)

    # ~sorta run additional test setup based on personality
    personality = get_personality()
    if personality.mood == "chaotic":
        safe_emoji_print(
            f"[CONFTEST] 🌀 Chaotic personality detected - expect unpredictable test behavior!"
        )
    elif personality.mood == "reliable":
        safe_emoji_print(
            f"[CONFTEST] ⚙️ Reliable personality detected - prioritizing deterministic behavior"
        )
    elif personality.mood == "playful":
        safe_emoji_print(
            f"[CONFTEST] 🎭 Playful personality detected - balanced chaos and reliability"
        )

    # Yield to actual build regeneration
    yield from regenerate_build()

    # ~sorta cleanup session data
    if chaos_random() < chaos_probability("sorta_print"):
        if GLOBAL_KINDA_FRAMEWORK:
            session_report = {
                "personality": selected_personality,
                "chaos_level": chaos_level,
                "seed": test_seed,
                "total_tests_run": GLOBAL_KINDA_FRAMEWORK.total_tests_run,
            }
            print(f"[CONFTEST] 📋 Session Summary: {session_report}")
    else:
        print(f"[CONFTEST] ~sorta skipping session cleanup summary")


def regenerate_build():
    # Step 1: Regenerate runtime
    generate_runtime()

    # Step 2: Clean and recreate build/ folder
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Step 3: Run transformer on all .knda files in each src dir
    for src_dir in SRC_DIRS:
        # Only use Python language since C support is disabled in v0.3.0
        lang = "python"
        result = subprocess.run(
            [
                "python3",
                "-m",
                "kinda",
                "transform",
                src_dir,
                "--out",
                str(BUILD_DIR),
                "--lang",
                lang,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Transformer failed:")
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            # ~maybe we continue despite transformer failure (chaos tolerance)
            if chaos_random() < chaos_probability("rarely"):
                print("[CONFTEST] ~rarely continuing despite transformer failure (chaos tolerance)")
            else:
                raise RuntimeError("Transformer failed during test setup")

    yield  # Make this a generator function - yield after all build is complete


# Additional kinda-based pytest fixtures and hooks for meta-programming test patterns
# This will be appended to conftest.py


@pytest.fixture
def kinda_test_personality():
    """Fixture that provides ~maybe different personality per test using kinda constructs."""
    # Save current personality context
    original_context = PersonalityContext._instance

    try:
        # ~maybe use a different personality for this specific test
        if chaos_random() < chaos_probability("maybe"):
            test_personalities = ["reliable", "playful", "cautious", "chaotic"]
            selected = test_personalities[chaos_randint(0, len(test_personalities) - 1)]
            chaos_level = chaos_randint(2, 8)  # ~kinda_int chaos level
            test_seed = chaos_randint(1, 10000) if chaos_random() < 0.8 else None  # ~maybe unseeded

            PersonalityContext._instance = PersonalityContext(selected, chaos_level, test_seed)
            print(
                f"[FIXTURE] ~maybe using test personality: {selected} (chaos: {chaos_level}, seed: {test_seed})"
            )
        else:
            print(
                f"[FIXTURE] ~maybe keeping session personality: {original_context.mood if original_context else 'default'}"
            )

        yield PersonalityContext.get_instance()

    finally:
        # Restore original personality context
        PersonalityContext._instance = original_context


@pytest.fixture
def fuzzy_test_timeout():
    """Fixture that provides ~kinda_float test timeouts using chaos functions."""
    base_timeout = 5.0

    # Use personality-based fuzzy timeout
    personality = get_personality()
    if personality.mood == "reliable":
        timeout = base_timeout * chaos_uniform(0.8, 1.2)  # Small variance for reliable
    elif personality.mood == "chaotic":
        timeout = base_timeout * chaos_uniform(0.3, 3.0)  # Large variance for chaotic
    else:
        timeout = base_timeout * chaos_uniform(0.5, 2.0)  # Medium variance for playful/cautious

    print(f"[FIXTURE] Using ~kinda_float timeout: {timeout:.2f}s (personality: {personality.mood})")
    return timeout


@pytest.fixture
def sorta_test_cleanup():
    """Fixture that provides ~sorta cleanup patterns with probabilistic execution."""
    cleanup_actions = []
    cleanup_probability = chaos_probability("sorta_print")

    def register_cleanup(action, description="cleanup action"):
        """Register a cleanup action that will ~sorta be executed."""
        cleanup_actions.append((action, description))

    def sorta_cleanup_function():
        """Execute registered cleanup actions with ~sorta probability."""
        executed = 0
        skipped = 0

        for action, description in cleanup_actions:
            if chaos_random() < cleanup_probability:
                try:
                    action()
                    executed += 1
                    print(f"[CLEANUP] ✅ ~sorta executed: {description}")
                except Exception as e:
                    print(f"[CLEANUP] ❌ ~sorta cleanup failed: {description} - {e}")
            else:
                skipped += 1
                print(f"[CLEANUP] ⏭️ ~sorta skipped: {description}")

        print(
            f"[CLEANUP] Summary: {executed} executed, {skipped} skipped (~sorta rate: {cleanup_probability:.1%})"
        )

    # Return the registration function
    yield register_cleanup

    # Execute cleanup at fixture teardown
    sorta_cleanup_function()


@pytest.fixture
def meta_test_framework():
    """Fixture that provides access to the global meta-testing framework."""
    global GLOBAL_KINDA_FRAMEWORK

    if GLOBAL_KINDA_FRAMEWORK is None:
        # Create a default framework if none exists
        GLOBAL_KINDA_FRAMEWORK = KindaTestFramework("playful", 5, 42)

    return GLOBAL_KINDA_FRAMEWORK


@pytest.fixture
def assert_probability_validator():
    """Fixture providing meta-probability validation using kinda constructs."""

    def validate_probability_meta(
        event_func, expected_prob=None, tolerance=None, samples=None, description="event"
    ):
        """Validate event probability using fuzzy parameters."""
        from kinda_test_framework import assert_probability_meta

        # Use fuzzy defaults if not provided
        if expected_prob is None:
            expected_prob = chaos_uniform(0.3, 0.7)  # ~kinda_float probability
        if tolerance is None:
            tolerance = chaos_uniform(0.05, 0.2)  # ~kinda_float tolerance
        if samples is None:
            samples = chaos_randint(50, 200)  # ~kinda_int samples

        return assert_probability_meta(event_func, expected_prob, tolerance, samples, description)

    return validate_probability_meta


@pytest.fixture
def assert_eventually_validator():
    """Fixture providing meta-eventual validation using kinda constructs."""

    def validate_eventually_meta(
        condition_func, timeout=None, confidence=None, description="condition"
    ):
        """Validate eventual condition using fuzzy parameters."""
        from kinda_test_framework import assert_eventually_meta

        # Use fuzzy defaults if not provided
        if timeout is None:
            timeout = chaos_uniform(1.0, 5.0)  # ~kinda_float timeout
        if confidence is None:
            confidence = chaos_uniform(0.6, 0.9)  # ~kinda_float confidence

        return assert_eventually_meta(condition_func, timeout, confidence, description)

    return validate_eventually_meta


def pytest_runtest_setup(item):
    """Hook that runs ~maybe different setup for each test using kinda constructs."""
    # ~sometimes we print extra test information
    if chaos_random() < chaos_probability("sometimes"):
        personality = get_personality()
        safe_emoji_print(
            f"\n[PYTEST] 🎲 Running {item.name} with {personality.mood} personality (chaos: {personality.chaos_level})"
        )

    # ~rarely we might skip a test entirely (controlled chaos!)
    if chaos_random() < chaos_probability("rarely") * 0.1:  # Very rare, just 1.5% chance typically
        safe_emoji_print(f"[PYTEST] 🎭 ~rarely skipping test {item.name} due to chaos factor!")
        pytest.skip("~rarely skipped due to chaos factor")


def pytest_runtest_teardown(item):
    """Hook that runs ~sorta cleanup after each test."""
    # ~sorta print test completion information
    if chaos_random() < chaos_probability("sorta_print"):
        personality = get_personality()
        safe_emoji_print(
            f"[PYTEST] ✨ ~sorta completed {item.name} (personality: {personality.mood})"
        )

        # ~maybe update instability based on test outcome
        if hasattr(item, "_skipped") and item._skipped:
            personality.update_instability(failed=True)  # Skipped = kind of failed
        elif hasattr(item, "_failed") and item._failed:
            personality.update_instability(failed=True)  # Actually failed
        else:
            personality.update_instability(failed=False)  # Probably succeeded


def pytest_sessionfinish(session, exitstatus):
    """Session-level hook that provides final ~kinda meta-analysis."""
    global GLOBAL_KINDA_FRAMEWORK

    # ~sometimes we print a comprehensive session report
    if chaos_random() < chaos_probability("sometimes"):
        personality = get_personality()
        safe_emoji_print(f"\n🎯 KINDA TEST SESSION FINAL REPORT")
        print(f"=" * 50)
        print(f"Session Personality: {personality.mood}")
        print(f"Chaos Level: {personality.chaos_level}/10")
        print(f"Seed: {personality.seed}")
        print(f"Exit Status: {exitstatus}")

        # Meta-framework statistics
        if GLOBAL_KINDA_FRAMEWORK:
            framework_score = GLOBAL_KINDA_FRAMEWORK.calculate_meta_score()
            print(f"Meta-Framework 'Kinda Tests Kinda' Score: {framework_score:.1%}")

            if framework_score > 0.8:
                safe_emoji_print("🏆 EXCELLENT: Meta-programming philosophy achieved!")
            elif framework_score > 0.6:
                safe_emoji_print("✨ GOOD: Strong meta-programming patterns")
            elif framework_score > 0.4:
                safe_emoji_print("📈 MODERATE: Some meta-programming present")
            else:
                safe_emoji_print("📚 BASIC: Limited meta-programming patterns")

        # Personality-based exit messages
        if personality.mood == "chaotic":
            safe_emoji_print("🌪️ Chaotic testing session complete - embrace the uncertainty!")
        elif personality.mood == "reliable":
            safe_emoji_print("⚙️ Reliable testing session complete - predictable outcomes achieved")
        else:
            safe_emoji_print("🎭 Playful testing session complete - balanced chaos and order")
    else:
        print(f"[SESSION] ~sorta skipping detailed session report")
