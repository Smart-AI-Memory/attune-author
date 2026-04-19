---
type: quickstart
feature: rag-hook
depth: quickstart
generated_at: 2026-04-19T06:43:49.111962+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Quickstart: rag hook

Check if RAG grounding is available and retrieve context for polish passes:

```python
from attune_author.rag_hook import rag_enabled, ground_polish_context

# Check if RAG is available
if rag_enabled():
    context = ground_polish_context("quickstart", "template", k=3)
    print(f"Retrieved context: {context[:100]}..." if context else "No context found")
else:
    print("RAG grounding disabled or unavailable")
```

Expected output:
```
RAG grounding disabled or unavailable
```

## Enable RAG grounding

1. **Install the RAG extra** to enable the grounding feature:
   ```bash
   pip install attune-author[rag]
   ```

2. **Verify RAG is available** by running the check again:
   ```python
   from attune_author.rag_hook import rag_enabled
   print(rag_enabled())  # Should print: True
   ```

3. **Retrieve grounding context** for a polish pass:
   ```python
   context = ground_polish_context("error-handling", "troubleshooting")
   if context:
       print("Found relevant templates to guide the polish pass")
   ```

## Disable RAG temporarily

Set the environment variable to skip RAG lookups:
```bash
export ATTUNE_AUTHOR_RAG=1
python your_script.py  # RAG will be disabled
```

**Next:** Configure your polish pipeline to use the grounding context in LLM prompts.
