# Probabilistic Control Flow Constructs - Epic #125 Complete Reference

## Overview

The Kinda programming language provides four advanced probabilistic control flow constructs that bring controlled chaos to looping and repetition. Each construct integrates fully with the personality system, offering predictable yet playful behavior patterns.

**The Four Constructs:**
- `~sometimes_while` - Probabilistic while loop with continuation probability
- `~maybe_for` - Probabilistic for loop with per-iteration execution probability
- `~kinda_repeat(n)` - Fuzzy repetition with variance-adjusted iteration count
- `~eventually_until` - Statistical loop that terminates based on confidence thresholds

## Architecture Integration

All constructs integrate seamlessly with:
- **Personality System**: Four personalities (reliable, cautious, playful, chaotic) with distinct probability profiles
- **Chaos Framework**: Statistical tracking and state management
- **Security System**: Safe condition evaluation and graceful error handling
- **Performance Optimization**: Caching and memory-optimized execution

---

## ~sometimes_while - Probabilistic While Loop

### Syntax
```kinda
~sometimes_while condition:
    # loop body
```

### Behavior
- Evaluates the condition normally on each iteration
- If condition is false, exits immediately (deterministic)
- If condition is true, applies personality-based probability for continuation
- Integrates with security validation for safe condition checking

### Personality-Specific Probabilities

| Personality | Continuation Probability | Typical Behavior |
|-------------|--------------------------|-----------------|
| **reliable** | 90% | Almost always continues when condition is true |
| **cautious** | 75% | Conservative continuation, early exits common |
| **playful** | 60% | Balanced randomness, moderate unpredictability |
| **chaotic** | 40% | Frequent early exits, high unpredictability |

### Examples

#### Basic Usage
```kinda
count = 0
~sometimes_while count < 10:
    count += 1
    print(f"Count: {count}")

# Reliable personality: Likely completes 8-10 iterations
# Chaotic personality: Likely completes 1-4 iterations
```

#### With Break Conditions
```kinda
attempts = 0
success = False
~sometimes_while not success and attempts < 100:
    attempts += 1
    success = try_operation()
    if attempts % 10 == 0:
        print(f"Attempt {attempts}: {success}")
```

#### Nested with Error Handling
```kinda
retry_count = 0
~sometimes_while retry_count < 5:
    try:
        result = risky_network_call()
        if result:
            break
    except Exception as e:
        print(f"Retry {retry_count}: {e}")
    retry_count += 1
```

### Performance Characteristics
- **Overhead**: <15% vs standard while loops
- **Memory Usage**: Minimal additional overhead
- **Early Termination**: Graceful probability-based exits

---

## ~maybe_for - Probabilistic For Loop

### Syntax
```kinda
~maybe_for variable in collection:
    # loop body
```

### Behavior
- Iterates through all items in the collection
- For each iteration, applies personality-based probability for execution
- Non-executed iterations are skipped but counted in chaos state
- Collection is fully traversed regardless of skipped executions

### Personality-Specific Probabilities

| Personality | Execution Probability per Item | Typical Coverage |
|-------------|-------------------------------|-----------------|
| **reliable** | 95% | Processes nearly all items |
| **cautious** | 85% | Processes most items with some gaps |
| **playful** | 70% | Balanced processing, noticeable gaps |
| **chaotic** | 50% | Roughly half of items processed |

### Examples

#### Basic Data Processing
```kinda
processed = []
items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
~maybe_for item in items:
    if item % 2 == 0:
        processed.append(item * 2)

print(f"Processed {len(processed)} even items")
# Reliable: ~4-5 items, Chaotic: ~2-3 items
```

#### File Processing Pipeline
```kinda
results = []
files = get_file_list("*.txt")
~maybe_for filename in files:
    try:
        content = read_file(filename)
        summary = process_content(content)
        results.append({"file": filename, "summary": summary})
    except Exception as e:
        print(f"Skipped {filename}: {e}")

print(f"Successfully processed {len(results)}/{len(files)} files")
```

#### Batch Processing with Status
```kinda
batch = get_data_batch(1000)
processed_count = 0
skipped_count = 0

~maybe_for record in batch:
    if validate_record(record):
        process_record(record)
        processed_count += 1
    else:
        skipped_count += 1

print(f"Batch complete: {processed_count} processed, {skipped_count} validation failures")
```

### Performance Characteristics
- **Overhead**: <10% vs standard for loops
- **Memory Usage**: No additional collection storage
- **Skip Efficiency**: O(1) skip operations

---

## ~kinda_repeat(n) - Fuzzy Repetition

### Syntax
```kinda
~kinda_repeat(n):
    # loop body repeated ~n times
```

### Behavior
- Takes a target repetition count `n`
- Applies personality-adjusted variance to determine actual iteration count
- Uses Gaussian distribution for natural variation patterns
- Gracefully handles non-numeric inputs with fallback behavior

