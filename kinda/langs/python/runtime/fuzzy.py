# Auto-generated fuzzy runtime for Python
# Uses centralized seeded RNG from PersonalityContext for reproducibility
env = {}

def assert_eventually(condition, timeout=5.0, confidence=0.95):
    """Wait for probabilistic condition to become true with statistical confidence"""
    import time
    from kinda.personality import update_chaos_state, get_personality
    from kinda.security import secure_condition_check
    try:
        # Validate parameters
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            print(f"[?] assert_eventually got weird timeout: {timeout}")
            print(f"[tip] Using default timeout of 5.0 seconds")
            timeout = 5.0
        
        if not isinstance(confidence, (int, float)) or not (0 < confidence < 1):
            print(f"[?] assert_eventually got weird confidence: {confidence}")
            print(f"[tip] Using default confidence of 0.95")
            confidence = 0.95
        
        start_time = time.time()
        attempts = 0
        successes = 0
        min_attempts = max(10, int(1 / (1 - confidence) * 3))  # Statistical minimum
        
        # Get personality for error messages
        personality = get_personality()
        style = personality.get_error_message_style()
        
        while time.time() - start_time < timeout:
            attempts += 1
            
            # Security check for condition
            should_proceed, condition_result = secure_condition_check(condition, 'assert_eventually')
            if not should_proceed:
                update_chaos_state(failed=True)
                raise AssertionError(f'Unsafe condition in assert_eventually')
            
            if condition_result:
                successes += 1
            
            # Check if we have enough data for statistical confidence
            if attempts >= min_attempts:
                observed_rate = successes / attempts
                # Use Wilson score interval for confidence bounds
                import math
                z = 1.96  # 95% confidence
                if confidence > 0.99:
                    z = 2.576  # 99% confidence
                elif confidence > 0.975:
                    z = 2.326  # 97.5% confidence
                elif confidence > 0.9:
                    z = 1.645  # 90% confidence
                
                n = attempts
                p_hat = observed_rate
                denominator = 1 + z*z/n
                center = (p_hat + z*z/(2*n)) / denominator
                margin = z * math.sqrt((p_hat*(1-p_hat) + z*z/(4*n))/n) / denominator
                lower_bound = center - margin
                
                # If lower confidence bound > 0.5, condition is statistically true
                if lower_bound > 0.5:
                    print(f"[stat] assert_eventually succeeded: {successes}/{attempts} = {observed_rate:.3f} (confidence: {confidence:.3f})")
                    update_chaos_state(failed=False)
                    return True
            
            time.sleep(0.05)  # Small delay between attempts
        
        # Timeout reached - statistical failure
        final_rate = successes / attempts if attempts > 0 else 0
        
        if style == 'professional':
            error_msg = f'Statistical assertion failed: condition was true in {successes}/{attempts} attempts ({final_rate:.3f}), below confidence threshold {confidence:.3f} within {timeout}s'
        elif style == 'friendly':
            error_msg = f'Hmm, that condition only happened {successes}/{attempts} times ({final_rate:.3f}) in {timeout}s - not confident enough!'
        elif style == 'snarky':
            error_msg = f'Surprise! Your "eventually" condition was kinda flaky: {successes}/{attempts} ({final_rate:.3f}) in {timeout}s. Try lowering your standards.'
        else:  # chaotic
            error_msg = f'NOPE! 💥 Condition flopped {attempts-successes}/{attempts} times in {timeout}s. Maybe try "~assert_never" instead? 😏'
        
        update_chaos_state(failed=True)
        raise AssertionError(error_msg)
    except AssertionError:
        raise  # Re-raise assertion errors
    except Exception as e:
        print(f"[shrug] assert_eventually got confused: {e}")
        print(f"[tip] Maybe check your condition syntax?")
        update_chaos_state(failed=True)
        raise AssertionError(f'assert_eventually failed with error: {e}')

env["assert_eventually"] = assert_eventually

