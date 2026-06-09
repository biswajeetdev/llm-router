#!/usr/bin/env python3
import argparse
import json
import sys

from src.classifier import classify
from src.router import Router


def cmd_classify(args):
    prompt = args.prompt or sys.stdin.read()
    tier = classify(prompt)
    print(f"Complexity: {tier}")


def cmd_run(args):
    prompt = args.prompt or sys.stdin.read().strip()
    r = Router(provider=args.provider)
    result = r.complete(prompt, args.complexity, args.max_tokens, args.system)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["text"])
        print(
            f"\n[{result['model']} | tier={result['tier']} | "
            f"{result['input_tokens']}+{result['output_tokens']} tok | "
            f"${result['cost_usd']:.6f} | {result['latency_ms']}ms]",
            file=sys.stderr,
        )


def cmd_stats(args):
    r = Router(provider=args.provider)
    s = r.stats()
    print(f"Total calls : {s['total_calls']}")
    print(f"Total cost  : ${s['total_cost_usd']:.6f}")
    print("\nBy model:")
    for m in s["by_model"]:
        print(
            f"  {m['model']:<45} {m['calls']:>4} calls  "
            f"${m['total_cost']:.6f}  {m['avg_latency']:.0f}ms avg"
        )


def main():
    parser = argparse.ArgumentParser(description="LLM Router — auto-route prompts to the right model")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("run", help="Route a prompt and get a completion")
    p.add_argument("prompt", nargs="?", help="Prompt (reads stdin if omitted)")
    p.add_argument("--provider", default="anthropic", choices=["anthropic", "openai"])
    p.add_argument("--complexity", choices=["simple", "medium", "complex"])
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--system", default="")
    p.add_argument("--json", action="store_true", dest="json")

    p = sub.add_parser("classify", help="Classify prompt complexity without calling a model")
    p.add_argument("prompt", nargs="?")

    p = sub.add_parser("stats", help="Show usage stats from the local DB")
    p.add_argument("--provider", default="anthropic")

    args = parser.parse_args()
    dispatch = {"run": cmd_run, "classify": cmd_classify, "stats": cmd_stats}
    if args.cmd in dispatch:
        dispatch[args.cmd](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
