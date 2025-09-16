# Quick Start Guide - Probabilistic Control Flow (Epic #125)

Get up and running with probabilistic control flow constructs in 30 minutes! This guide provides the fastest path to productive use of the four new constructs.

## 30-Second Overview

Epic #125 adds four probabilistic control flow constructs:

```kinda
~sometimes_while condition:    # Probabilistic while loop
    do_work()

~maybe_for item in collection:  # Probabilistic for loop
    process(item)

~kinda_repeat(10):             # Fuzzy repetition
    perform_action()

~eventually_until condition:   # Statistical termination loop
    improve_system()
```

## 5-Minute Quick Start

### Step 1: Choose Your Personality

```kinda
# Set behavior profile (affects all constructs)
~kinda mood reliable   # Predictable, high success rates
~kinda mood cautious   # Conservative, moderate rates
~kinda mood playful    # Balanced, default behavior
~kinda mood chaotic    # Unpredictable, experimental
```

### Step 2: Try Each Construct

```kinda
# 1. ~sometimes_while: Loop with probabilistic continuation
count = 0
~sometimes_while count < 10:
    count += 1
    print(f"Count: {count}")
    # May exit early based on personality

# 2. ~maybe_for: Process items probabilistically
items = [1, 2, 3, 4, 5]
processed = []
~maybe_for item in items:
    processed.append(item * 2)
    # Some items may be skipped

print(f"Processed {len(processed)} out of {len(items)} items")

# 3. ~kinda_repeat: Fuzzy iteration count
operations_completed = 0
~kinda_repeat(5):  # Usually 4-6 iterations
    operations_completed += 1
    perform_operation()

print(f"Completed {operations_completed} operations")

# 4. ~eventually_until: Loop until statistical confidence
attempts = 0
~eventually_until system_ready():
    attempts += 1
    improve_system()

print(f"System ready after {attempts} attempts")
```

## 15-Minute Real-World Example

### Resilient Data Processing Pipeline

```kinda
def process_data_pipeline():
    ~kinda mood cautious  # Conservative for data processing

    print("Starting resilient data processing...")

    # Generate sample data
    dataset = []
    ~kinda_repeat(100):  # ~90-110 records with cautious personality
        record = {
            'id': generate_id(),
            'value': random.uniform(0, 100),
            'quality': random.uniform(0.5, 1.0)
        }
        dataset.append(record)

    print(f"Generated {len(dataset)} records")

    # Process with multiple retry stages
    stage1_results = []
    stage2_results = []

    # Stage 1: Initial processing with probabilistic filtering
    ~maybe_for record in dataset:  # ~85% processing rate with cautious
        if record['quality'] > 0.7:  # Quality threshold
            stage1_results.append(record)

    print(f"Stage 1: {len(stage1_results)} records passed initial filter")

    # Stage 2: Intensive processing with retry logic
    batch_count = 0
    ~sometimes_while batch_count < 10 and len(stage2_results) < len(stage1_results) * 0.8:
        batch_count += 1
        print(f"Processing batch {batch_count}")

        # Process remaining records
        remaining = [r for r in stage1_results if r not in stage2_results]

        ~maybe_for record in remaining[:10]:  # Process in small batches
            # Retry logic with fuzzy attempts
            success = False
            ~kinda_repeat(3):  # 2-4 attempts typically
                if simulate_processing(record):
                    success = True
                    break

            if success:
                stage2_results.append(record)

    print(f"Stage 2: {len(stage2_results)} records successfully processed")

    # Stage 3: Quality assurance with statistical confidence
    qa_cycles = 0
    quality_samples = []

    ~eventually_until len(quality_samples) >= 20 and average_quality(quality_samples) > 0.85:
        qa_cycles += 1

        # Sample some results for quality checking
        ~maybe_for result in stage2_results[-10:]:  # Check recent results
            quality_score = assess_quality(result)
            quality_samples.append(quality_score)

        # Keep only recent samples for relevance
        quality_samples = quality_samples[-30:]

    final_quality = average_quality(quality_samples) if quality_samples else 0

    print(f"Quality assurance complete after {qa_cycles} cycles")
    print(f"Final quality score: {final_quality:.3f}")
    print(f"Processing complete: {len(stage2_results)}/{len(dataset)} records ({len(stage2_results)/len(dataset):.1%})")

    return stage2_results

# Helper functions
def generate_id():
    return f"rec_{random.randint(1000, 9999)}"

def simulate_processing(record):
    # 80% success rate with some variation
    return random.random() > 0.2

def assess_quality(result):
    return random.uniform(0.6, 1.0)

def average_quality(samples):
    return sum(samples) / len(samples) if samples else 0

# Run the example
if __name__ == "__main__":
    import random
    processed_data = process_data_pipeline()
```

