# llm-router

Auto-routes prompts to the right LLM tier based on complexity. Saves cost without sacrificing quality.

## How it works

1. **Classify** — heuristic analyzes prompt length + keywords → `simple | medium | complex`
2. **Route** — maps tier to the right model (Haiku/Sonnet/Opus or GPT-4o-mini/4o/o1)
3. **Track** — logs tokens, cost, latency to local SQLite DB

```
simple  → claude-haiku / gpt-4o-mini    (~10x cheaper)
medium  → claude-sonnet / gpt-4o        (balanced)
complex → claude-opus / o1              (full power)
```

## Install

```bash
pip install -r requirements.txt
cp .env.example .env  # add your API keys
```

## CLI

```bash
# auto-route a prompt
python cli.py run "What is the capital of France?"

# force a tier
python cli.py run "Explain transformer attention" --complexity complex

# see what tier a prompt gets without calling an API
python cli.py classify "Summarize this text in one sentence"

# show cost + latency stats
python cli.py stats
```

## REST API

```bash
uvicorn api:app --reload
```

```bash
# auto-routed completion
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List the top 3 sorting algorithms"}'

# usage stats
curl http://localhost:8000/stats
```

## Python API

```python
from src.router import Router

r = Router(provider="anthropic")
result = r.complete("Summarize this meeting transcript: ...")
print(result["text"])
print(f"Used {result['model']} ({result['tier']}) — ${result['cost_usd']:.6f}")
```

## Supported Models

| Provider  | simple                    | medium          | complex        |
|-----------|---------------------------|-----------------|----------------|
| anthropic | claude-haiku-4-5-20251001 | claude-sonnet-4-6 | claude-opus-4-8 |
| openai    | gpt-4o-mini               | gpt-4o          | o1             |
