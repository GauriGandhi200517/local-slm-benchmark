import json
import datetime
import os
from benchmark.runner import run_benchmark
from benchmark.evaluator import score_task
from benchmark.tasks import TASKS

MODELS = [
    "phi3:mini",
    "llama3.2:3b",
    "mistral:7b-instruct-q4_K_M"
]

RUNS_PER_TASK = 2  # run each task twice and average

os.makedirs("results/runs", exist_ok=True)

all_results = []

for model in MODELS:
    print(f"\n{'='*50}")
    print(f"Testing model: {model}")
    print(f"{'='*50}")

    for task in TASKS:
        run_results = []

        for run_num in range(RUNS_PER_TASK):
            print(f"  [{task['type']}] run {run_num + 1}/{RUNS_PER_TASK}...", end=" ", flush=True)

            result = run_benchmark(model, task["prompt"], task["type"])
            result.quality_score = score_task(
                task["type"], result.response, task["ground_truth"]
            )

            run_results.append(result)
            print(f"done — {result.tokens_per_second:.1f} tok/s")

        # Average across runs
        avg = {
            "model": model,
            "task": task["type"],
            "avg_ttft_ms": round(
                sum(r.time_to_first_token_ms for r in run_results) / RUNS_PER_TASK, 1
            ),
            "avg_total_ms": round(
                sum(r.total_time_ms for r in run_results) / RUNS_PER_TASK, 1
            ),
            "avg_tokens_per_sec": round(
                sum(r.tokens_per_second for r in run_results) / RUNS_PER_TASK, 1
            ),
            "avg_quality_score": (
                round(sum(r.quality_score for r in run_results
                          if r.quality_score is not None) / RUNS_PER_TASK, 2)
                if any(r.quality_score is not None for r in run_results)
                else None
            ),
            "sample_response": run_results[0].response[:300]
        }

        print(f"    TTFT: {avg['avg_ttft_ms']}ms | "
              f"Speed: {avg['avg_tokens_per_sec']} tok/s | "
              f"Quality: {avg['avg_quality_score']}")

        all_results.append(avg)

# Save results
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"results/runs/benchmark_{timestamp}.json"

with open(output_file, "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\n✅ Done! Results saved to {output_file}")