def assert_probability(event, expected_prob=0.5, tolerance=0.1, samples=1000):
    """Validate probability distributions with statistical testing"""
    from kinda.personality import update_chaos_state, get_personality
    from kinda.security import secure_condition_check
    import math
    try:
        # Validate parameters
        if not isinstance(expected_prob, (int, float)) or not (0 <= expected_prob <= 1):
            print(f"[?] assert_probability got weird expected_prob: {expected_prob}")
            print(f"[tip] Using default expected_prob of 0.5")
            expected_prob = 0.5
        
        if not isinstance(tolerance, (int, float)) or tolerance <= 0:
            print(f"[?] assert_probability got weird tolerance: {tolerance}")
            print(f"[tip] Using default tolerance of 0.1")
            tolerance = 0.1
        
        if not isinstance(samples, int) or samples <= 0:
            print(f"[?] assert_probability got weird samples: {samples}")
            print(f"[tip] Using default samples of 1000")
            samples = 1000
        
        # Limit samples for performance and security
        if samples > 10000:
            print(f"[?] Limiting samples to 10000 for performance (requested {samples})")
            samples = 10000
        
        # Run statistical sampling
        successes = 0
        for i in range(samples):
            # Security check for event condition
            should_proceed, event_result = secure_condition_check(event, 'assert_probability')
            if not should_proceed:
                update_chaos_state(failed=True)
                raise AssertionError(f'Unsafe event condition in assert_probability')
            
            if event_result:
                successes += 1
        
        observed_prob = successes / samples
        difference = abs(observed_prob - expected_prob)
        
        # Calculate statistical significance (binomial test approximation)
        # Standard error for binomial proportion
        se = math.sqrt(expected_prob * (1 - expected_prob) / samples)
        z_score = abs(observed_prob - expected_prob) / se if se > 0 else 0
        
        # Get personality for error messages
        personality = get_personality()
        style = personality.get_error_message_style()
        
        if difference <= tolerance:
            print(f"[stat] assert_probability passed: {observed_prob:.3f} vs expected {expected_prob:.3f} (diff: {difference:.3f}, tolerance: {tolerance:.3f})")
            update_chaos_state(failed=False)
            return True
        else:
            # Statistical failure
            if style == 'professional':
                error_msg = f'Probability assertion failed: observed {observed_prob:.3f}, expected {expected_prob:.3f} ± {tolerance:.3f} (difference: {difference:.3f}, z-score: {z_score:.2f})'
            elif style == 'friendly':
                error_msg = f'Oops! Got probability {observed_prob:.3f} but expected around {expected_prob:.3f} ± {tolerance:.3f} (off by {difference:.3f})'
            elif style == 'snarky':
                error_msg = f'Your random event is apparently not very random: {observed_prob:.3f} vs {expected_prob:.3f} ± {tolerance:.3f}. Maybe check your math?'
            else:  # chaotic
                error_msg = f'PROBABILITY FAIL! 🎲💥 Got {observed_prob:.3f}, wanted ~{expected_prob:.3f}. That\'s a {difference:.3f} swing, which is NOT kinda close!'
            
            update_chaos_state(failed=True)
            raise AssertionError(error_msg)
    except AssertionError:
        raise  # Re-raise assertion errors
    except Exception as e:
        print(f"[shrug] assert_probability got confused: {e}")
        print(f"[tip] Maybe check your event condition or parameters?")
        update_chaos_state(failed=True)
        raise AssertionError(f'assert_probability failed with error: {e}')

env["assert_probability"] = assert_probability

def drift_access(var_name, current_value):
    """Access a variable with time-based drift applied"""
    from kinda.personality import get_time_drift, update_chaos_state
    try:
        # Calculate time-based drift
        drift = get_time_drift(var_name, current_value)
        
        # Apply drift to current value
        if isinstance(current_value, (int, float)):
            result = current_value + drift
            # Maintain type consistency
            if isinstance(current_value, int):
                result = int(round(result))
        else:
            result = current_value  # Non-numeric values don't drift
        
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Drift access failed: {e}")
        print(f"[tip] Returning original value")
        update_chaos_state(failed=True)
        return current_value if current_value is not None else 0

env["drift_access"] = drift_access

