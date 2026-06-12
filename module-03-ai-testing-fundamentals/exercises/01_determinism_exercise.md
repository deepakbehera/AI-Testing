# Exercise: Determinism & Variance

Estimated time: 25–35 minutes

## Goal

Make non-determinism visible and measurable in your own test environment.

## Tasks

1. **Run the probe.** Execute `python examples/determinism_probe.py`. Record the token-overlap scores printed at the end.

2. **Increase the sample size.** Open the script and change `RUNS = 5` to `RUNS = 10`. Re-run. Does the minimum score drop? Does the average shift?

3. **Lock temperature.** Set `temperature = 0.0` in the call (find it in the script). Re-run 10 times. Does variance disappear? Is the minimum score now 1.0? If not — write one sentence in your notes explaining why not.

4. **Write a variance-aware assertion.** In a new file `exercises/variance_check.py`, write a function:
   ```python
   def assert_consistent(responses: list[str], threshold: float = 0.7) -> None:
       """
       Assert that all pairs of responses share at least `threshold` token overlap.
       Raise AssertionError with a useful message if any pair falls below.
       """
       ...
   ```
   Use the token-overlap logic from the example (or your own similarity measure). Call it with the 10 responses from task 2.

5. **Reflection.** In `notes.md` (your personal notes, not the module notes), answer:
   - Which of the five unique AI testing challenges did you *feel* most during this exercise?
   - What would it take to make a test suite that catches a 10% change in model behavior reliably?

## Self-check

- [ ] `determinism_probe.py` runs without errors
- [ ] You have recorded variance scores at `RUNS=10`
- [ ] You understand why `temperature=0` doesn't guarantee identical outputs
- [ ] `assert_consistent` raises a useful error when variance is too high
- [ ] You've written at least two sentences of reflection in your notes
