from typing import Optional
import json
import re


def score_json_extraction(response: str, ground_truth: dict) -> float:
    """Score JSON extraction tasks using exact match."""
    try:
        # Strip markdown code fences if model adds them
        cleaned = response.strip()
        cleaned = re.sub(r"```json|```", "", cleaned).strip()

        parsed = json.loads(cleaned)

        matches = sum(
            1 for k, v in ground_truth.items()
            if str(parsed.get(k, "")).lower().strip() == str(v).lower().strip()
        )
        return round(matches / len(ground_truth), 2)

    except (json.JSONDecodeError, AttributeError):
        return 0.0


def score_code_gen(response: str) -> float:
    """Actually run the generated code and test it."""
    try:
        # Extract code block
        code_match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
        if not code_match:
            code_match = re.search(r"```\n(.*?)```", response, re.DOTALL)
        if not code_match:
            return 0.0

        code = code_match.group(1)
        namespace = {}
        exec(code, namespace)

        fib = namespace.get("fibonacci") or namespace.get("fib")
        if not fib:
            return 0.0

        assert fib(0) == 0
        assert fib(1) == 1
        assert fib(10) == 55
        assert fib(15) == 610
        return 1.0

    except Exception:
        return 0.0


def score_task(task_type: str, response: str, ground_truth) -> Optional[float]:
    if task_type == "json_extraction" and ground_truth:
        return score_json_extraction(response, ground_truth)
    elif task_type == "code_gen":
        return score_code_gen(response)
    else:
        return None