def fuzzy_assign(var_name, value):
    """Fuzzy assignment with personality-adjusted fuzz and chaos tracking"""
    from kinda.personality import chaos_fuzz_range, update_chaos_state, chaos_randint
    try:
        # Check if value is numeric
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                print(f"[?] fuzzy assignment got something weird: {repr(value)}")
                print(f"[tip] Expected a number but got {type(value).__name__}")
                update_chaos_state(failed=True)
                return chaos_randint(0, 10)
        
        fuzz_min, fuzz_max = chaos_fuzz_range('int')
        fuzz = chaos_randint(fuzz_min, fuzz_max)
        result = int(value + fuzz)
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Fuzzy assignment kinda failed: {e}")
        print(f"[tip] Returning a random number because why not?")
        update_chaos_state(failed=True)
        return chaos_randint(0, 10)

env["fuzzy_assign"] = fuzzy_assign

def ish_comparison(left_val, right_val, tolerance=None):
    """Check if values are approximately equal within personality-adjusted tolerance"""
    from kinda.personality import chaos_tolerance, update_chaos_state, chaos_choice
    try:
        # Use personality-adjusted tolerance if not specified
        if tolerance is None:
            tolerance = chaos_tolerance()
        
        # Convert both values to numeric
        if not isinstance(left_val, (int, float)):
            try:
                left_val = float(left_val)
            except (ValueError, TypeError):
                print(f"[?] ish comparison got weird left value: {repr(left_val)}")
                print(f"[tip] Expected a number but got {type(left_val).__name__}")
                update_chaos_state(failed=True)
                return chaos_choice([True, False])
        
        if not isinstance(right_val, (int, float)):
            try:
                right_val = float(right_val)
            except (ValueError, TypeError):
                print(f"[?] ish comparison got weird right value: {repr(right_val)}")
                print(f"[tip] Expected a number but got {type(right_val).__name__}")
                update_chaos_state(failed=True)
                return chaos_choice([True, False])
        
        # Check if values are within tolerance
        difference = abs(left_val - right_val)
        result = difference <= tolerance
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Ish comparison kinda broke: {e}")
        print(f"[tip] Flipping a coin instead")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["ish_comparison"] = ish_comparison

def ish_value(val, variance=None):
    """Create a fuzzy value with personality-adjusted variance"""
    from kinda.personality import chaos_variance, update_chaos_state, chaos_uniform
    try:
        # Use personality-adjusted variance if not specified
        if variance is None:
            variance = chaos_variance()
        
        # Convert to float for processing
        if not isinstance(val, (int, float)):
            try:
                val = float(val)
            except (ValueError, TypeError):
                print(f"[?] ish value got something weird: {repr(val)}")
                print(f"[tip] Expected a number but got {type(val).__name__}")
                update_chaos_state(failed=True)
                return chaos_uniform(-variance, variance)
        
        # Generate fuzzy variance
        fuzz = chaos_uniform(-variance, variance)
        result = val + fuzz
        update_chaos_state(failed=False)
        
        # Return integer if input was integer, float otherwise
        return int(result) if isinstance(val, int) else result
    except Exception as e:
        print(f"[shrug] Ish value kinda confused: {e}")
        print(f"[tip] Returning random value with variance +/-{variance}")
        update_chaos_state(failed=True)
        return chaos_uniform(-variance, variance)

env["ish_value"] = ish_value

def kinda_binary(pos_prob=None, neg_prob=None, neutral_prob=None):
    """Returns 1 (positive), -1 (negative), or 0 (neutral) with personality-adjusted probabilities."""
    from kinda.personality import chaos_binary_probabilities, update_chaos_state, chaos_random, chaos_choice
    try:
        # Use personality-adjusted probabilities if not specified
        if pos_prob is None or neg_prob is None or neutral_prob is None:
            pos_prob, neg_prob, neutral_prob = chaos_binary_probabilities()
        
        # Validate probabilities
        total_prob = pos_prob + neg_prob + neutral_prob
        if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors
            print(f"[?] Binary probabilities don't add up to 1.0 (got {total_prob:.3f})")
            print(f"[tip] Normalizing: pos={pos_prob:.3f}, neg={neg_prob:.3f}, neutral={neutral_prob:.3f}")
            # Normalize probabilities
            pos_prob /= total_prob
            neg_prob /= total_prob
            neutral_prob /= total_prob
        
        rand = chaos_random()
        if rand < pos_prob:
            result = 1
        elif rand < pos_prob + neg_prob:
            result = -1
        else:
            result = 0
        
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Binary choice kinda broke: {e}")
        print(f"[tip] Defaulting to random choice between -1, 0, 1")
        update_chaos_state(failed=True)
        return chaos_choice([-1, 0, 1])

