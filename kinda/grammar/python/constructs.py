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
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state, chaos_randint\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] kinda int got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return chaos_randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = chaos_randint(fuzz_min, fuzz_max)\n"
            "        result = int(val + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda int got kinda confused: {e}")\n'
            '        print(f"[tip] Just picking a random number instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_randint(0, 10)"
        ),
    },
    "kinda_float": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda float (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy floating-point declaration with personality-adjusted drift",
        "body": (
            "def kinda_float(val):\n"
            '    """Fuzzy floating-point with personality-adjusted drift and chaos tracking"""\n'
            "    from kinda.personality import chaos_float_drift_range, update_chaos_state, chaos_uniform\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] kinda float got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return chaos_uniform(0.0, 10.0)\n"
            "        \n"
            "        # Convert to float\n"
            "        base_val = float(val)\n"
            "        \n"
            "        # Apply personality-adjusted drift\n"
            "        drift_min, drift_max = chaos_float_drift_range()\n"
            "        drift = chaos_uniform(drift_min, drift_max)\n"
            "        result = base_val + drift\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda float got kinda confused: {e}")\n'
            '        print(f"[tip] Just picking a random float instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_uniform(0.0, 10.0)"
        ),
    },
    "kinda_bool": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda bool (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy boolean declaration with personality-adjusted uncertainty",
        "body": (
            "def kinda_bool(val):\n"
            '    """Fuzzy boolean with personality-adjusted uncertainty and chaos tracking"""\n'
            "    from kinda.personality import chaos_bool_uncertainty, update_chaos_state, chaos_random, chaos_choice\n"
            "    try:\n"
            "        # Handle None case\n"
            "        if val is None:\n"
            '            print(f"[?] kinda bool got None - that\'s kinda ambiguous")\n'
            '            print(f"[tip] Choosing randomly between True and False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return chaos_choice([True, False])\n"
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
            "        if chaos_random() < uncertainty:\n"
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
            "        return chaos_choice([True, False])"
        ),
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r"~sorta print\s*\((.*)\)\s*(?:;|$)"),
        "description": "Print with personality-adjusted probability",
        "body": (
            "def sorta_print(*args):\n"
            '    """Sorta prints with personality-adjusted probability and chaos tracking"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice\n"
            "    try:\n"
            "        if not args:\n"
            "            prob = chaos_probability('sorta_print')\n"
            "            if chaos_random() < prob:\n"
            "                print('[shrug] Nothing to print, I guess?')\n"
            "            update_chaos_state(failed=False)\n"
            "            return\n"
            "        \n"
            "        prob = chaos_probability('sorta_print')\n"
            "        if chaos_random() < prob:\n"
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
            "            response = chaos_choice(shrug_responses)\n"
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
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice\n"
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
            "        result = chaos_random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Sometimes got confused: {e}")\n'
            '        print("[tip] Flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_choice([True, False])"
        ),
    },
    "maybe": {
        "type": "conditional",
        "pattern": re.compile(r"~maybe\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with personality-adjusted probability",
        "body": (
            "def maybe(condition=True):\n"
            '    """Maybe evaluates a condition with personality-adjusted probability"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice\n"
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
            "        result = chaos_random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Maybe couldn\'t decide: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_choice([True, False])"
        ),
    },
    "probably": {
        "type": "conditional",
        "pattern": re.compile(r"~probably\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with 70% base probability and personality adjustment",
        "body": (
            "def probably(condition=True):\n"
            '    """Probably evaluates a condition with 70% base probability and personality adjustment"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice\n"
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
            "        result = chaos_random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Probably got confused: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_choice([True, False])"
        ),
    },
    "rarely": {
        "type": "conditional",
        "pattern": re.compile(r"~rarely\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with 15% base probability and personality adjustment",
        "body": (
            "def rarely(condition=True):\n"
            '    """Rarely evaluates a condition with 15% base probability and personality adjustment"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice\n"
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
            "        result = chaos_random() < prob and condition_result\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Rarely got confused: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_choice([True, False])"
        ),
    },
    "fuzzy_reassign": {
        "type": "reassignment",
        "pattern": re.compile(r"(\w+)\s*~=\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy reassignment with personality-adjusted noise",
        "body": (
            "def fuzzy_assign(var_name, value):\n"
            '    """Fuzzy assignment with personality-adjusted fuzz and chaos tracking"""\n'
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state, chaos_randint\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(value, (int, float)):\n"
            "            try:\n"
            "                value = float(value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] fuzzy assignment got something weird: {repr(value)}")\n'
            '                print(f"[tip] Expected a number but got {type(value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return chaos_randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = chaos_randint(fuzz_min, fuzz_max)\n"
            "        result = int(value + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Fuzzy assignment kinda failed: {e}")\n'
            '        print(f"[tip] Returning a random number because why not?")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_randint(0, 10)"
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
            "    from kinda.personality import chaos_binary_probabilities, update_chaos_state, chaos_random, chaos_choice\n"
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
            "        rand = chaos_random()\n"
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
            "        return chaos_choice([-1, 0, 1])"
        ),
    },
    "ish_value": {
        "type": "value",
        "pattern": re.compile(r"(\d+(?:\.\d+)?)~ish"),
        "description": "Fuzzy value with personality-adjusted variance",
        "body": (
            "def ish_value(val, variance=None):\n"
            '    """Create a fuzzy value with personality-adjusted variance"""\n'
            "    from kinda.personality import chaos_variance, update_chaos_state, chaos_uniform\n"
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
            "                return chaos_uniform(-variance, variance)\n"
            "        \n"
            "        # Generate fuzzy variance\n"
            "        fuzz = chaos_uniform(-variance, variance)\n"
            "        result = val + fuzz\n"
            "        update_chaos_state(failed=False)\n"
            "        \n"
            "        # Return integer if input was integer, float otherwise\n"
            "        return int(result) if isinstance(val, int) else result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Ish value kinda confused: {e}")\n'
            '        print(f"[tip] Returning random value with variance +/-{variance}")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_uniform(-variance, variance)"
        ),
    },
    "ish_comparison": {
        "type": "comparison",
        "pattern": re.compile(r"(\w+)\s*~ish\s*([^#;\s]+)"),
        "description": "Fuzzy comparison with personality-adjusted tolerance",
        "body": (
            "def ish_comparison(left_val, right_val, tolerance=None):\n"
            '    """Check if values are approximately equal within personality-adjusted tolerance"""\n'
            "    from kinda.personality import chaos_tolerance, update_chaos_state, chaos_choice\n"
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
            "                return chaos_choice([True, False])\n"
            "        \n"
            "        if not isinstance(right_val, (int, float)):\n"
            "            try:\n"
            "                right_val = float(right_val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish comparison got weird right value: {repr(right_val)}")\n'
            '                print(f"[tip] Expected a number but got {type(right_val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return chaos_choice([True, False])\n"
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
            "        return chaos_choice([True, False])"
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
            '            print(f"[welp] BOOM! {e} *CRASH* Whatever, here\'s: {repr(fallback_value)}")\n'
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
            "    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state, chaos_uniform\n"
            "    try:\n"
            "        # Convert initial value to float\n"
            "        if not isinstance(initial_value, (int, float)):\n"
            "            try:\n"
            "                initial_value = float(initial_value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] time drift float got something weird: {repr(initial_value)}")\n'
            '                print(f"[tip] Expected a number but got {type(initial_value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                initial_value = chaos_uniform(0.0, 10.0)\n"
            "        \n"
            "        float_value = float(initial_value)\n"
            "        \n"
            "        # Register variable for time-based drift tracking\n"
            "        register_time_variable(var_name, float_value, 'float')\n"
            "        \n"
            "        # Apply initial small random drift (fresh variables are mostly precise)\n"
            "        initial_drift = chaos_uniform(-0.01, 0.01)\n"
            "        result = float_value + initial_drift\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Time drift float got confused: {e}")\n'
            '        print(f"[tip] Just picking a random float instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_uniform(0.0, 10.0)"
        ),
    },
    "time_drift_int": {
        "type": "declaration",
        "pattern": re.compile(r"~time drift int (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Time-based drift integer declaration with accumulating uncertainty",
        "body": (
            "def time_drift_int(var_name, initial_value):\n"
            '    """Create an integer variable that drifts over time and usage"""\n'
            "    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state, chaos_randint, chaos_choice\n"
            "    try:\n"
            "        # Convert initial value to int\n"
            "        if not isinstance(initial_value, (int, float)):\n"
            "            try:\n"
            "                initial_value = float(initial_value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] time drift int got something weird: {repr(initial_value)}")\n'
            '                print(f"[tip] Expected a number but got {type(initial_value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                initial_value = chaos_randint(0, 10)\n"
            "        \n"
            "        int_value = int(initial_value)\n"
            "        \n"
            "        # Register variable for time-based drift tracking\n"
            "        register_time_variable(var_name, int_value, 'int')\n"
            "        \n"
            "        # Apply initial small random fuzz (fresh variables are mostly precise)\n"
            "        initial_fuzz = chaos_choice([-1, 0, 0, 0, 1])  # Mostly no fuzz, occasional small drift\n"
            "        result = int_value + initial_fuzz\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Time drift int got confused: {e}")\n'
            '        print(f"[tip] Just picking a random integer instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return chaos_randint(0, 10)"
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
    "assert_eventually": {
        "type": "statistical",
        "pattern": re.compile(
            r"~assert_eventually\s*\(\s*([^,)]+)(?:\s*,\s*timeout\s*=\s*([^,)]+))?(?:\s*,\s*confidence\s*=\s*([^)]+))?\s*\)"
        ),
        "description": "Statistical assertion that waits for probabilistic condition to become true",
        "body": (
            "def assert_eventually(condition, timeout=5.0, confidence=0.95):\n"
            '    """Wait for probabilistic condition to become true with statistical confidence"""\n'
            "    import time\n"
            "    from kinda.personality import update_chaos_state, get_personality\n"
            "    from kinda.security import secure_condition_check\n"
            "    try:\n"
            "        # Validate parameters\n"
            "        if not isinstance(timeout, (int, float)) or timeout <= 0:\n"
            '            print(f"[?] assert_eventually got weird timeout: {timeout}")\n'
            '            print(f"[tip] Using default timeout of 5.0 seconds")\n'
            "            timeout = 5.0\n"
            "        \n"
            "        if not isinstance(confidence, (int, float)) or not (0 < confidence < 1):\n"
            '            print(f"[?] assert_eventually got weird confidence: {confidence}")\n'
            '            print(f"[tip] Using default confidence of 0.95")\n'
            "            confidence = 0.95\n"
            "        \n"
            "        start_time = time.time()\n"
            "        attempts = 0\n"
            "        successes = 0\n"
            "        min_attempts = max(10, int(1 / (1 - confidence) * 3))  # Statistical minimum\n"
            "        \n"
            "        # Get personality for error messages\n"
            "        personality = get_personality()\n"
            "        style = personality.get_error_message_style()\n"
            "        \n"
            "        while time.time() - start_time < timeout:\n"
            "            attempts += 1\n"
            "            \n"
            "            # Security check for condition\n"
            "            should_proceed, condition_result = secure_condition_check(condition, 'assert_eventually')\n"
            "            if not should_proceed:\n"
            "                update_chaos_state(failed=True)\n"
            "                raise AssertionError(f'Unsafe condition in assert_eventually')\n"
            "            \n"
            "            if condition_result:\n"
            "                successes += 1\n"
            "            \n"
            "            # Check if we have enough data for statistical confidence\n"
            "            if attempts >= min_attempts:\n"
            "                observed_rate = successes / attempts\n"
            "                # Use Wilson score interval for confidence bounds\n"
            "                import math\n"
            "                z = 1.96  # 95% confidence\n"
            "                if confidence > 0.99:\n"
            "                    z = 2.576  # 99% confidence\n"
            "                elif confidence > 0.975:\n"
            "                    z = 2.326  # 97.5% confidence\n"
            "                elif confidence > 0.9:\n"
            "                    z = 1.645  # 90% confidence\n"
            "                \n"
            "                n = attempts\n"
            "                p_hat = observed_rate\n"
            "                denominator = 1 + z*z/n\n"
            "                center = (p_hat + z*z/(2*n)) / denominator\n"
            "                margin = z * math.sqrt((p_hat*(1-p_hat) + z*z/(4*n))/n) / denominator\n"
            "                lower_bound = center - margin\n"
            "                \n"
            "                # If lower confidence bound > 0.5, condition is statistically true\n"
            "                if lower_bound > 0.5:\n"
            '                    print(f"[stat] assert_eventually succeeded: {successes}/{attempts} = {observed_rate:.3f} (confidence: {confidence:.3f})")\n'
            "                    update_chaos_state(failed=False)\n"
            "                    return True\n"
            "            \n"
            "            time.sleep(0.05)  # Small delay between attempts\n"
            "        \n"
            "        # Timeout reached - statistical failure\n"
            "        final_rate = successes / attempts if attempts > 0 else 0\n"
            "        \n"
            "        if style == 'professional':\n"
            "            error_msg = f'Statistical assertion failed: condition was true in {successes}/{attempts} attempts ({final_rate:.3f}), below confidence threshold {confidence:.3f} within {timeout}s'\n"
            "        elif style == 'friendly':\n"
            "            error_msg = f'Hmm, that condition only happened {successes}/{attempts} times ({final_rate:.3f}) in {timeout}s - not confident enough!'\n"
            "        elif style == 'snarky':\n"
            "            error_msg = f'Surprise! Your \"eventually\" condition was kinda flaky: {successes}/{attempts} ({final_rate:.3f}) in {timeout}s. Try lowering your standards.'\n"
            "        else:  # chaotic\n"
            "            error_msg = f'NOPE! *BOOM* Condition flopped {attempts-successes}/{attempts} times in {timeout}s. Maybe try \"~assert_never\" instead? *wink*'\n"
            "        \n"
            "        update_chaos_state(failed=True)\n"
            "        raise AssertionError(error_msg)\n"
            "    except AssertionError:\n"
            "        raise  # Re-raise assertion errors\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] assert_eventually got confused: {e}")\n'
            '        print(f"[tip] Maybe check your condition syntax?")\n'
            "        update_chaos_state(failed=True)\n"
            "        raise AssertionError(f'assert_eventually failed with error: {e}')"
        ),
    },
    "assert_probability": {
        "type": "statistical",
        "pattern": re.compile(
            r"~assert_probability\s*\(\s*([^,)]+)(?:\s*,\s*expected_prob\s*=\s*([^,)]+))?(?:\s*,\s*tolerance\s*=\s*([^,)]+))?(?:\s*,\s*samples\s*=\s*([^)]+))?\s*\)"
        ),
        "description": "Statistical assertion for validating probability distributions",
        "body": (
            "def assert_probability(event, expected_prob=0.5, tolerance=0.1, samples=1000):\n"
            '    """Validate probability distributions with statistical testing"""\n'
            "    from kinda.personality import update_chaos_state, get_personality\n"
            "    from kinda.security import secure_condition_check\n"
            "    import math\n"
            "    try:\n"
            "        # Validate parameters\n"
            "        if not isinstance(expected_prob, (int, float)) or not (0 <= expected_prob <= 1):\n"
            '            print(f"[?] assert_probability got weird expected_prob: {expected_prob}")\n'
            '            print(f"[tip] Using default expected_prob of 0.5")\n'
            "            expected_prob = 0.5\n"
            "        \n"
            "        if not isinstance(tolerance, (int, float)) or tolerance <= 0:\n"
            '            print(f"[?] assert_probability got weird tolerance: {tolerance}")\n'
            '            print(f"[tip] Using default tolerance of 0.1")\n'
            "            tolerance = 0.1\n"
            "        \n"
            "        if not isinstance(samples, int) or samples <= 0:\n"
            '            print(f"[?] assert_probability got weird samples: {samples}")\n'
            '            print(f"[tip] Using default samples of 1000")\n'
            "            samples = 1000\n"
            "        \n"
            "        # Limit samples for performance and security\n"
            "        if samples > 10000:\n"
            '            print(f"[?] Limiting samples to 10000 for performance (requested {samples})")\n'
            "            samples = 10000\n"
            "        \n"
            "        # Run statistical sampling\n"
            "        successes = 0\n"
            "        for i in range(samples):\n"
            "            # Security check for event condition\n"
            "            should_proceed, event_result = secure_condition_check(event, 'assert_probability')\n"
            "            if not should_proceed:\n"
            "                update_chaos_state(failed=True)\n"
            "                raise AssertionError(f'Unsafe event condition in assert_probability')\n"
            "            \n"
            "            if event_result:\n"
            "                successes += 1\n"
            "        \n"
            "        observed_prob = successes / samples\n"
            "        difference = abs(observed_prob - expected_prob)\n"
            "        \n"
            "        # Calculate statistical significance (binomial test approximation)\n"
            "        # Standard error for binomial proportion\n"
            "        se = math.sqrt(expected_prob * (1 - expected_prob) / samples)\n"
            "        z_score = abs(observed_prob - expected_prob) / se if se > 0 else 0\n"
            "        \n"
            "        # Get personality for error messages\n"
            "        personality = get_personality()\n"
            "        style = personality.get_error_message_style()\n"
            "        \n"
            "        if difference <= tolerance:\n"
            '            print(f"[stat] assert_probability passed: {observed_prob:.3f} vs expected {expected_prob:.3f} (diff: {difference:.3f}, tolerance: {tolerance:.3f})")\n'
            "            update_chaos_state(failed=False)\n"
            "            return True\n"
            "        else:\n"
            "            # Statistical failure\n"
            "            if style == 'professional':\n"
            "                error_msg = f'Probability assertion failed: observed {observed_prob:.3f}, expected {expected_prob:.3f} ± {tolerance:.3f} (difference: {difference:.3f}, z-score: {z_score:.2f})'\n"
            "            elif style == 'friendly':\n"
            "                error_msg = f'Oops! Got probability {observed_prob:.3f} but expected around {expected_prob:.3f} ± {tolerance:.3f} (off by {difference:.3f})'\n"
            "            elif style == 'snarky':\n"
            "                error_msg = f'Your random event is apparently not very random: {observed_prob:.3f} vs {expected_prob:.3f} ± {tolerance:.3f}. Maybe check your math?'\n"
            "            else:  # chaotic\n"
            "                error_msg = f'PROBABILITY FAIL! [DICE]*CRASH* Got {observed_prob:.3f}, wanted ~{expected_prob:.3f}. That\\'s a {difference:.3f} swing, which is NOT kinda close!'\n"
            "            \n"
            "            update_chaos_state(failed=True)\n"
            "            raise AssertionError(error_msg)\n"
            "    except AssertionError:\n"
            "        raise  # Re-raise assertion errors\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] assert_probability got confused: {e}")\n'
            '        print(f"[tip] Maybe check your event condition or parameters?")\n'
            "        update_chaos_state(failed=True)\n"
            "        raise AssertionError(f'assert_probability failed with error: {e}')"
        ),
    },
    "sometimes_while": {
        "type": "loop",
        "pattern": re.compile(r"~sometimes_while\s+(.+):\s*"),
        "description": "Probabilistic while loop with personality-adjusted continuation probability",
        "body": (
            "def sometimes_while_condition(condition):\n"
            '    """Check if sometimes_while loop should continue with probabilistic decision"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random\n"
            "    from kinda.security import secure_condition_check\n"
            "    try:\n"
            "        # First check the actual condition\n"
            "        should_proceed, condition_result = secure_condition_check(condition, 'sometimes_while')\n"
            "        if not should_proceed:\n"
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        # If condition is false, definitely don't continue\n"
            "        if not condition_result:\n"
            "            update_chaos_state(failed=False)\n"
            "            return False\n"
            "        \n"
            "        # Condition is true, now apply personality-based probability\n"
            "        prob = chaos_probability('sometimes_while')\n"
            "        should_continue = chaos_random() < prob\n"
            "        update_chaos_state(failed=not should_continue)\n"
            "        return should_continue\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] sometimes_while condition check failed: {e}")\n'
            '        print(f"[tip] Defaulting to False for safety")\n'
            "        update_chaos_state(failed=True)\n"
            "        return False"
        ),
    },
    "maybe_for": {
        "type": "loop",
        "pattern": re.compile(r"~maybe_for\s+(\w+)\s+in\s+(.+):\s*"),
        "description": "Probabilistic for loop with personality-adjusted per-iteration execution",
        "body": (
            "def maybe_for_item_execute():\n"
            '    """Check if maybe_for should execute current iteration with probabilistic decision"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, chaos_random\n"
            "    try:\n"
            "        # Apply personality-based probability for this iteration\n"
            "        prob = chaos_probability('maybe_for')\n"
            "        should_execute = chaos_random() < prob\n"
            "        update_chaos_state(failed=not should_execute)\n"
            "        return should_execute\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] maybe_for execution check failed: {e}")\n'
            '        print(f"[tip] Defaulting to True for safety")\n'
            "        update_chaos_state(failed=True)\n"
            "        return True"
        ),
    },
}