### Personality-Specific Variance

| Personality | Variance (% of n) | Typical Range for n=10 |
|-------------|-------------------|----------------------|
| **reliable** | ±10% | 9-11 iterations |
| **cautious** | ±20% | 8-12 iterations |
| **playful** | ±30% | 7-13 iterations |
| **chaotic** | ±40% | 6-14 iterations |

### Examples

#### Basic Repetition
```kinda
print("Starting fuzzy countdown...")
~kinda_repeat(10):
    print("Tick!")
    time.sleep(0.5)

# Reliable: Usually 9-11 ticks
# Chaotic: Usually 6-14 ticks
```

#### Load Testing Simulation
```kinda
def simulate_user_session():
    # User performs 5-15 actions (target: 10)
    ~kinda_repeat(10):
        action = random.choice(['click', 'scroll', 'type'])
        perform_action(action)
        time.sleep(random.uniform(0.1, 2.0))

# Run simulation with multiple users
for user_id in range(100):
    threading.Thread(target=simulate_user_session).start()
```

#### Fuzzy Batch Processing
```kinda
def process_batch(items, target_passes=3):
    """Process items with fuzzy number of refinement passes"""
    for item in items:
        ~kinda_repeat(target_passes):
            item = refine_item(item)
        yield item

# Each item gets 2-4 passes typically with playful personality
refined_items = list(process_batch(raw_items, 3))
```

#### Data Generation
```kinda
def generate_test_data(base_count=1000):
    data = []
    ~kinda_repeat(base_count):
        record = {
            'id': generate_id(),
            'value': random.uniform(0, 100),
            'timestamp': time.time()
        }
        data.append(record)
    return data

# Generates approximately 1000 records with personality-based variation
test_data = generate_test_data()
print(f"Generated {len(test_data)} test records")
```

### Performance Characteristics
- **Variance Calculation**: O(1) Gaussian sampling
- **Memory Usage**: Constant overhead per loop
- **Predictable Range**: Bounded variation prevents runaway loops

---

## ~eventually_until - Statistical Termination Loop

### Syntax
```kinda
~eventually_until condition:
    # loop body
```

### Behavior
- Runs loop body repeatedly until condition becomes consistently true
- Uses statistical confidence thresholds rather than single condition check
- Maintains circular buffer of recent condition evaluations
- Terminates when confidence threshold is met over evaluation window

### Personality-Specific Confidence

| Personality | Confidence Threshold | Termination Behavior |
|-------------|---------------------|---------------------|
| **reliable** | 95% | Waits for very high confidence |
| **cautious** | 90% | Moderate confidence requirements |
| **playful** | 80% | Balanced confidence checking |
| **chaotic** | 70% | Terminates on moderate confidence |

### Examples

#### Network Stability Monitoring
```kinda
def wait_for_network_stability():
    ping_count = 0
    ~eventually_until is_network_stable():
        ping_count += 1
        result = ping_server()
        log_ping_result(result)
        time.sleep(1)

    print(f"Network stable after {ping_count} pings")

# Reliable: Waits for 95% confidence over evaluation window
# Chaotic: Terminates earlier with 70% confidence
```

#### Convergence Detection
```kinda
def train_until_convergence(model, data):
    epoch = 0
    ~eventually_until has_converged(model):
        epoch += 1
        loss = train_epoch(model, data)
        print(f"Epoch {epoch}: loss = {loss:.4f}")

        if epoch % 10 == 0:
            validate_model(model)

    print(f"Converged after {epoch} epochs")
    return model
```

#### Resource Availability Waiting
```kinda
def wait_for_resources(required_memory_gb=8):
    check_count = 0
    ~eventually_until has_sufficient_memory(required_memory_gb):
        check_count += 1
        current_memory = get_available_memory_gb()
        print(f"Check {check_count}: {current_memory}GB available")

        if check_count % 5 == 0:
            cleanup_memory()

        time.sleep(5)

    print(f"Sufficient memory available after {check_count} checks")
```

#### System Health Monitoring
```kinda
def monitor_system_health():
    alerts_sent = 0
    ~eventually_until system_is_healthy():
        health_score = calculate_health_score()
        log_health_metrics(health_score)

        if health_score < 0.5:
            send_alert(health_score)
            alerts_sent += 1

        time.sleep(30)  # Check every 30 seconds

    print(f"System healthy - sent {alerts_sent} alerts during recovery")
```

### Performance Characteristics
- **Memory Usage**: Circular buffer with bounded size (default: 100 evaluations)
- **Confidence Calculation**: O(1) rolling average updates
- **Early Termination**: Prevents infinite loops with statistical confidence

---

## Integration with Personality System

