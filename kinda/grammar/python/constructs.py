# kinda/grammar/constructs.py

import re

KindaPythonConstructs = {
    "kinda_int": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda int (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy integer declaration with personality-adjusted noise",
        "body": (
            "def kinda_int(val):\n"
            '    """Fuzzy integer with personality-adjusted fuzz and chaos tracking"""\n'
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] kinda int got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = random.randint(fuzz_min, fuzz_max)\n"
            "        result = int(val + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda int got kinda confused: {e}")\n'
            '        print(f"[tip] Just picking a random number instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.randint(0, 10)"
        ),
    },
    "kinda_float": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda float (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy floating-point declaration with personality-adjusted drift",
        "body": (
            "def kinda_float(val):\n"
            '    """Fuzzy floating-point with personality-adjusted drift and chaos tracking"""\n'
            "    from kinda.personality import chaos_float_drift_range, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] kinda float got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.uniform(0.0, 10.0)\n"
            "        \n"
            "        # Convert to float\n"
            "        base_val = float(val)\n"
            "        \n"
            "        # Apply personality-adjusted drift\n"
            "        drift_min, drift_max = chaos_float_drift_range()\n"
            "        drift = random.uniform(drift_min, drift_max)\n"
            "        result = base_val + drift\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda float got kinda confused: {e}")\n'
            '        print(f"[tip] Just picking a random float instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.uniform(0.0, 10.0)"
        ),
    },
    "kinda_bool": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda bool (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy boolean declaration with personality-adjusted uncertainty",
        "body": (
            "def kinda_bool(val):\n"
            '    """Fuzzy boolean with personality-adjusted uncertainty and chaos tracking"""\n'
            "    from kinda.personality import chaos_bool_uncertainty, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Handle None case\n"
            "        if val is None:\n"
            '            print(f"[?] kinda bool got None - that\'s kinda ambiguous")\n'
            '            print(f"[tip] Choosing randomly between True and False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return random.choice([True, False])\n"
            "        \n"
            "        # Convert value to boolean\n"
            "        if isinstance(val, str):\n"
            "            val_lower = val.lower().strip()\n"
            "            if val_lower in ('true', '1', 'yes', 'on', 'y'):\n"
            "                base_bool = True\n"
            "            elif val_lower in ('false', '0', 'no', 'off', 'n'):\n"
            "                base_bool = False\n"
            "            else:\n"
            '                print(f"[?] kinda bool got ambiguous string: {repr(val)}")\n'
            '                print(f"[tip] Treating non-empty string as truthy")\n'
            "                base_bool = bool(val)\n"
            "        else:\n"
            "            base_bool = bool(val)\n"
            "        \n"
            "        # Apply personality-adjusted uncertainty\n"
            "        uncertainty = chaos_bool_uncertainty()\n"
            "        if random.random() < uncertainty:\n"
            "            # Introduce fuzzy uncertainty - flip the boolean sometimes\n"
            "            result = not base_bool\n"
            '            print(f"[fuzzy] kinda bool feeling uncertain, flipped to {result}")\n'
            "            update_chaos_state(failed=True)\n"
            "        else:\n"
            "            result = base_bool\n"
            "            update_chaos_state(failed=False)\n"
            "        \n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda bool got kinda confused: {e}")\n'
            '        print(f"[tip] Just flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r"~sorta print\s*\((.*)\)\s*(?:;|$)"),
        "description": "Print with personality-adjusted probability",
        "body": (
            "def sorta_print(*args):\n"
            '    """Sorta prints with personality-adjusted probability and chaos tracking"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if not args:\n"
            "            prob = chaos_probability('sorta_print')\n"
            "            if random.random() < prob:\n"
            "                print('[shrug] Nothing to print, I guess?')\n"
            "            update_chaos_state(failed=False)\n"
            "            return\n"
            "        \n"
            "        prob = chaos_probability('sorta_print')\n"
            "        if random.random() < prob:\n"
            "            print('[print]', *args)\n"
            "            update_chaos_state(failed=False)\n"
            "        else:\n"
            '            # Add some personality to the "shrug" responses\n'
            "            shrug_responses = [\n"
            "                '[shrug] Meh...',\n"
            "                '[shrug] Not feeling it right now',\n"
            "                '[shrug] Maybe later?',\n"
            "                '[shrug] *waves hand dismissively*',\n"
            "                '[shrug] Kinda busy'\n"
            "            ]\n"
            "            response = random.choice(shrug_responses)\n"
            "            print(response, *args)\n"
            "            update_chaos_state(failed=True)\n"
            "    except Exception as e:\n"
            "        print(f'[error] Sorta print kinda broke: {e}')\n"
            "        print('[fallback]', *args)\n"
            "        update_chaos_state(failed=True)"
        ),
    },
    "sometimes": {
        "type": "conditional",
        "pattern": re.compile(r"~sometimes\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with personality-adjusted probability",
        "body": (
            "def sometimes(condition=True):\n"
            '    """Sometimes evaluates a condition with personality-adjusted probability"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Sometimes got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        # SECURITY: Use secure condition checking\n"
            "        from kinda.security import secure_condition_check\n"
            "        should_proceed, condition_result = secure_condition_check(condition, 'Sometimes')\n"
            "        if not should_proceed:\n"
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('sometimes')\n"
            "        result = random.random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Sometimes got confused: {e}")\n'
            '        print("[tip] Flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "maybe": {
        "type": "conditional",
        "pattern": re.compile(r"~maybe\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with personality-adjusted probability",
        "body": (
            "def maybe(condition=True):\n"
            '    """Maybe evaluates a condition with personality-adjusted probability"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Maybe got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        # SECURITY: Use secure condition checking\n"
            "        from kinda.security import secure_condition_check\n"
            "        should_proceed, condition_result = secure_condition_check(condition, 'Maybe')\n"
            "        if not should_proceed:\n"
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('maybe')\n"
            "        result = random.random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Maybe couldn\'t decide: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "probably": {
        "type": "conditional",
        "pattern": re.compile(r"~probably\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with 70% base probability and personality adjustment",
        "body": (
            "def probably(condition=True):\n"
            '    """Probably evaluates a condition with 70% base probability and personality adjustment"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Probably got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        # SECURITY: Use secure condition checking\n"
            "        from kinda.security import secure_condition_check\n"
            "        should_proceed, condition_result = secure_condition_check(condition, 'Probably')\n"
            "        if not should_proceed:\n"
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('probably')\n"
            "        result = random.random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Probably got confused: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "rarely": {
        "type": "conditional",
        "pattern": re.compile(r"~rarely\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with 15% base probability and personality adjustment",
        "body": (
            "def rarely(condition=True):\n"
            '    """Rarely evaluates a condition with 15% base probability and personality adjustment"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Rarely got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        # SECURITY: Use secure condition checking\n"
            "        from kinda.security import secure_condition_check\n"
            "        should_proceed, condition_result = secure_condition_check(condition, 'Rarely')\n"
            "        if not should_proceed:\n"
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('rarely')\n"
            "        result = random.random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Rarely got confused: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "fuzzy_reassign": {
        "type": "reassignment",
        "pattern": re.compile(r"(\w+)\s*~=\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy reassignment with personality-adjusted noise",
        "body": (
            "def fuzzy_assign(var_name, value):\n"
            '    """Fuzzy assignment with personality-adjusted fuzz and chaos tracking"""\n'
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(value, (int, float)):\n"
            "            try:\n"
            "                value = float(value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] fuzzy assignment got something weird: {repr(value)}")\n'
            '                print(f"[tip] Expected a number but got {type(value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = random.randint(fuzz_min, fuzz_max)\n"
            "        result = int(value + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Fuzzy assignment kinda failed: {e}")\n'
            '        print(f"[tip] Returning a random number because why not?")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.randint(0, 10)"
        ),
    },
    "kinda_binary": {
        "type": "declaration",
        "pattern": re.compile(
            r"~kinda\s+binary\s+(\w+)(?:\s*~\s*probabilities\s*\(([^)]+)\))?(?:;|$)"
        ),
        "description": "Three-state binary with personality-adjusted probabilities",
        "body": (
            "def kinda_binary(pos_prob=None, neg_prob=None, neutral_prob=None):\n"
            '    """Returns 1 (positive), -1 (negative), or 0 (neutral) with personality-adjusted probabilities."""\n'
            "    from kinda.personality import chaos_binary_probabilities, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted probabilities if not specified\n"
            "        if pos_prob is None or neg_prob is None or neutral_prob is None:\n"
            "            pos_prob, neg_prob, neutral_prob = chaos_binary_probabilities()\n"
            "        \n"
            "        # Validate probabilities\n"
            "        total_prob = pos_prob + neg_prob + neutral_prob\n"
            "        if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors\n"
            '            print(f"[?] Binary probabilities don\'t add up to 1.0 (got {total_prob:.3f})")\n'
            '            print(f"[tip] Normalizing: pos={pos_prob:.3f}, neg={neg_prob:.3f}, neutral={neutral_prob:.3f}")\n'
            "            # Normalize probabilities\n"
            "            pos_prob /= total_prob\n"
            "            neg_prob /= total_prob\n"
            "            neutral_prob /= total_prob\n"
            "        \n"
            "        rand = random.random()\n"
            "        if rand < pos_prob:\n"
            "            result = 1\n"
            "        elif rand < pos_prob + neg_prob:\n"
            "            result = -1\n"
            "        else:\n"
            "            result = 0\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Binary choice kinda broke: {e}")\n'
            '        print(f"[tip] Defaulting to random choice between -1, 0, 1")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([-1, 0, 1])"
        ),
    },
    "ish_value": {
        "type": "value",
        "pattern": re.compile(r"(\d+(?:\.\d+)?)~ish"),
        "description": "Fuzzy value with personality-adjusted variance",
        "body": (
            "def ish_value(val, variance=None):\n"
            '    """Create a fuzzy value with personality-adjusted variance"""\n'
            "    from kinda.personality import chaos_variance, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted variance if not specified\n"
            "        if variance is None:\n"
            "            variance = chaos_variance()\n"
            "        \n"
            "        # Convert to float for processing\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish value got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.uniform(-variance, variance)\n"
            "        \n"
            "        # Generate fuzzy variance\n"
            "        fuzz = random.uniform(-variance, variance)\n"
            "        result = val + fuzz\n"
            "        update_chaos_state(failed=False)\n"
            "        \n"
            "        # Return integer if input was integer, float otherwise\n"
            "        return int(result) if isinstance(val, int) else result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Ish value kinda confused: {e}")\n'
            '        print(f"[tip] Returning random value with variance +/-{variance}")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.uniform(-variance, variance)"
        ),
    },
    "ish_comparison": {
        "type": "comparison",
        "pattern": re.compile(r"(\w+)\s*~ish\s*([^#;\s]+)"),
        "description": "Fuzzy comparison with personality-adjusted tolerance",
        "body": (
            "def ish_comparison(left_val, right_val, tolerance=None):\n"
            '    """Check if values are approximately equal within personality-adjusted tolerance"""\n'
            "    from kinda.personality import chaos_tolerance, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted tolerance if not specified\n"
            "        if tolerance is None:\n"
            "            tolerance = chaos_tolerance()\n"
            "        \n"
            "        # Convert both values to numeric\n"
            "        if not isinstance(left_val, (int, float)):\n"
            "            try:\n"
            "                left_val = float(left_val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish comparison got weird left value: {repr(left_val)}")\n'
            '                print(f"[tip] Expected a number but got {type(left_val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        if not isinstance(right_val, (int, float)):\n"
            "            try:\n"
            "                right_val = float(right_val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish comparison got weird right value: {repr(right_val)}")\n'
            '                print(f"[tip] Expected a number but got {type(right_val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        # Check if values are within tolerance\n"
            "        difference = abs(left_val - right_val)\n"
            "        result = difference <= tolerance\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Ish comparison kinda broke: {e}")\n'
            '        print(f"[tip] Flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "welp": {
        "type": "fallback",
        "pattern": re.compile(r"(.+)\s*~welp\s*(.+)"),
        "description": "Graceful fallback with personality-aware error messages",
        "body": (
            "def welp_fallback(primary_expr, fallback_value):\n"
            '    """Execute primary expression with graceful fallback and chaos tracking"""\n'
            "    from kinda.personality import update_chaos_state, get_personality\n"
            "    try:\n"
            "        # If primary_expr is a callable, call it\n"
            "        if callable(primary_expr):\n"
            "            result = primary_expr()\n"
            "        else:\n"
            "            result = primary_expr\n"
            "        \n"
            "        # Return fallback if result is None or falsy (but not 0 or False explicitly)\n"
            "        if result is None:\n"
            "            # Get personality-appropriate error message style\n"
            "            personality = get_personality()\n"
            "            style = personality.get_error_message_style()\n"
            "            \n"
            "            if style == 'professional':\n"
            '                print(f"[welp] Expression returned None, using fallback: {repr(fallback_value)}")\n'
            "            elif style == 'friendly':\n"
            '                print(f"[welp] Got nothing there, trying fallback: {repr(fallback_value)}")\n'
            "            elif style == 'snarky':\n"
            '                print(f"[welp] Well that was useless, falling back to: {repr(fallback_value)}")\n'
            "            else:  # chaotic\n"
            '                print(f"[welp] *shrugs* That didn\'t work, whatever: {repr(fallback_value)}")\n'
            "            \n"
            "            update_chaos_state(failed=True)\n"
            "            return fallback_value\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            "        # Get personality-appropriate error message style\n"
            "        personality = get_personality()\n"
            "        style = personality.get_error_message_style()\n"
            "        \n"
            "        if style == 'professional':\n"
            '            print(f"[welp] Operation failed ({type(e).__name__}: {e}), using fallback: {repr(fallback_value)}")\n'
            "        elif style == 'friendly':\n"
            '            print(f"[welp] Oops, that didn\'t work ({e}), trying: {repr(fallback_value)}")\n'
            "        elif style == 'snarky':\n"
            '            print(f"[welp] Predictably failed with {type(e).__name__}, fine: {repr(fallback_value)}")\n'
            "        else:  # chaotic\n"
            '            print(f"[welp] BOOM! {e} 💥 Whatever, here\'s: {repr(fallback_value)}")\n'
            "        \n"
            "        update_chaos_state(failed=True)\n"
            "        return fallback_value"
        ),
    },
    "time_drift_float": {
        "type": "declaration",
        "pattern": re.compile(r"~time drift float (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Time-based drift floating-point declaration with accumulating uncertainty",
        "body": (
            "def time_drift_float(var_name, initial_value):\n"
            '    """Create a floating-point variable that drifts over time and usage"""\n'
            "    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Convert initial value to float\n"
            "        if not isinstance(initial_value, (int, float)):\n"
            "            try:\n"
            "                initial_value = float(initial_value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] time drift float got something weird: {repr(initial_value)}")\n'
            '                print(f"[tip] Expected a number but got {type(initial_value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                initial_value = random.uniform(0.0, 10.0)\n"
            "        \n"
            "        float_value = float(initial_value)\n"
            "        \n"
            "        # Register variable for time-based drift tracking\n"
            "        register_time_variable(var_name, float_value, 'float')\n"
            "        \n"
            "        # Apply initial small random drift (fresh variables are mostly precise)\n"
            "        initial_drift = random.uniform(-0.01, 0.01)\n"
            "        result = float_value + initial_drift\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Time drift float got confused: {e}")\n'
            '        print(f"[tip] Just picking a random float instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.uniform(0.0, 10.0)"
        ),
    },
    "time_drift_int": {
        "type": "declaration",
        "pattern": re.compile(r"~time drift int (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Time-based drift integer declaration with accumulating uncertainty",
        "body": (
            "def time_drift_int(var_name, initial_value):\n"
            '    """Create an integer variable that drifts over time and usage"""\n'
            "    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Convert initial value to int\n"
            "        if not isinstance(initial_value, (int, float)):\n"
            "            try:\n"
            "                initial_value = float(initial_value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] time drift int got something weird: {repr(initial_value)}")\n'
            '                print(f"[tip] Expected a number but got {type(initial_value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                initial_value = random.randint(0, 10)\n"
            "        \n"
            "        int_value = int(initial_value)\n"
            "        \n"
            "        # Register variable for time-based drift tracking\n"
            "        register_time_variable(var_name, int_value, 'int')\n"
            "        \n"
            "        # Apply initial small random fuzz (fresh variables are mostly precise)\n"
            "        initial_fuzz = random.choice([-1, 0, 0, 0, 1])  # Mostly no fuzz, occasional small drift\n"
            "        result = int_value + initial_fuzz\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Time drift int got confused: {e}")\n'
            '        print(f"[tip] Just picking a random integer instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.randint(0, 10)"
        ),
    },
    "drift_access": {
        "type": "access",
        "pattern": re.compile(r"(\w+)~drift"),
        "description": "Access variable with time-based drift accumulation",
        "body": (
            "def drift_access(var_name, current_value):\n"
            '    """Access a variable with time-based drift applied"""\n'
            "    from kinda.personality import get_time_drift, update_chaos_state\n"
            "    try:\n"
            "        # Calculate time-based drift\n"
            "        drift = get_time_drift(var_name, current_value)\n"
            "        \n"
            "        # Apply drift to current value\n"
            "        if isinstance(current_value, (int, float)):\n"
            "            result = current_value + drift\n"
            "            # Maintain type consistency\n"
            "            if isinstance(current_value, int):\n"
            "                result = int(round(result))\n"
            "        else:\n"
            "            result = current_value  # Non-numeric values don't drift\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Drift access failed: {e}")\n'
            '        print(f"[tip] Returning original value")\n'
            "        update_chaos_state(failed=True)\n"
            "        return current_value if current_value is not None else 0"
        ),
    },
}