env["kinda_binary"] = kinda_binary

def kinda_bool(val):
    """Fuzzy boolean with personality-adjusted uncertainty and chaos tracking"""
    from kinda.personality import chaos_bool_uncertainty, update_chaos_state, chaos_random, chaos_choice
    try:
        # Handle None case
        if val is None:
            print(f"[?] kinda bool got None - that's kinda ambiguous")
            print(f"[tip] Choosing randomly between True and False")
            update_chaos_state(failed=True)
            return chaos_choice([True, False])
        
        # Convert value to boolean
        if isinstance(val, str):
            val_lower = val.lower().strip()
            if val_lower in ('true', '1', 'yes', 'on', 'y'):
                base_bool = True
            elif val_lower in ('false', '0', 'no', 'off', 'n'):
                base_bool = False
            else:
                print(f"[?] kinda bool got ambiguous string: {repr(val)}")
                print(f"[tip] Treating non-empty string as truthy")
                base_bool = bool(val)
        else:
            base_bool = bool(val)
        
        # Apply personality-adjusted uncertainty
        uncertainty = chaos_bool_uncertainty()
        if chaos_random() < uncertainty:
            # Introduce fuzzy uncertainty - flip the boolean sometimes
            result = not base_bool
            print(f"[fuzzy] kinda bool feeling uncertain, flipped to {result}")
            update_chaos_state(failed=True)
        else:
            result = base_bool
            update_chaos_state(failed=False)
        
        return result
    except Exception as e:
        print(f"[shrug] Kinda bool got kinda confused: {e}")
        print(f"[tip] Just flipping a coin instead")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["kinda_bool"] = kinda_bool

def kinda_float(val):
    """Fuzzy floating-point with personality-adjusted drift and chaos tracking"""
    from kinda.personality import chaos_float_drift_range, update_chaos_state, chaos_uniform
    try:
        # Check if value is numeric
        if not isinstance(val, (int, float)):
            try:
                val = float(val)
            except (ValueError, TypeError):
                print(f"[?] kinda float got something weird: {repr(val)}")
                print(f"[tip] Expected a number but got {type(val).__name__}")
                update_chaos_state(failed=True)
                return chaos_uniform(0.0, 10.0)
        
        # Convert to float
        base_val = float(val)
        
        # Apply personality-adjusted drift
        drift_min, drift_max = chaos_float_drift_range()
        drift = chaos_uniform(drift_min, drift_max)
        result = base_val + drift
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Kinda float got kinda confused: {e}")
        print(f"[tip] Just picking a random float instead")
        update_chaos_state(failed=True)
        return chaos_uniform(0.0, 10.0)

env["kinda_float"] = kinda_float

def kinda_int(val):
    """Fuzzy integer with personality-adjusted fuzz and chaos tracking"""
    from kinda.personality import chaos_fuzz_range, update_chaos_state, chaos_randint
    try:
        # Check if value is numeric
        if not isinstance(val, (int, float)):
            try:
                val = float(val)
            except (ValueError, TypeError):
                print(f"[?] kinda int got something weird: {repr(val)}")
                print(f"[tip] Expected a number but got {type(val).__name__}")
                update_chaos_state(failed=True)
                return chaos_randint(0, 10)
        
        fuzz_min, fuzz_max = chaos_fuzz_range('int')
        fuzz = chaos_randint(fuzz_min, fuzz_max)
        result = int(val + fuzz)
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Kinda int got kinda confused: {e}")
        print(f"[tip] Just picking a random number instead")
        update_chaos_state(failed=True)
        return chaos_randint(0, 10)

env["kinda_int"] = kinda_int

