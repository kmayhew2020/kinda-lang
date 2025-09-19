# Probabilistic Control Flow Examples

This directory contains 10 comprehensive real-world examples demonstrating the four probabilistic control flow constructs introduced in Epic #125:

- `~sometimes_while` - Probabilistic while loop with continuation probability
- `~maybe_for` - Probabilistic for loop with per-iteration execution probability
- `~kinda_repeat(n)` - Fuzzy repetition with variance-adjusted iteration count
- `~eventually_until` - Statistical loop that terminates based on confidence thresholds

## Examples Overview

### 1. Fuzzy Batch Processing (`01_fuzzy_batch_processing.knda`)
**Constructs Used:** `~sometimes_while`, `~maybe_for`, `~kinda_repeat`

Demonstrates data batch processing with probabilistic retry logic. Shows how to:
- Process multiple data batches with fuzzy continuation
- Handle items probabilistically with retry mechanisms
- Use fuzzy repetition for robust processing attempts
- Adapt behavior based on personality settings

**Key Learning:** Real-world data processing often benefits from probabilistic approaches that handle variable conditions gracefully.

### 2. Probabilistic System Monitoring (`02_probabilistic_system_monitoring.knda`)
**Constructs Used:** `~eventually_until`, `~sometimes_while`, `~maybe_for`

System health monitoring with adaptive checking frequencies. Features:
- Statistical confidence-based health assessment
- Probabilistic maintenance operations
- Adaptive monitoring intervals based on system state
- Emergency response with cascading health checks

**Key Learning:** System monitoring can be more effective with probabilistic thresholds rather than rigid binary checks.

### 3. Fuzzy Load Testing (`03_fuzzy_load_testing.knda`)
**Constructs Used:** `~kinda_repeat`, `~maybe_for`, `~sometimes_while`

Realistic load testing with probabilistic user behavior simulation. Includes:
- Fuzzy user action counts for realistic traffic patterns
- Probabilistic action selection mimicking real user behavior
- Ramp-up and sustained load testing with natural variation
- Spike testing with burst traffic simulation

**Key Learning:** Load testing with probabilistic patterns creates more realistic stress scenarios than deterministic approaches.

### 4. ETL Pipeline Recovery (`04_etl_pipeline_recovery.knda`)
**Constructs Used:** All 4 constructs working together

Comprehensive ETL pipeline with probabilistic error recovery. Shows:
- Data extraction, transformation, and loading with fuzzy retry logic
- Statistical validation of data processing success
- Multi-layered error recovery strategies
- Performance optimization through probabilistic processing

**Key Learning:** ETL pipelines benefit from fuzzy error handling that adapts to varying data quality and system conditions.

### 5. Network Request Handling (`05_network_request_handling.knda`)
**Constructs Used:** `~eventually_until`, `~kinda_repeat`, `~maybe_for`

HTTP client with probabilistic retry and timeout behavior. Features:
- Adaptive timeout strategies based on network conditions
- Fuzzy backoff timing for request retries
- Batch request handling with probabilistic concurrency
- Circuit breaker patterns with statistical decision making

**Key Learning:** Network resilience improves with probabilistic retry strategies that adapt to changing conditions.

### 6. Data Processing Validation (`06_data_processing_validation.knda`)
**Constructs Used:** `~maybe_for`, `~eventually_until`, `~kinda_repeat`

Data validation pipeline with fuzzy quality checks. Includes:
- Multi-dimensional data quality assessment
- Probabilistic improvement cycles until quality targets are met
- Statistical confidence in data validation decisions
- Adaptive validation intensity based on data characteristics

**Key Learning:** Data quality assurance benefits from probabilistic validation that considers uncertainty and confidence levels.

### 7. Adaptive Resource Management (`07_adaptive_resource_management.knda`)
**Constructs Used:** `~sometimes_while`, `~eventually_until`, `~maybe_for`

Dynamic resource allocation with probabilistic scaling. Features:
- Adaptive scaling decisions based on utilization patterns
- Probabilistic task scheduling with priority awareness
- Resource preemption strategies for critical workloads
- Statistical monitoring for scaling stability

**Key Learning:** Resource management systems perform better with probabilistic scaling that considers uncertainty in demand patterns.

### 8. Distributed Consensus (`08_distributed_consensus.knda`)
**Constructs Used:** `~eventually_until`, `~maybe_for`, `~sometimes_while`

Consensus algorithm with fuzzy agreement thresholds. Demonstrates:
- Leader election with probabilistic candidate selection
- Statistical confidence in consensus achievement
- Fault tolerance with probabilistic recovery mechanisms
- Network partition handling with adaptive timeouts

**Key Learning:** Distributed systems benefit from probabilistic consensus mechanisms that handle uncertainty in network conditions.

### 9. Machine Learning Training (`09_machine_learning_training.knda`)
**Constructs Used:** `~kinda_repeat`, `~eventually_until`, `~maybe_for`