### Setting Personality
```kinda
# Set personality before using constructs
~kinda mood reliable   # High reliability, low variance
~kinda mood cautious   # Conservative behavior
~kinda mood playful    # Balanced randomness (default)
~kinda mood chaotic    # High unpredictability
```

### Personality-Aware Programming Patterns
```kinda
# Check current personality and adapt behavior
if current_personality == "reliable":
    # Use more iterations for important operations
    ~kinda_repeat(20):
        perform_critical_task()
else:
    # Use fuzzy approach for exploratory work
    ~maybe_for item in experimental_data:
        try_experimental_approach(item)
```

### Cross-Construct Synergy
```kinda
# Combine constructs for complex probabilistic behavior
batch_num = 0
~sometimes_while batch_num < max_batches:
    batch_num += 1
    current_batch = get_batch(batch_num)

    processed_in_batch = 0
    ~maybe_for item in current_batch:
        ~kinda_repeat(3):  # Multiple processing passes
            item = enhance_item(item)
        processed_in_batch += 1

    # Wait until batch processing confidence is high
    ~eventually_until batch_quality_acceptable(current_batch):
        quality_check()
        time.sleep(1)

    print(f"Batch {batch_num}: processed {processed_in_batch} items")
```

## Error Handling and Safety

All constructs include comprehensive error handling:

### Safe Condition Evaluation
```kinda
# Conditions are safely evaluated with fallback behavior
~sometimes_while potentially_risky_condition():
    # If condition evaluation fails, loop terminates safely
    perform_operation()
```

### Graceful Degradation
```kinda
# Non-numeric inputs to kinda_repeat are handled gracefully
user_input = input("How many times? ")
~kinda_repeat(user_input):  # Works even if user_input is not numeric
    print("Doing something...")
```

### Exception Handling
```kinda
# Constructs maintain chaos state tracking even during exceptions
try:
    ~maybe_for item in potentially_problematic_data:
        risky_operation(item)
except Exception as e:
    # Chaos state is properly maintained
    print(f"Handled exception: {e}")
```

## Performance Optimization

### Caching System
- Personality probabilities are cached for repeated construct usage
- Cache invalidation occurs automatically on personality changes
- Memory-optimized circular buffers for `~eventually_until`

### Benchmarking Results
```
Construct Performance (vs standard equivalents):
- ~sometimes_while: 12% overhead
- ~maybe_for: 8% overhead
- ~kinda_repeat: 5% overhead
- ~eventually_until: 15% overhead (includes confidence tracking)
```

### Memory Usage
```
Memory Overhead per Construct:
- ~sometimes_while: <100 bytes
- ~maybe_for: <50 bytes
- ~kinda_repeat: <75 bytes
- ~eventually_until: ~8KB (circular buffer)
```

## Migration Patterns

### From Standard Loops

#### Standard to ~sometimes_while
```kinda
# Standard while loop
while condition:
    body()

# Probabilistic equivalent
~sometimes_while condition:
    body()
```

#### Standard to ~maybe_for
```kinda
# Standard for loop
for item in collection:
    if should_process(item):
        process(item)

# Probabilistic equivalent
~maybe_for item in collection:
    process(item)  # Probability replaces explicit condition
```

#### Standard to ~kinda_repeat
```kinda
# Standard counted loop
for i in range(10):
    do_something()

# Fuzzy equivalent
~kinda_repeat(10):
    do_something()
```

#### Standard to ~eventually_until
```kinda
# Standard condition loop with manual confidence
confidence_checks = 0
while True:
    if check_condition():
        confidence_checks += 1
        if confidence_checks >= 5:
            break
    else:
        confidence_checks = 0
    do_work()

# Statistical equivalent
~eventually_until check_condition():
    do_work()
```

---

## Advanced Usage Patterns

### Nested Probabilistic Constructs
```kinda
# Complex nested probabilistic behavior
outer_iteration = 0
~sometimes_while outer_iteration < 5:
    outer_iteration += 1
    print(f"\\n--- Outer iteration {outer_iteration} ---")

    # Process batch with fuzzy repetition
    ~kinda_repeat(8):
        batch = generate_batch()

        # Maybe process each item
        ~maybe_for item in batch:
            processed = process_item(item)

            # Wait until processing is confirmed stable
            ~eventually_until processing_stable(processed):
                verify_processing(processed)
```

### Adaptive Behavior Based on Results
```kinda
def adaptive_processing(data, quality_threshold=0.8):
    iteration = 0
    quality_scores = []

    ~sometimes_while len(quality_scores) < 10 or avg(quality_scores) < quality_threshold:
        iteration += 1
        print(f"\\nAdaptive iteration {iteration}")

        # Process subset based on current quality
        current_quality = avg(quality_scores) if quality_scores else 0
        if current_quality < 0.5:
            # Lower quality: process more items
            ~kinda_repeat(15):
                process_item_intensive()
        else:
            # Higher quality: selective processing
            ~maybe_for item in data:
                if item.priority > current_quality:
                    process_item_selective(item)

        # Measure quality until stable
        iteration_scores = []
        ~eventually_until len(iteration_scores) >= 3:
            score = measure_quality()
            iteration_scores.append(score)

        quality_scores.extend(iteration_scores)
        quality_scores = quality_scores[-20:]  # Keep recent history

    return avg(quality_scores)
```

