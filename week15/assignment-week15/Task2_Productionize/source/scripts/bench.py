import argparse
import asyncio
import json
import statistics
import time

import httpx

QUESTIONS = [
    "My card was charged twice for the same order, I want a refund",
    "How long does standard delivery take?",
    "Can I change the delivery address after ordering?",
    "Is there a fee if I cancel my order now?",
    "Where do I download the invoice for my order?",
    "What payment methods do you accept?",
    "I want to close my account permanently",
    "How do I unsubscribe from the newsletter?",
]


async def one_shot(client: httpx.AsyncClient, url: str, question: str) -> dict:
    start = time.perf_counter()
    try:
        response = await client.post(
            f"{url}/chat", json={"message": question, "use_tools": False}, timeout=180
        )
        elapsed = (time.perf_counter() - start) * 1000
        if response.status_code != 200:
            return {"ok": False, "status": response.status_code, "ms": elapsed}
        body = response.json()
        return {
            "ok": True,
            "ms": elapsed,
            "cache": body["cache"],
            "degraded": body["degraded"],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "ms": (time.perf_counter() - start) * 1000}


async def time_to_first_token(client: httpx.AsyncClient, url: str, question: str) -> float | None:
    start = time.perf_counter()
    async with client.stream(
        "POST", f"{url}/chat/stream", json={"message": question}, timeout=180
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith('data: {"token"'):
                return (time.perf_counter() - start) * 1000
    return None


def summarise(name: str, values: list[float]) -> None:
    if not values:
        print(f"{name}: no samples")
        return
    ordered = sorted(values)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    print(
        f"{name}: n={len(values)} "
        f"p50={statistics.median(ordered):.0f}ms p95={p95:.0f}ms max={ordered[-1]:.0f}ms"
    )


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--rounds", type=int, default=2)
    args = parser.parse_args()

    limits = httpx.Limits(max_connections=args.concurrency * 2)
    async with httpx.AsyncClient(limits=limits) as client:
        ready = (await client.get(f"{args.url}/readyz", timeout=30)).json()
        print("readiness:", json.dumps(ready))

        ttft = await time_to_first_token(client, args.url, "How long does standard delivery take?")
        print(f"time to first token: {ttft:.0f}ms" if ttft else "time to first token: n/a")

        print(f"\ncold run, concurrency {args.concurrency}")
        started = time.perf_counter()
        results = []
        for _ in range(args.rounds):
            batch = await asyncio.gather(
                *(
                    one_shot(client, args.url, q)
                    for q in QUESTIONS[: args.concurrency]
                )
            )
            results.extend(batch)
        wall = time.perf_counter() - started
        ok = [r for r in results if r["ok"]]
        summarise("latency", [r["ms"] for r in ok])
        print(f"requests/second: {len(results) / wall:.2f}   failures: {len(results) - len(ok)}")

        print("\nwarm run, same questions (cache should hit)")
        started = time.perf_counter()
        warm = await asyncio.gather(
            *(one_shot(client, args.url, q) for q in QUESTIONS[: args.concurrency])
        )
        wall = time.perf_counter() - started
        hits = [r for r in warm if r.get("cache") in {"exact", "semantic"}]
        summarise("latency", [r["ms"] for r in warm if r["ok"]])
        print(f"requests/second: {len(warm) / wall:.2f}   cache hits: {len(hits)}/{len(warm)}")

        print("\nbatch endpoint")
        started = time.perf_counter()
        response = await client.post(
            f"{args.url}/chat/batch",
            json={"messages": QUESTIONS[: args.concurrency], "use_tools": False},
            timeout=300,
        )
        wall = (time.perf_counter() - started) * 1000
        print(f"{len(response.json())} answers in {wall:.0f}ms")


if __name__ == "__main__":
    asyncio.run(main())