ML model training with probabilistic optimization. Includes:
- Hyperparameter optimization with fuzzy search strategies
- Training with adaptive epoch counts based on convergence
- Ensemble training with probabilistic diversity
- Early stopping with statistical confidence thresholds

**Key Learning:** ML training often benefits from probabilistic approaches that handle the inherent uncertainty in optimization.

### 10. Chaos Testing Framework (`10_chaos_testing_framework.knda`)
**Constructs Used:** All 4 constructs comprehensively

Chaos engineering with probabilistic failure injection. Features:
- Comprehensive failure type simulation with varying intensities
- Cascading failure detection and analysis
- Recovery validation with statistical confidence
- System resilience assessment through probabilistic testing

**Key Learning:** Chaos engineering is most effective with probabilistic failure patterns that reflect real-world uncertainty.

## Running the Examples

### Prerequisites
```bash
# Ensure you're in the kinda-lang directory
cd ~/kinda-lang

# Activate the Python environment
source ~/.venv/bin/activate

# Set personality (optional, defaults to 'playful')
~kinda mood reliable    # For more predictable behavior
~kinda mood chaotic     # For more unpredictable behavior
```

### Running Individual Examples
```bash
# Run any example directly
python -m kinda examples/probabilistic_control_flow/01_fuzzy_batch_processing.knda

# Or use the kinda interpreter
kinda run examples/probabilistic_control_flow/02_probabilistic_system_monitoring.knda
```

### Batch Execution
```bash
# Run all examples with different personalities
for personality in reliable cautious playful chaotic; do
  echo "\\n=== Running with $personality personality ==="
  ~kinda mood $personality
  for example in examples/probabilistic_control_flow/*.knda; do
    echo "Running $example..."
    kinda run $example
  done
done
```

## Personality Impact Demonstrations

Each example demonstrates how different personalities affect behavior:

### Reliable Personality
- Higher continuation probabilities in `~sometimes_while`
- More items processed in `~maybe_for`
- Lower variance in `~kinda_repeat`
- Higher confidence thresholds in `~eventually_until`

### Cautious Personality
- Moderate probabilities with conservative thresholds
- Balanced processing with safety margins
- Reasonable variance levels
- Moderate confidence requirements

### Playful Personality (Default)
- Standard probability distributions
- Balanced exploration vs exploitation
- Natural variance levels
- Adaptive confidence thresholds

### Chaotic Personality
- Lower continuation probabilities
- More items skipped or terminated early
- Higher variance and unpredictability
- Lower confidence thresholds (faster termination)

## Example Complexity Progression

The examples are designed with increasing complexity:

1. **Basic Usage (Examples 1-3):** Single-construct focus with clear use cases
2. **Integration (Examples 4-6):** Multiple constructs working together
3. **Advanced Patterns (Examples 7-8):** Complex real-world scenarios
4. **Comprehensive (Examples 9-10):** All constructs in sophisticated applications

## Common Patterns Demonstrated

### Error Recovery
- Fuzzy retry counts with `~kinda_repeat`
- Statistical confidence in recovery with `~eventually_until`
- Probabilistic fallback strategies with `~maybe_for`

### Performance Optimization
- Adaptive resource allocation
- Probabilistic load balancing
- Statistical performance monitoring

### System Resilience
- Graceful degradation under load
- Fault tolerance with recovery
- Chaos engineering validation

### Data Processing
- Quality-based processing decisions
- Statistical validation thresholds
- Adaptive processing strategies

## Testing the Examples

Each example includes:
- Realistic simulation parameters
- Comprehensive error handling
- Performance metrics collection
- Personality impact demonstration

Run examples with different personalities to observe behavioral changes:

```bash
# Conservative processing
~kinda mood reliable
python -m kinda examples/probabilistic_control_flow/04_etl_pipeline_recovery.knda

# Aggressive processing
~kinda mood chaotic
python -m kinda examples/probabilistic_control_flow/04_etl_pipeline_recovery.knda
```

## Integration with Epic #124

These examples also demonstrate integration with Epic #124 constructs:
- `~kinda int`, `~kinda float`, `~kinda bool` for fuzzy data generation
- `~ish` comparisons for approximate value matching
- `~sorta_if` conditions for fuzzy decision making

This creates a comprehensive probabilistic programming environment where data, conditions, and control flow all embrace controlled chaos.

## Learning Outcomes

After working through these examples, you'll understand:

1. **When to use each construct:** Appropriate scenarios for different probabilistic control flow patterns
2. **Personality impact:** How different personalities affect system behavior and outcomes
3. **Integration patterns:** Combining multiple constructs for complex real-world applications
4. **Performance considerations:** Trade-offs between predictability and flexibility
5. **Testing strategies:** Validating probabilistic systems with statistical methods

## Next Steps

- Modify examples to explore different parameter ranges
- Create hybrid examples combining multiple use cases
- Implement your own probabilistic control flow patterns
- Contribute additional real-world examples to the collection

These examples provide a solid foundation for understanding and applying probabilistic control flow constructs in real-world scenarios while maintaining the balance between chaos and control that defines the Kinda programming language.