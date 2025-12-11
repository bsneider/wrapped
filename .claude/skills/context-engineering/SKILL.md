# Context Engineering Skill

Use this skill when analyzing, optimizing, or understanding LLM context window usage, context rot, and memory management patterns.

## When to Use

- Analyzing context compaction/summarization patterns
- Detecting context rot symptoms
- Optimizing prompt engineering for large contexts
- Understanding context utilization metrics
- Diagnosing context-related performance issues

## Key Concepts

### Context Rot

LLMs do not maintain consistent performance across input lengths. Even on simple tasks, performance degrades non-uniformly as input length grows.

**Research Finding (NoLiMa Benchmark)**: At 32k tokens, 11 out of 12 tested models dropped below 50% of their performance in short contexts.

### The "Lost in the Middle" Effect

LLMs are more likely to recall information at the beginning or end of prompts rather than content in the middle. Critical information placed mid-context may be effectively invisible during generation.

**Implication**: Place important context at the start or end of prompts, not the middle.

### Context Compaction (Summarization)

When context windows fill up, Claude summarizes the conversation to continue. This is tracked in JSONL as:

```json
{"type": "summary", "summary": "Brief description of summarized content", "leafUuid": "..."}
```

**Metrics to Track**:
- `total_summaries`: Total compactions across all sessions
- `sessions_with_compaction`: Sessions that hit context limits
- `max_compactions_in_session`: Deepest work session (most compactions)
- `tokens_per_compaction`: Average tokens consumed before reset

## Key Metrics

### Input/Output Ratio
```
input_output_ratio = total_input_tokens / total_output_tokens
```
- High (>5x): Context-heavy usage (lots of code reading, large files)
- Balanced (2-5x): Normal interactive coding
- Low (<2x): Output-heavy (lots of code generation)

### Context Pressure
Estimated context utilization relative to model limits:
```python
estimated_context_limit = 200000  # Conservative for Claude
if session_tokens > estimated_context_limit * 0.8:
    context_pressure_detected = True
```

### Compaction Rate
```
context_collapse_rate = total_summaries / total_sessions
```
- <0.1: Efficient short sessions
- 0.1-0.3: Normal deep work
- >0.3: Heavy context usage, consider breaking tasks

## Detection Patterns

### High Context Rot Risk
```python
if (input_output_ratio > 6 and
    avg_tokens_per_message > 3000 and
    sessions_with_compaction / total_sessions > 0.2):
    # High context rot risk
```

### Marathon Coding Sessions
```python
if session.summary_count >= 3:
    # Deep dive session, multiple context resets
```

## Best Practices

### Slot-Based Memory
Use structured JSON sections instead of raw transcripts:
```json
{
  "instructions": "...",
  "memory_slots": {...},
  "retrieved_facts": [...],
  "tool_outputs": [...]
}
```

### Context Window Management
- At 85-90% occupancy, summarize or drop least-valuable chunks
- Apply absolute cap before exceeding provider limits
- Use RAG to offload historical context

### Retrieval Augmentation
- Track Retrieval Recall@K when using RAG
- Monitor summary drift (semantic delta between original and summary)

## Metrics Formulas

### Tokens Per Compaction
Average tokens consumed before a context reset:
```python
tokens_per_compaction = (total_input + total_output) / total_summaries
```

### Average Tokens Per Message
```python
avg_tokens = (total_input + total_output) / total_messages
```
- <500: Concise messages
- 500-2000: Normal
- >2000: Verbose/large code blocks

## Research Sources

- Chroma Research: "Context Rot: How Increasing Input Tokens Impacts LLM Performance"
- NoLiMa Benchmark: Non-uniform performance degradation study
- Andrej Karpathy: "Context engineering is the delicate art of filling the context window with just the right information"

## Related Files

- `analyzer.py`: Extracts context metrics from JSONL
- `generator.py`: Visualizes context engineering metrics
- `metrics_db.py`: Stores context metrics history