def maybe(condition=True):
    """Maybe evaluates a condition with personality-adjusted probability"""
    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice
    try:
        if condition is None:
            print("[?] Maybe got None as condition - treating as False")
            update_chaos_state(failed=True)
            return False
        
        # SECURITY: Use secure condition checking
        from kinda.security import secure_condition_check
        should_proceed, condition_result = secure_condition_check(condition, 'Maybe')
        if not should_proceed:
            update_chaos_state(failed=True)
            return False
        
        prob = chaos_probability('maybe')
        result = chaos_random() < prob and condition_result
        update_chaos_state(failed=not result)
        return result
    except Exception as e:
        print(f"[shrug] Maybe couldn't decide: {e}")
        print("[tip] Defaulting to random choice")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["maybe"] = maybe

def probably(condition=True):
    """Probably evaluates a condition with 70% base probability and personality adjustment"""
    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice
    try:
        if condition is None:
            print("[?] Probably got None as condition - treating as False")
            update_chaos_state(failed=True)
            return False
        
        # SECURITY: Use secure condition checking
        from kinda.security import secure_condition_check
        should_proceed, condition_result = secure_condition_check(condition, 'Probably')
        if not should_proceed:
            update_chaos_state(failed=True)
            return False
        
        prob = chaos_probability('probably')
        result = chaos_random() < prob and condition_result
        update_chaos_state(failed=not result)
        return result
    except Exception as e:
        print(f"[shrug] Probably got confused: {e}")
        print("[tip] Defaulting to random choice")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["probably"] = probably

def rarely(condition=True):
    """Rarely evaluates a condition with 15% base probability and personality adjustment"""
    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice
    try:
        if condition is None:
            print("[?] Rarely got None as condition - treating as False")
            update_chaos_state(failed=True)
            return False
        
        # SECURITY: Use secure condition checking
        from kinda.security import secure_condition_check
        should_proceed, condition_result = secure_condition_check(condition, 'Rarely')
        if not should_proceed:
            update_chaos_state(failed=True)
            return False
        
        prob = chaos_probability('rarely')
        result = chaos_random() < prob and condition_result
        update_chaos_state(failed=not result)
        return result
    except Exception as e:
        print(f"[shrug] Rarely got confused: {e}")
        print("[tip] Defaulting to random choice")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["rarely"] = rarely

def sometimes(condition=True):
    """Sometimes evaluates a condition with personality-adjusted probability"""
    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice
    try:
        if condition is None:
            print("[?] Sometimes got None as condition - treating as False")
            update_chaos_state(failed=True)
            return False
        
        # SECURITY: Use secure condition checking
        from kinda.security import secure_condition_check
        should_proceed, condition_result = secure_condition_check(condition, 'Sometimes')
        if not should_proceed:
            update_chaos_state(failed=True)
            return False
        
        prob = chaos_probability('sometimes')
        result = chaos_random() < prob and condition_result
        update_chaos_state(failed=not result)
        return result
    except Exception as e:
        print(f"[shrug] Sometimes got confused: {e}")
        print("[tip] Flipping a coin instead")
        update_chaos_state(failed=True)
        return chaos_choice([True, False])

env["sometimes"] = sometimes

def sorta_print(*args):
    """Sorta prints with personality-adjusted probability and chaos tracking"""
    from kinda.personality import chaos_probability, update_chaos_state, chaos_random, chaos_choice
    try:
        if not args:
            prob = chaos_probability('sorta_print')
            if chaos_random() < prob:
                print('[shrug] Nothing to print, I guess?')
            update_chaos_state(failed=False)
            return
        
        prob = chaos_probability('sorta_print')
        if chaos_random() < prob:
            print('[print]', *args)
            update_chaos_state(failed=False)
        else:
            # Add some personality to the "shrug" responses
            shrug_responses = [
                '[shrug] Meh...',
                '[shrug] Not feeling it right now',
                '[shrug] Maybe later?',
                '[shrug] *waves hand dismissively*',
                '[shrug] Kinda busy'
            ]
            response = chaos_choice(shrug_responses)
            print(response, *args)
            update_chaos_state(failed=True)
    except Exception as e:
        print(f'[error] Sorta print kinda broke: {e}')
        print('[fallback]', *args)
        update_chaos_state(failed=True)

env["sorta_print"] = sorta_print