## 30-Minute Complete Integration

### Smart System Monitor with All Four Constructs

```kinda
import time
import random

def smart_system_monitor():
    """Complete example using all four probabilistic control flow constructs."""

    ~kinda mood playful  # Balanced behavior for monitoring

    print("🚀 Starting Smart System Monitor")

    # System state
    system_health = 0.6  # Start with moderate health
    monitoring_cycles = 0
    alerts_sent = 0
    improvements_made = 0

    # Main monitoring loop
    ~sometimes_while monitoring_cycles < 50 and system_health < 0.95:
        monitoring_cycles += 1
        print(f"\n--- Monitoring Cycle {monitoring_cycles} ---")
        print(f"Current system health: {system_health:.3f}")

        # Collect metrics from multiple sources
        metrics_collected = []
        metric_sources = ['cpu', 'memory', 'disk', 'network', 'database']

        ~maybe_for source in metric_sources:
            # Simulate metric collection (may fail or be skipped)
            metric_value = random.uniform(0.3, 0.9)
            metrics_collected.append({
                'source': source,
                'value': metric_value,
                'timestamp': time.time()
            })
            print(f"  📊 {source}: {metric_value:.3f}")

        print(f"  Collected {len(metrics_collected)} metrics")

        # Analyze metrics and send alerts if needed
        low_metrics = [m for m in metrics_collected if m['value'] < 0.6]

        if low_metrics:
            print(f"  ⚠️  {len(low_metrics)} metrics below threshold")

            # Send alerts with fuzzy retry logic
            ~kinda_repeat(len(low_metrics)):  # Fuzzy number of alerts
                alert_sent = send_alert(low_metrics)
                if alert_sent:
                    alerts_sent += 1

        # System improvement attempts
        if system_health < 0.8:
            print("  🔧 System needs improvement")

            # Keep trying improvements until health is better
            improvement_attempts = 0
            ~eventually_until system_health > 0.8 or improvement_attempts >= 5:
                improvement_attempts += 1

                # Try multiple improvement strategies
                ~maybe_for strategy in ['cleanup', 'optimize', 'restart', 'scale']:
                    if attempt_improvement(strategy):
                        improvement_delta = random.uniform(0.05, 0.15)
                        system_health = min(1.0, system_health + improvement_delta)
                        improvements_made += 1
                        print(f"    ✅ {strategy} successful (+{improvement_delta:.3f})")

                        if system_health > 0.8:
                            break
                    else:
                        print(f"    ❌ {strategy} failed")

            print(f"  Improvement attempts: {improvement_attempts}, final health: {system_health:.3f}")

        # Adaptive monitoring frequency
        if system_health > 0.9:
            sleep_time = 3  # Slower monitoring when healthy
        elif system_health > 0.7:
            sleep_time = 2  # Normal monitoring
        else:
            sleep_time = 1  # Fast monitoring when unhealthy

        time.sleep(sleep_time)

    # Final report
    print(f"\n=== Monitoring Session Complete ===")
    print(f"Total cycles: {monitoring_cycles}")
    print(f"Alerts sent: {alerts_sent}")
    print(f"Improvements made: {improvements_made}")
    print(f"Final system health: {system_health:.3f}")

    # Success criteria
    if system_health >= 0.90:
        print("✅ System monitoring successful - high health achieved!")
    elif system_health >= 0.75:
        print("✓ System monitoring partially successful - acceptable health")
    else:
        print("⚠️  System monitoring needs attention - health still low")

    return {
        'final_health': system_health,
        'cycles': monitoring_cycles,
        'alerts': alerts_sent,
        'improvements': improvements_made
    }

def send_alert(low_metrics):
    """Simulate sending an alert."""
    print(f"    📧 Sending alert for {len(low_metrics)} issues...")
    # 85% success rate
    return random.random() > 0.15

def attempt_improvement(strategy):
    """Simulate system improvement attempt."""
    success_rates = {
        'cleanup': 0.8,
        'optimize': 0.7,
        'restart': 0.9,
        'scale': 0.6
    }
    return random.random() < success_rates.get(strategy, 0.5)

# Run the complete example
if __name__ == "__main__":
    results = smart_system_monitor()

    print(f"\n🎯 Try different personalities:")
    print("  ~kinda mood reliable  # More thorough monitoring")
    print("  ~kinda mood chaotic   # More experimental approaches")
```

