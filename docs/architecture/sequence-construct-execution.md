# Kinda-Lang Construct Execution Flow

## Fuzzy Construct Execution Sequence

This diagram shows how fuzzy constructs interact with the personality system during runtime execution.

```mermaid
sequenceDiagram
    participant Code as Generated Python Code
    participant Construct as Fuzzy Construct<br/>(e.g., kinda_int, sometimes)
    participant Personality as Personality System<br/>(kinda/personality.py)
    participant Random as Random Module
    participant Output as Console Output

    Note over Code: Example: ~kinda int x = 42
    Code->>Construct: kinda_int(42)
    
    Note over Construct: Personality Integration (constructs.py:12-35)
    Construct->>Personality: chaos_fuzz_range('int')
    Personality->>Personality: Get profile.int_fuzz_range (-1, 1)
    Personality->>Personality: Apply chaos_amplifier (e.g., 1.8 for chaotic)
    Personality->>Personality: Scale range: (-1.8, 1.8) → (-2, 2)
    Personality-->>Construct: fuzz_range = (-2, 2)
    
    Construct->>Random: randint(fuzz_min, fuzz_max)
    Random-->>Construct: fuzz = 1
    
    Construct->>Construct: result = int(42 + 1) = 43
    Construct->>Personality: update_chaos_state(failed=False)
    Personality->>Personality: instability_level *= 0.95 (recovery)
    Personality->>Personality: execution_count += 1
    
    Construct-->>Code: return 43

    Note over Code: Example: ~sometimes (score > 50) { print("High score!") }
    Code->>Construct: sometimes(score > 50)
    
    Note over Construct: Conditional Logic (constructs.py:82-100)
    Construct->>Personality: chaos_probability('sometimes', condition)
    Personality->>Personality: base_prob = profile.sometimes_base (0.5)
    
    alt Chaotic personality (chaos_amplifier > 1.0)
        Personality->>Personality: Pull probability toward 0.5 (unpredictable)
        Personality->>Personality: adjusted = 0.5 - (0.5-0.3) * 0.8 = 0.34
    else Reliable personality (chaos_amplifier < 1.0)  
        Personality->>Personality: Pull probability toward success (0.95)
        Personality->>Personality: adjusted = 0.5 + (1.0-0.5) * 0.8 = 0.9
    end
    
    Note over Personality: Apply Cascade Effects
    Personality->>Personality: Apply instability: prob *= (1 - instability * cascade_strength)
    Personality-->>Construct: final_probability = 0.32 (chaotic + some instability)
    
    Construct->>Random: random.random()
    Random-->>Construct: 0.67 (fails the 0.32 threshold)
    
    Construct->>Construct: result = False (condition not executed)
    Construct->>Personality: update_chaos_state(failed=True)
    Personality->>Personality: instability_level += 0.1 * cascade_strength
    
    Construct-->>Code: return False
    Code->>Code: Skip the print("High score!") block

    Note over Code: Example: ~sorta print("Debug info")
    Code->>Construct: sorta_print("Debug info")
    
    Construct->>Personality: chaos_probability('sorta_print')
    Personality-->>Construct: probability = 0.6 (chaotic mode reduces print reliability)
    
    Construct->>Random: random.random()
    Random-->>Construct: 0.85 (fails the 0.6 threshold)
    
    Note over Construct: Personality-Aware Error Message (constructs.py:60-70)
    Construct->>Random: choice(shrug_responses)
    Random-->>Construct: "[shrug] Kinda busy"
    
    Construct->>Output: print("[shrug] Kinda busy", "Debug info")
    Construct->>Personality: update_chaos_state(failed=True)
    
    Construct-->>Code: return None

    Note over Code: Example: risky_operation() ~welp 0
    Code->>Construct: welp_fallback(lambda: risky_operation(), 0)
    
    Construct->>Code: primary_expr() # Call risky_operation()
    Code-->>Construct: raises ValueError("Network timeout")
    
    Note over Construct: Personality-Aware Error Handling (constructs.py:321-332)
    Construct->>Personality: get_personality().get_error_message_style()
    Personality-->>Construct: "chaotic" (snark_level = 0.9)
    
    Construct->>Output: print("[welp] BOOM! Network timeout 💥 Whatever, here's: 0")
    Construct->>Personality: update_chaos_state(failed=True)
    Personality->>Personality: instability_level += 0.1 * cascade_strength
    
    Construct-->>Code: return 0
```

## State Tracking and Cascade Effects

```mermaid
sequenceDiagram
    participant Construct1 as First Construct
    participant Construct2 as Second Construct  
    participant Construct3 as Third Construct
    participant Personality as Personality System

    Note over Personality: Initial State: instability_level = 0.0

    Construct1->>Personality: update_chaos_state(failed=True)
    Personality->>Personality: instability_level += 0.1 * 0.5 = 0.05
    Note over Personality: System becoming unstable

    Construct2->>Personality: chaos_probability('maybe')
    Personality->>Personality: base_prob = 0.4 (chaotic profile)
    Personality->>Personality: cascade_impact = 0.05 * 0.5 = 0.025
    Personality->>Personality: adjusted = 0.4 * (1 - 0.025) = 0.39
    Personality-->>Construct2: Lower probability due to instability
    
    Construct2->>Personality: update_chaos_state(failed=True)
    Personality->>Personality: instability_level += 0.05 = 0.1
    Note over Personality: Instability cascading

    Construct3->>Personality: chaos_probability('sometimes')
    Personality->>Personality: base_prob = 0.3, cascade_impact = 0.1 * 0.5 = 0.05
    Personality->>Personality: adjusted = 0.3 * (1 - 0.05) = 0.285
    Personality-->>Construct3: Even lower probability
    
    Construct3->>Personality: update_chaos_state(failed=False)
    Personality->>Personality: instability_level *= 0.95 = 0.095
    Note over Personality: Slow recovery from instability
```

## Key Runtime Characteristics

### Personality-Driven Behavior
- **Dynamic Adjustment**: Each construct queries personality for current parameters
- **Consistent Philosophy**: All constructs share the same chaos level and error style
- **Cascade Effects**: Failed operations increase system instability, affecting subsequent operations

### State Tracking
- **Execution Count**: Tracks total operations for time-based effects
- **Instability Level**: Accumulates from failures, slowly recovers from successes
- **Chaos Amplification**: Global multiplier affects all randomness and variance

### Error Handling Hierarchy
1. **Professional** (reliable): "Expression returned None, using fallback"
2. **Friendly** (cautious): "Got nothing there, trying fallback"  
3. **Snarky** (playful): "Well that was useless, falling back to"
4. **Chaotic** (chaotic): "BOOM! Network timeout 💥 Whatever, here's"

This design creates emergent complexity where individual construct failures affect overall system behavior, simulating realistic software degradation patterns.