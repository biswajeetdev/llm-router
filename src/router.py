import os
import time
from typing import Optional

from anthropic import Anthropic
from openai import OpenAI

from .classifier import classify
from .tracker import Tracker

TIERS = {
    "anthropic": {
        "simple":  "claude-haiku-4-5-20251001",
        "medium":  "claude-sonnet-4-6",
        "complex": "claude-opus-4-8",
    },
    "openai": {
        "simple":  "gpt-4o-mini",
        "medium":  "gpt-4o",
        "complex": "o1",
    },
}

# (input $/M, output $/M)
PRICING = {
    "claude-haiku-4-5-20251001": (0.80,  4.00),
    "claude-sonnet-4-6":         (3.00,  15.00),
    "claude-opus-4-8":           (15.00, 75.00),
    "gpt-4o-mini":               (0.15,  0.60),
    "gpt-4o":                    (2.50,  10.00),
    "o1":                        (15.00, 60.00),
}


class Router:
    def __init__(self, provider: str = "anthropic", db_path: str = "usage.db"):
        self.provider = provider
        self.tracker = Tracker(db_path)

        if provider == "anthropic":
            self._client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        else:
            self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def complete(
        self,
        prompt: str,
        complexity: Optional[str] = None,
        max_tokens: int = 1024,
        system: str = "",
    ) -> dict:
        tier = complexity or classify(prompt)
        model = TIERS[self.provider][tier]

        start = time.monotonic()

        if self.provider == "anthropic":
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system
            resp = self._client.messages.create(**kwargs)
            text = resp.content[0].text
            in_tok = resp.usage.input_tokens
            out_tok = resp.usage.output_tokens
        else:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = self._client.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens
            )
            text = resp.choices[0].message.content
            in_tok = resp.usage.prompt_tokens
            out_tok = resp.usage.completion_tokens

        latency_ms = int((time.monotonic() - start) * 1000)
        cost = self._cost(model, in_tok, out_tok)

        self.tracker.record(
            model=model, tier=tier,
            input_tok=in_tok, output_tok=out_tok,
            cost_usd=cost, latency_ms=latency_ms,
        )

        return {
            "text": text,
            "model": model,
            "tier": tier,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "cost_usd": round(cost, 6),
            "latency_ms": latency_ms,
        }

    def stats(self) -> dict:
        return self.tracker.summary()

    def _cost(self, model: str, in_tok: int, out_tok: int) -> float:
        if model not in PRICING:
            return 0.0
        in_p, out_p = PRICING[model]
        return (in_tok * in_p + out_tok * out_p) / 1_000_000
