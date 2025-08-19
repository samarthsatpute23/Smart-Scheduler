# scheduler.py

from datetime import datetime

def smart_schedule(tasks):
    """
    tasks: list of dicts with keys: title, duration, deadline, priority
    Returns: sorted list of tasks
    """
    def parse_deadline(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except:
            return datetime.max  # fallback if deadline missing

    # Sort by priority (high first) then by earliest deadline
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (-t['priority'], parse_deadline(t['deadline']))
    )

    return sorted_tasks
