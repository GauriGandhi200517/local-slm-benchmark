TASKS = [
    {
        "type": "json_extraction",
        "prompt": """Extract the following fields as valid JSON only: {"name": ..., "email": ..., "age": ...}

Text: 'Contact Sarah Chen at sarah@example.com, she is 34 years old.'

Reply with JSON only. No explanation.""",
        "ground_truth": {"name": "Sarah Chen", "email": "sarah@example.com", "age": "34"}
    },
    {
        "type": "summarization",
        "prompt": """Summarize this in exactly one sentence:

'Climate change is accelerating at an unprecedented rate. Global temperatures have risen by 1.1 degrees Celsius since pre-industrial times. Scientists warn that without immediate action to reduce carbon emissions, we risk crossing critical tipping points that could lead to irreversible damage to ecosystems worldwide.'""",
        "ground_truth": None
    },
    {
        "type": "code_gen",
        "prompt": """Write a Python function called fibonacci(n) that returns the nth Fibonacci number using memoization.

Reply with only the Python code block. No explanation.""",
        "ground_truth": None
    },
    {
        "type": "reasoning",
        "prompt": """Answer with Yes or No, then explain in one sentence:

If all Bloops are Razzles, and all Razzles are Lazzles, are all Bloops definitely Lazzles?""",
        "ground_truth": None
    }
]