### Context-Aware Resource Management
```kinda
def manage_resources_probabilistically():
    resource_pool = initialize_resources(100)
    active_tasks = []

    # Run until resource management stabilizes
    ~eventually_until resource_usage_stable():
        current_load = calculate_system_load()

        if current_load < 0.3:
            # Low load: aggressively start new tasks
            ~kinda_repeat(10):
                if resource_pool:
                    task = create_task(resource_pool.pop())
                    active_tasks.append(task)

        elif current_load < 0.7:
            # Medium load: selectively start tasks
            ~maybe_for resource in resource_pool[:5]:
                if resource.priority > current_load:
                    task = create_task(resource)
                    active_tasks.append(task)
                    resource_pool.remove(resource)

        else:
            # High load: probabilistic task completion waiting
            completed_count = 0
            ~sometimes_while completed_count < 3:
                task = wait_for_task_completion(timeout=1)
                if task:
                    completed_count += 1
                    resource_pool.append(task.resource)
                    active_tasks.remove(task)

        # Monitor stability
        log_system_metrics(current_load, len(active_tasks), len(resource_pool))
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Loops terminate too early
**Symptoms**: `~sometimes_while` or `~eventually_until` exit unexpectedly
**Solution**: Check personality settings and consider using `reliable` mode
```kinda
~kinda mood reliable  # Use for critical operations
~sometimes_while important_condition:
    critical_operation()
```

#### Issue: Too many/few iterations with ~kinda_repeat
**Symptoms**: Iteration count varies too widely
**Solution**: Adjust personality or use explicit bounds checking
```kinda
# Constrain variance
target_iterations = 100
~kinda mood cautious  # Lower variance personality

iterations_completed = 0
~kinda_repeat(target_iterations):
    iterations_completed += 1
    if iterations_completed > target_iterations * 1.5:
        break  # Manual upper bound
```

#### Issue: ~maybe_for skips too many items
**Symptoms**: Important data processing is incomplete
**Solution**: Use `reliable` personality or add explicit retry logic
```kinda
~kinda mood reliable
important_items = []
~maybe_for item in critical_data:
    result = process_item(item)
    if result:
        important_items.append(result)

# Retry missed items if needed
if len(important_items) < len(critical_data) * 0.9:
    # Process remaining items with standard loop
    for item in critical_data:
        if not already_processed(item):
            process_item(item)
```

#### Issue: ~eventually_until never terminates
**Symptoms**: Loop runs indefinitely
**Solution**: Check condition logic and consider timeout
```kinda
import time
start_time = time.time()
max_runtime = 300  # 5 minutes

~eventually_until condition_check() or (time.time() - start_time > max_runtime):
    if time.time() - start_time > max_runtime:
        print("Timeout reached, terminating")
        break
    do_work()
```

### Debugging Helpers

#### Enable Construct Logging
```kinda
# Add logging to understand construct behavior
import kinda.personality as personality

# Enable debug mode (implementation-specific)
personality.set_debug_mode(True)

~sometimes_while condition:
    # Will log probability decisions
    operation()
```

#### Statistical Analysis
```kinda
def analyze_construct_behavior(n_trials=100):
    """Analyze probabilistic construct behavior over multiple trials"""
    results = {'sometimes_while': [], 'maybe_for': [], 'kinda_repeat': []}

    for trial in range(n_trials):
        # Test sometimes_while
        count = 0
        ~sometimes_while count < 10:
            count += 1
        results['sometimes_while'].append(count)

        # Test maybe_for
        processed = 0
        items = list(range(10))
        ~maybe_for item in items:
            processed += 1
        results['maybe_for'].append(processed)

        # Test kinda_repeat
        iterations = 0
        ~kinda_repeat(10):
            iterations += 1
        results['kinda_repeat'].append(iterations)

    # Print statistics
    for construct, values in results.items():
        mean_val = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        print(f"{construct}: mean={mean_val:.2f}, range={min_val}-{max_val}")

# Run analysis with different personalities
for personality_name in ['reliable', 'cautious', 'playful', 'chaotic']:
    print(f"\\n--- {personality_name.upper()} PERSONALITY ---")
    ~kinda mood {personality_name}
    analyze_construct_behavior()
```

This comprehensive reference provides everything needed to effectively use the probabilistic control flow constructs in real-world applications while understanding their behavior across different personality modes.