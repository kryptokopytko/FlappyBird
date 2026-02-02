import json
import math

def compute_stats(data):
    novelty_scores = []
    qualities = []

    for ind in data.get("individuals", []):
        novelty = ind.get("novelty_score")
        quality = ind.get("quality")

        if isinstance(novelty, (int, float)) and math.isfinite(novelty):
            novelty_scores.append(novelty)

        if isinstance(quality, (int, float)) and math.isfinite(quality):
            qualities.append(quality)

    stats = {}

    if novelty_scores:
        stats["novelty_avg"] = sum(novelty_scores) / len(novelty_scores)
        stats["novelty_max"] = max(novelty_scores)
    else:
        stats["novelty_avg"] = None
        stats["novelty_max"] = None

    if qualities:
        stats["quality_avg"] = sum(qualities) / len(qualities)
        stats["quality_max"] = max(qualities)
    else:
        stats["quality_avg"] = None
        stats["quality_max"] = None

    return stats



with open("data/novelty_archive.json", "r") as f:
    data = json.load(f)

stats = compute_stats(data)

print("Novelty score:")
print("  avg:", stats["novelty_avg"])
print("  max:", stats["novelty_max"])

print("Quality:")
print("  avg:", stats["quality_avg"])
print("  max:", stats["quality_max"])
