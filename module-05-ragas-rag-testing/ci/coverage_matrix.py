# coverage_matrix.py
# CI-only: prints the Module 5 capability x failure-mode coverage matrix (extending
# Module 4 Day 4's matrix with retrieval failure modes) for golden_dataset.json
# (normal + hard-negative rows together), as markdown.
# Run with: python coverage_matrix.py   (cwd = this ci/ folder)

import json
from collections import Counter

with open("golden_dataset.json", "r") as f:
    all_cases = json.load(f)

categories = sorted({c["category"] for c in all_cases})
failure_modes = sorted({c["failure_mode"] for c in all_cases})
counts = Counter((c["category"], c["failure_mode"]) for c in all_cases)

print(f"| Capability \\ Failure mode | {' | '.join(failure_modes)} |")
print(f"|{'---|' * (len(failure_modes) + 1)}")
for cat in categories:
    row = [str(counts[(cat, fm)]) for fm in failure_modes]
    print(f"| {cat} | {' | '.join(row)} |")

zero_cells = [(cat, fm) for cat in categories for fm in failure_modes if counts[(cat, fm)] == 0]
print()
print(f"Filled cells: {len(counts)} / {len(categories) * len(failure_modes)}")
if zero_cells:
    print()
    print("Untested capability x failure-mode combinations (not necessarily a problem — just visible now):")
    for cat, fm in zero_cells:
        print(f"- `{cat}` x `{fm}`")
