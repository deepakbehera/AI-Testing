# Day 5 — Exercise: DeepEval in CI/CD

**Estimated time:** 40–50 minutes

---

## Part A — Deploy the Eval Workflow (15 min)

1. Copy the provided workflow:
   ```bash
   cp module-04-deepeval-llm-testing/examples/day5_ci/llm-eval.yml \
      .github/workflows/llm-eval.yml
   ```

2. Add `OPENAI_API_KEY` to GitHub Secrets:
   - `repo → Settings → Secrets and variables → Actions → New repository secret`
   - Name: `OPENAI_API_KEY`, Value: your actual key

3. Commit and push:
   ```bash
   git add .github/workflows/llm-eval.yml
   git commit -m "ci: add DeepEval eval workflow"
   git push
   ```

4. Go to the **Actions** tab. Confirm the workflow starts and shows eval results.

---

## Part B — Threshold Tuning (15 min)

Look at the eval scores from Part A. For each metric:

1. Record the actual score your model achieved (check the CI output or artifact report)
2. Decide on a production threshold: give yourself a 10% buffer below the lowest score you've seen

Example:
```
AnswerRelevancy: scores observed [0.82, 0.79, 0.88] → set threshold=0.70
Faithfulness:   scores observed [0.91, 0.89, 0.92] → set threshold=0.80
Correctness:    scores observed [0.74, 0.68, 0.77] → set threshold=0.60
```

Update your test thresholds and push. Confirm CI is still green with the new values.

---

## Part C — Break the Gate (10 min)

Intentionally make a test fail to confirm CI blocks the merge:

1. Create a new branch: `git checkout -b test/eval-gate`
2. Edit one test case's `actual_output` to a clearly wrong or off-topic answer
3. Push and open a PR
4. Confirm CI shows red ✗ and the merge button is blocked

Then fix it, push again, and confirm green ✓.

---

## Part D — Nightly Drift Detection (10 min)

Add a second job to the workflow that:
- Runs on schedule every Monday at 2 AM UTC
- Calls your LLM with the same 5 factual prompts from Day 1
- Checks each response still passes `AnswerRelevancyMetric(threshold=0.7)`
- Posts results as a GitHub Actions summary

```yaml
drift-check:
  runs-on: ubuntu-latest
  if: github.event_name == 'schedule'
  steps:
    - ... # checkout, setup, install
    - name: Run drift check
      run: pytest module-04-deepeval-llm-testing/tests/test_drift.py -v
```

---

## Self-Check

- [ ] Workflow appears in Actions tab and runs green
- [ ] HTML report is downloadable as artifact from the run page
- [ ] Intentionally broken case shows red ✗ and blocks PR merge
- [ ] Thresholds are set based on observed scores (not arbitrary)
- [ ] Nightly drift job is scheduled with correct cron syntax
- [ ] You can explain: why run evals on a schedule, not just on every push?
