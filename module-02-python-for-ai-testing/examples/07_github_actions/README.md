# Day 7 — GitHub Actions setup

## Install the workflow

1. Copy [`llm-tests.yml`](llm-tests.yml) to `.github/workflows/llm-tests.yml` at the repo root:
   ```bash
   mkdir -p .github/workflows
   cp module-02-python-for-ai-testing/examples/07_github_actions/llm-tests.yml .github/workflows/
   ```
2. Add your API key(s) as repo secrets (GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**):
   - `OPENAI_API_KEY` (required if `PROVIDER=openai`)
   - `ANTHROPIC_API_KEY` (required if `PROVIDER=anthropic`)
3. Commit and push:
   ```bash
   git add .github/workflows/llm-tests.yml
   git commit -m "ci: add LLM test workflow"
   git push
   ```
4. Open the **Actions** tab — you'll see the workflow running.

## What the workflow does

| Step | Purpose |
|---|---|
| **Checkout** | Pull the repo onto the runner |
| **Set up Python 3.11** | Install a known Python version |
| **Cache pip** | Skip re-downloading deps on every run |
| **Install requirements** | `pip install -r requirements.txt` |
| **Run pytest** | Execute the Day 6 framework, produce HTML + JUnit XML |
| **Upload HTML report** | Available for download from the run page (30 days) |
| **Upload JUnit XML** | Standard format consumed by GitHub UI + many tools |
| **Publish test results** | Render a pass/fail table on the PR |

## Triggers

The workflow runs on:
- **push** to `main`
- **pull_request** targeting `main`  (this is where gating lives — make the job required in branch protection)
- **workflow_dispatch** — manual run from the Actions tab
- **schedule** — weekly, Monday 06:00 UTC (catches upstream model drift)

## Gate merges on test results

After the workflow has run once successfully:

1. Repo → **Settings** → **Branches** → **Add rule** for `main`
2. Enable **Require status checks to pass before merging**
3. Search for and require `Run pytest suite` (the job name)
4. Save

Now a PR cannot merge if the LLM tests fail.

## Cost note

Each run hits the LLM API. For a ~20-case golden suite with `gpt-4o-mini` the cost is typically under $0.05. If you're running on every push, use `PROVIDER=ollama` locally and flip to `openai` only for the scheduled nightly run (or use a cheap model like `gpt-4o-mini`).

## Common issues

| Problem | Fix |
|---|---|
| `OPENAI_API_KEY is not set` | Secret not added, or spelling mismatch |
| `working-directory` not found | Check the path; your repo layout may differ |
| Tests pass locally, fail in CI | Likely a model-version drift — pin `DEMO_MODEL` explicitly |
| Workflow takes > 5 min | Add `pytest -n auto` via `pytest-xdist` in requirements |
| HTML report missing | Report only uploads on `if: always()` — check the step did run |