def time_drift_float(var_name, initial_value):
    """Create a floating-point variable that drifts over time and usage"""
    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state, chaos_uniform
    try:
        # Convert initial value to float
        if not isinstance(initial_value, (int, float)):
            try:
                initial_value = float(initial_value)
            except (ValueError, TypeError):
                print(f"[?] time drift float got something weird: {repr(initial_value)}")
                print(f"[tip] Expected a number but got {type(initial_value).__name__}")
                update_chaos_state(failed=True)
                initial_value = chaos_uniform(0.0, 10.0)
        
        float_value = float(initial_value)
        
        # Register variable for time-based drift tracking
        register_time_variable(var_name, float_value, 'float')
        
        # Apply initial small random drift (fresh variables are mostly precise)
        initial_drift = chaos_uniform(-0.01, 0.01)
        result = float_value + initial_drift
        
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Time drift float got confused: {e}")
        print(f"[tip] Just picking a random float instead")
        update_chaos_state(failed=True)
        return chaos_uniform(0.0, 10.0)

env["time_drift_float"] = time_drift_float

def time_drift_int(var_name, initial_value):
    """Create an integer variable that drifts over time and usage"""
    from kinda.personality import register_time_variable, get_time_drift, update_chaos_state, chaos_randint, chaos_choice
    try:
        # Convert initial value to int
        if not isinstance(initial_value, (int, float)):
            try:
                initial_value = float(initial_value)
            except (ValueError, TypeError):
                print(f"[?] time drift int got something weird: {repr(initial_value)}")
                print(f"[tip] Expected a number but got {type(initial_value).__name__}")
                update_chaos_state(failed=True)
                initial_value = chaos_randint(0, 10)
        
        int_value = int(initial_value)
        
        # Register variable for time-based drift tracking
        register_time_variable(var_name, int_value, 'int')
        
        # Apply initial small random fuzz (fresh variables are mostly precise)
        initial_fuzz = chaos_choice([-1, 0, 0, 0, 1])  # Mostly no fuzz, occasional small drift
        result = int_value + initial_fuzz
        
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        print(f"[shrug] Time drift int got confused: {e}")
        print(f"[tip] Just picking a random integer instead")
        update_chaos_state(failed=True)
        return chaos_randint(0, 10)

env["time_drift_int"] = time_drift_int

def welp_fallback(primary_expr, fallback_value):
    """Execute primary expression with graceful fallback and chaos tracking"""
    from kinda.personality import update_chaos_state, get_personality
    try:
        # If primary_expr is a callable, call it
        if callable(primary_expr):
            result = primary_expr()
        else:
            result = primary_expr
        
        # Return fallback if result is None or falsy (but not 0 or False explicitly)
        if result is None:
            # Get personality-appropriate error message style
            personality = get_personality()
            style = personality.get_error_message_style()
            
            if style == 'professional':
                print(f"[welp] Expression returned None, using fallback: {repr(fallback_value)}")
            elif style == 'friendly':
                print(f"[welp] Got nothing there, trying fallback: {repr(fallback_value)}")
            elif style == 'snarky':
                print(f"[welp] Well that was useless, falling back to: {repr(fallback_value)}")
            else:  # chaotic
                print(f"[welp] *shrugs* That didn't work, whatever: {repr(fallback_value)}")
            
            update_chaos_state(failed=True)
            return fallback_value
        
        update_chaos_state(failed=False)
        return result
    except Exception as e:
        # Get personality-appropriate error message style
        personality = get_personality()
        style = personality.get_error_message_style()
        
        if style == 'professional':
            print(f"[welp] Operation failed ({type(e).__name__}: {e}), using fallback: {repr(fallback_value)}")
        elif style == 'friendly':
            print(f"[welp] Oops, that didn't work ({e}), trying: {repr(fallback_value)}")
        elif style == 'snarky':
            print(f"[welp] Predictably failed with {type(e).__name__}, fine: {repr(fallback_value)}")
        else:  # chaotic
            print(f"[welp] BOOM! {e} 💥 Whatever, here's: {repr(fallback_value)}")
        
        update_chaos_state(failed=True)
        return fallback_value

env["welp_fallback"] = welp_fallback

