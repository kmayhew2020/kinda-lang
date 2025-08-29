# kinda/grammar/constructs.py

import re

KindaPythonConstructs = {
    "kinda_int": {
        "type": "declaration",
        "pattern": re.compile(r'~kinda int (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)'),
        "description": "Fuzzy integer declaration with noise",
        "body": (
            "def kinda_int(val):\n"
            "    \"\"\"Fuzzy integer with graceful error handling\"\"\"\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            "                print(f\"[?] kinda int got something weird: {repr(val)}\")\n"
            "                print(f\"[tip] Expected a number but got {type(val).__name__}\")\n"
            "                return random.randint(0, 10)\n"
            "        fuzz = random.randint(-1, 1)\n"
            "        return int(val + fuzz)\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Kinda int got kinda confused: {e}\")\n"
            "        print(f\"[tip] Just picking a random number instead\")\n"
            "        return random.randint(0, 10)"
        ),
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r'~sorta print\s*\((.*)\)\s*(?:;|$)'),
        "description": "Print with ~70% probability",
        "body": (
            "def sorta_print(*args):\n"
            "    \"\"\"Sorta prints with 80% probability and kinda personality\"\"\"\n"
            "    try:\n"
            "        if not args:\n"
            "            if random.random() < 0.5:\n"
            "                print('[shrug] Nothing to print, I guess?')\n"
            "            return\n"
            "        if random.random() < 0.8:\n"
            "            print('[print]', *args)\n"
            "        else:\n"
            "            # Add some personality to the \"shrug\" responses\n"
            "            shrug_responses = [\n"
            "                '[shrug] Meh...',\n"
            "                '[shrug] Not feeling it right now',\n"
            "                '[shrug] Maybe later?',\n"
            "                '[shrug] *waves hand dismissively*',\n"
            "                '[shrug] Kinda busy'\n"
            "            ]\n"
            "            response = random.choice(shrug_responses)\n"
            "            print(response, *args)\n"
            "    except Exception as e:\n"
            "        print(f'[error] Sorta print kinda broke: {e}')\n"
            "        print('[fallback]', *args)"
        ),
    },
    "sometimes": {
        "type": "conditional",
        "pattern": re.compile(r'~sometimes\s*\(([^)]*)\)\s*\{?'),
        "description": "Fuzzy conditional trigger (50% chance)",
        "body": (
            "def sometimes(condition=True):\n"
            "    \"\"\"Sometimes evaluates a condition with 50% probability\"\"\"\n"
            "    try:\n"
            "        if condition is None:\n"
            "            print(\"[?] Sometimes got None as condition - treating as False\")\n"
            "            return False\n"
            "        return random.random() < 0.5 and bool(condition)\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Sometimes got confused: {e}\")\n"
            "        print(\"[tip] Flipping a coin instead\")\n"
            "        return random.choice([True, False])"
        ),
    },
    "maybe": {
        "type": "conditional",
        "pattern": re.compile(r'~maybe\s*\(([^)]*)\)\s*\{?'),
        "description": "Fuzzy conditional trigger (60% chance)",
        "body": (
            "def maybe(condition=True):\n"
            "    \"\"\"Maybe evaluates a condition with 60% probability\"\"\"\n"
            "    try:\n"
            "        if condition is None:\n"
            "            print(\"[?] Maybe got None as condition - treating as False\")\n"
            "            return False\n"
            "        return random.random() < 0.6 and bool(condition)\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Maybe couldn't decide: {e}\")\n"
            "        print(\"[tip] Defaulting to random choice\")\n"
            "        return random.choice([True, False])"
        ),
    },
    "fuzzy_reassign": {
        "type": "reassignment",
        "pattern": re.compile(r'(\w+)\s*~=\s*([^#;]+?)(?:\s*#.*)?(?:;|$)'),
        "description": "Fuzzy reassignment to an existing variable",
        "body": (
            "def fuzzy_assign(var_name, value):\n"
            "    \"\"\"Fuzzy assignment with error handling\"\"\"\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(value, (int, float)):\n"
            "            try:\n"
            "                value = float(value)\n"
            "            except (ValueError, TypeError):\n"
            "                print(f\"[?] fuzzy assignment got something weird: {repr(value)}\")\n"
            "                print(f\"[tip] Expected a number but got {type(value).__name__}\")\n"
            "                return random.randint(0, 10)\n"
            "        fuzz = random.randint(-1, 1)\n"
            "        return int(value + fuzz)\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Fuzzy assignment kinda failed: {e}\")\n"
            "        print(f\"[tip] Returning a random number because why not?\")\n"
            "        return random.randint(0, 10)"
        ),
    },
    "kinda_binary": {
        "type": "declaration",
        "pattern": re.compile(r'~kinda\s+binary\s+(\w+)(?:\s*~\s*probabilities\s*\(([^)]+)\))?(?:;|$)'),
        "description": "Three-state binary: positive (1), negative (-1), or neutral (0)",
        "body": (
            "def kinda_binary(pos_prob=0.4, neg_prob=0.4, neutral_prob=0.2):\n"
            "    \"\"\"Returns 1 (positive), -1 (negative), or 0 (neutral) with specified probabilities.\"\"\"\n"
            "    try:\n"
            "        # Validate probabilities\n"
            "        total_prob = pos_prob + neg_prob + neutral_prob\n"
            "        if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors\n"
            "            print(f\"[?] Binary probabilities don't add up to 1.0 (got {total_prob:.3f})\")\n"
            "            print(f\"[tip] Normalizing: pos={pos_prob}, neg={neg_prob}, neutral={neutral_prob}\")\n"
            "            # Normalize probabilities\n"
            "            pos_prob /= total_prob\n"
            "            neg_prob /= total_prob\n"
            "            neutral_prob /= total_prob\n"
            "        \n"
            "        rand = random.random()\n"
            "        if rand < pos_prob:\n"
            "            return 1\n"
            "        elif rand < pos_prob + neg_prob:\n"
            "            return -1\n"
            "        else:\n"
            "            return 0\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Binary choice kinda broke: {e}\")\n"
            "        print(f\"[tip] Defaulting to random choice between -1, 0, 1\")\n"
            "        return random.choice([-1, 0, 1])"
        ),
    },
    "ish_value": {
        "type": "value",
        "pattern": re.compile(r'(\d+(?:\.\d+)?)~ish'),
        "description": "Fuzzy value with ±2 variance (e.g., 42~ish)",
        "body": (
            "def ish_value(val, variance=2):\n"
            "    \"\"\"Create a fuzzy value with specified variance\"\"\"\n"
            "    try:\n"
            "        # Convert to float for processing\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            "                print(f\"[?] ish value got something weird: {repr(val)}\")\n"
            "                print(f\"[tip] Expected a number but got {type(val).__name__}\")\n"
            "                return random.uniform(-variance, variance)\n"
            "        \n"
            "        # Generate fuzzy variance\n"
            "        fuzz = random.uniform(-variance, variance)\n"
            "        result = val + fuzz\n"
            "        \n"
            "        # Return integer if input was integer, float otherwise\n"
            "        return int(result) if isinstance(val, int) else result\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Ish value kinda confused: {e}\")\n"
            "        print(f\"[tip] Returning random value with variance +/-{variance}\")\n"
            "        return random.uniform(-variance, variance)"
        ),
    },
    "ish_comparison": {
        "type": "comparison",
        "pattern": re.compile(r'(\w+)\s*~ish\s*([^#;\s]+)'),
        "description": "Fuzzy comparison with ±2 tolerance (e.g., score ~ish 100)",
        "body": (
            "def ish_comparison(left_val, right_val, tolerance=2):\n"
            "    \"\"\"Check if values are approximately equal within tolerance\"\"\"\n"
            "    try:\n"
            "        # Convert both values to numeric\n"
            "        if not isinstance(left_val, (int, float)):\n"
            "            try:\n"
            "                left_val = float(left_val)\n"
            "            except (ValueError, TypeError):\n"
            "                print(f\"[?] ish comparison got weird left value: {repr(left_val)}\")\n"
            "                print(f\"[tip] Expected a number but got {type(left_val).__name__}\")\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        if not isinstance(right_val, (int, float)):\n"
            "            try:\n"
            "                right_val = float(right_val)\n"
            "            except (ValueError, TypeError):\n"
            "                print(f\"[?] ish comparison got weird right value: {repr(right_val)}\")\n"
            "                print(f\"[tip] Expected a number but got {type(right_val).__name__}\")\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        # Check if values are within tolerance\n"
            "        difference = abs(left_val - right_val)\n"
            "        return difference <= tolerance\n"
            "    except Exception as e:\n"
            "        print(f\"[shrug] Ish comparison kinda broke: {e}\")\n"
            "        print(f\"[tip] Flipping a coin instead\")\n"
            "        return random.choice([True, False])"
        ),
    },
    "welp": {
        "type": "fallback",
        "pattern": re.compile(r'(.+)\s*~welp\s*(.+)'),
        "description": "Graceful fallback when expression fails (e.g., api_call() ~welp \"default\")",
        "body": (
            "def welp_fallback(primary_expr, fallback_value):\n"
            "    \"\"\"Execute primary expression with graceful fallback\"\"\"\n"
            "    try:\n"
            "        # If primary_expr is a callable, call it\n"
            "        if callable(primary_expr):\n"
            "            result = primary_expr()\n"
            "        else:\n"
            "            result = primary_expr\n"
            "        \n"
            "        # Return fallback if result is None or falsy (but not 0 or False explicitly)\n"
            "        if result is None:\n"
            "            print(f\"[welp] Got None, using fallback: {repr(fallback_value)}\")\n"
            "            return fallback_value\n"
            "        \n"
            "        return result\n"
            "    except Exception as e:\n"
            "        print(f\"[welp] Operation failed ({type(e).__name__}: {e}), using fallback: {repr(fallback_value)}\")\n"
            "        return fallback_value"
        ),
    },
}
