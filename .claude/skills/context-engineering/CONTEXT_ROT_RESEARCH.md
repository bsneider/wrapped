# Context Rot Research Summary

## Overview

Context rot refers to the degradation of LLM performance as input context length increases. This is a fundamental limitation that affects all current large language models.

## Key Research Findings

### 1. Non-Uniform Performance Degradation

**Source**: Chroma Research - NoLiMa Benchmark

LLMs do not process context uniformly:
- Performance varies significantly as input length changes
- Even simple tasks show degradation at longer contexts
- At 32k tokens, 11/12 tested models dropped below 50% of short-context performance

### 2. Needle-Question Similarity Impact

Lower semantic similarity between questions and answers accelerates performance decline:
- PG essay needles: 0.445-0.775 similarity range
- arXiv topics: 0.521-0.829 similarity range
- Performance degrades faster with low-similarity pairs as context grows

### 3. Distractor Effects

The presence of irrelevant information compounds degradation:
- Single distractors reduce accuracy vs needle-only baselines
- Four distractors cause further compound degradation
- Non-uniform impact across distractor types
- Claude models: lowest hallucination rates
- GPT models: highest hallucination rates (confident incorrect responses)

### 4. Haystack Structure Paradox

Counter-intuitively, models perform BETTER on shuffled (incoherent) haystacks than logically structured ones. This suggests attention mechanisms are disrupted by narrative flow.

### 5. Position Accuracy

Information position significantly affects recall:
- Words placed early in sequences: higher detection rates
- Words in middle/end of long contexts: significantly lower accuracy
- This is the "lost in the middle" effect

## Model-Specific Behaviors

### Claude Models
- Conservative abstention under ambiguity
- Lower hallucination rates
- Better handling of structured prompts

### GPT Models
- Generate confident incorrect responses with distractors
- Higher hallucination frequency
- More susceptible to distractor content

## Useful Metrics for Tracking

### 1. Cosine Similarity Scores
Track question-answer similarity across multiple embedding models to predict performance.

### 2. Normalized Levenshtein Distance
Measure output fidelity for copy/retrieval tasks.

### 3. Position Accuracy Percentages
Identify information location effects - where in context does information need to be to be recalled?

### 4. Hallucination Frequency Rates
Track by model family and context length.

### 5. Word Count Differences
Compare input vs output to detect under/over-generation patterns.

### 6. Refusal Rates
Track across input length ranges to understand model confidence thresholds.

## Context Management Strategies

### 1. Slot-Based Memory
Instead of raw transcripts, use structured memory:
```json
{
  "system_instructions": "...",
  "conversation_slots": {
    "current_task": "...",
    "relevant_code": "...",
    "decisions_made": [...]
  },
  "retrieved_context": [...],
  "tool_results": [...]
}
```

### 2. Occupancy Thresholds
- Monitor context usage percentage
- At 85-90% occupancy: summarize or drop least-valuable chunks
- Apply absolute cap before hitting provider limits

### 3. Retrieval Augmented Generation (RAG)
- Offload historical context to vector stores
- Track Retrieval Recall@K metrics
- Use semantic search instead of full context inclusion

### 4. Summary Drift Monitoring
Track semantic delta between original text and its summary to ensure important information isn't lost during compaction.

## Implications for Claude Code Usage

### High Compaction Sessions
Sessions with 3+ compactions indicate:
- Complex multi-step tasks
- Large codebase navigation
- Potential context rot risk

### Optimization Opportunities
1. Break large tasks into smaller focused sessions
2. Use explicit file references instead of including full content
3. Provide concise, structured prompts
4. Place critical information at start/end of context

### Warning Signs
- Sudden increase in errors after long context
- Model "forgetting" earlier instructions
- Repetitive or circular conversations
- Inconsistent behavior on similar prompts

## Future Considerations

Context window sizes continue to grow:
- GPT-4o: 128k tokens
- Claude Sonnet 4: 200k tokens (1M beta)
- Gemini: 1M-2M tokens
- Llama 4: 10M tokens

However, larger windows don't eliminate context rot - they extend the degradation curve. Effective context engineering remains critical regardless of window size.