## Key Concepts Summary

### When to Use Each Construct

1. **~sometimes_while**: Variable continuation based on conditions
   - Monitoring loops that should adapt to system state
   - Retry mechanisms with probabilistic backoff
   - Batch processing with dynamic termination

2. **~maybe_for**: Probabilistic item processing
   - Data sampling and filtering
   - Load testing with realistic user behavior
   - Resource-constrained processing

3. **~kinda_repeat**: Fuzzy iteration counts
   - Approximate operations (like "do this about 10 times")
   - Natural variation in repetitive tasks
   - Simulation with realistic variance

4. **~eventually_until**: Statistical confidence-based termination
   - Convergence detection
   - Quality assurance with confidence thresholds
   - System readiness checking

### Personality Impact Quick Reference

| Construct | Reliable | Cautious | Playful | Chaotic |
|-----------|----------|----------|---------|---------|
| **~sometimes_while** | 90% continue | 75% continue | 60% continue | 40% continue |
| **~maybe_for** | 95% execute | 85% execute | 70% execute | 50% execute |
| **~kinda_repeat(n)** | ±10% variance | ±20% variance | ±30% variance | ±40% variance |
| **~eventually_until** | 95% confidence | 90% confidence | 80% confidence | 70% confidence |

### Best Practices

1. **Set personality once** per execution context
2. **Layer constructs** for complex behavior
3. **Test statistical properties** with multiple runs
4. **Use appropriate construct** for the use case
5. **Consider performance** for tight loops

## Next Steps

1. **Run the examples** above to see probabilistic behavior
2. **Experiment with personalities** to understand their impact
3. **Check out the comprehensive examples** in `examples/probabilistic_control_flow/`
4. **Read the full documentation** in `docs/PROBABILISTIC_CONTROL_FLOW.md`
5. **Review performance considerations** in `docs/PERFORMANCE_GUIDE.md`

## Common Patterns

```kinda
# Pattern 1: Resilient processing with retries
~maybe_for item in data:
    success = False
    ~kinda_repeat(3):  # Fuzzy retry count
        if try_process(item):
            success = True
            break
    if not success:
        handle_failure(item)

# Pattern 2: Adaptive monitoring
~sometimes_while system_needs_monitoring():
    check_system()
    ~eventually_until system_stable():
        apply_fix()

# Pattern 3: Load testing with realistic patterns
~maybe_for user in user_pool:
    ~kinda_repeat(user.expected_actions):
        simulate_user_action(user)
```

You're now ready to use probabilistic control flow constructs effectively! Remember: embrace controlled chaos for more resilient, adaptive, and realistic systems.