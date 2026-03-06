---
name: ai-service-integration
description: Integrate external AI APIs (OpenAI, vision models, local ML) into FastAPI backend safely and cleanly.
keywords: openai, ai api, vision model, retry logic, error handling
---

# AI Service Integration

## Rules

- Always isolate AI calls
- Add timeout
- Add retry logic
- Log responses
- Handle rate limits

---

# Example Pattern

```python
import httpx

class AIService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60)

    async def analyze(self, images):
        response = await self.client.post(
            "https://api.example.com/analyze",
            json={"images": images}
        )
        response.raise_for_status()
        return response.json()
```
