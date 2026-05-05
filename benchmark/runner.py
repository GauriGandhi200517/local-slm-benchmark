import time
import json
import psutil
import requests
from dataclasses import dataclass
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"

@dataclass
class BenchmarkResult:
    model: str
    task_type: str
    time_to_first_token_ms: float
    total_time_ms: float
    tokens_generated: int
    tokens_per_second: float
    response: str
    quality_score: Optional[float] = None
    ram_delta_mb: float = 0.0

def run_benchmark(model: str, prompt: str, task_type: str) -> BenchmarkResult:
    ram_before = psutil.virtual_memory().used / 1024**2

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0,
            "seed": 42
        }
    }

    first_token_time = None
    full_response = ""
    token_count = 0

    start = time.perf_counter()

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if chunk.get("response"):
                    if first_token_time is None:
                        first_token_time = (time.perf_counter() - start) * 1000
                    full_response += chunk["response"]
                    token_count += 1
                if chunk.get("done"):
                    token_count = chunk.get("eval_count", token_count)
                    break

    except Exception as e:
        print(f"\n  ERROR calling Ollama: {e}")
        total_time = (time.perf_counter() - start) * 1000
        return BenchmarkResult(
            model=model,
            task_type=task_type,
            time_to_first_token_ms=0,
            total_time_ms=total_time,
            tokens_generated=0,
            tokens_per_second=0,
            response=f"ERROR: {str(e)}",
            ram_delta_mb=0,
        )

    total_time = (time.perf_counter() - start) * 1000
    ram_after = psutil.virtual_memory().used / 1024**2

    return BenchmarkResult(
        model=model,
        task_type=task_type,
        time_to_first_token_ms=first_token_time or total_time,
        total_time_ms=total_time,
        tokens_generated=token_count,
        tokens_per_second=token_count / (total_time / 1000) if total_time > 0 else 0,
        response=full_response,
        ram_delta_mb=ram_after - ram_before,
    )