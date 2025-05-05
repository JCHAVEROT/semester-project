import itertools
from typing import List, Dict

def compute_score(data: Dict) -> float:
    """Compute a preference score from implicit and explicit signals."""
    implicit = data["implicit_data"]
    explicit = data["explicit_data"]
    
    # Thresholds to cap the values
    MAX_TIME_ON_TASK = 10_800  # Max 3 hours
    MAX_ACTIVE_MINUTES = 600  # Max active minutes (10 hours)
    
    # Implicit features
    time_on_task = min(sum(implicit["time_on_task_per_module"].values()), MAX_TIME_ON_TASK)
    scroll_depth = implicit["scrolling_behavior"]["average_scroll_depth"]
    scroll_events = implicit["scrolling_behavior"]["scroll_events"]
    completion_rate = implicit["engagement_metrics"]["completion_rate"]
    active_minutes = min(implicit["engagement_metrics"]["active_minutes"], MAX_ACTIVE_MINUTES)
    memory_use = implicit["memory_usage_patterns"]["personal_notes_added"] + implicit["memory_usage_patterns"]["memory_recalls"]
    retries = sum(implicit.get("number_of_retries_on_quizzes", {}).values())
    response_times = sum(implicit.get("response_times", {}).values())
    pace = implicit["pace_tracking_signals"]["average_pace"]
    interactions = len(implicit["interactions_with_tutor"])

    # Explicit features
    avg_module_rating = (
        sum(explicit["ratings_on_modules"].values()) / len(explicit["ratings_on_modules"])
        if explicit["ratings_on_modules"] else 0
    )
    satisfaction = explicit["satisfaction_surveys"]["overall_satisfaction"]
    self_improvement = explicit["skill_self_assessments"]["after_training"] - explicit["skill_self_assessments"]["before_training"]
    relevance = explicit["relevance_feedback"]
    difficulty = explicit["difficulty_feedback"]
    trust = explicit["trust_feedback"]

    # Weighted formula
    score = (
        0.2 * time_on_task +
        0.1 * scroll_depth +
        0.1 * scroll_events +
        0.2 * completion_rate +
        0.1 * active_minutes +
        0.1 * memory_use +
        0.05 * interactions +
        0.05 * avg_module_rating +
        0.05 * satisfaction +
        0.05 * self_improvement +
        0.05 * (relevance + trust - difficulty) +
        0.02 * pace -
        0.02 * retries -
        0.01 * response_times
    )

    return round(score, 2)

def generate_preference_pairs(user_data: List[Dict]) -> List[Dict]:
    """Generate preference pairs (chosen, rejected) for each user."""
    pairs = []
    user_samples = {}

    # Group samples per user
    for sample in user_data:
        uid = sample["user_id"]
        score = compute_score(sample)
        sample["score"] = score
        user_samples.setdefault(uid, []).append(sample)

    # Compare pairs within the same user
    for uid, samples in user_samples.items():
        for a, b in itertools.combinations(samples, 2):
            if a["score"] == b["score"]:
                continue  # skip equal score pairs
            chosen, rejected = (a, b) if a["score"] > b["score"] else (b, a)
            pairs.append({
                "user_id": uid,
                "chosen": chosen,
                "rejected": rejected,
                "score_diff": abs(chosen["score"] - rejected["score"])
            })
    return pairs