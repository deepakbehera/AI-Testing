# Exercise: GitHub Actions CI/CD

**Estimated time:** 40–50 minutes

---

## Part A — Deploy the Workflow (20 min)

1. Create the workflows directory in your repo root:
   ```bash
   mkdir -p .github/workflows
   ```

2. Copy the provided workflow file:
   ```bash
   cp module-02-python-for-ai-testing/examples/07_github_actions/llm-tests.yml \
      .github/workflows/llm-tests.yml
   ```

3. Add your API key as a GitHub Secret:
   - Navigate to: `repo → Settings → Secrets and variables → Actions → New repository secret`
   - Name: `OPENAI_API_KEY`
   - Value: your actual key

   If you're using Ollama only, the workflow will need adjustment — see Part B.

4. Commit and push:
   ```bash
   git add .github/workflows/llm-tests.yml
   git commit -m "ci: add LLM test workflow"
   git push
   ```

5. Go to the **Actions** tab in your GitHub repo. Confirm the workflow starts running.

6. Screenshot or note: the run URL, the run time, and the final status (green ✓ or red ✗).

---

## Part B — Customize the Workflow (15 min)

Modify `llm-tests.yml` with these improvements:

1. **Add Ollama support as a fallback** — add a step that runs Ollama if `OPENAI_API_KEY` is not set:
   ```yaml
   - name: Start Ollama (fallback)
     if: env.OPENAI_API_KEY == ''
     run: |
       curl -fsSL https://ollama.ai/install.sh | sh
       ollama serve &
       sleep 5
       ollama pull llama3.2:3b
   ```

2. **Only run on changed files** — add a `paths:` filter so the workflow only triggers when Python or test files change:
   ```yaml
   on:
     push:
       paths:
         - "module-02-python-for-ai-testing/**"
         - ".github/workflows/llm-tests.yml"
   ```

3. **Add a scheduled weekly run** — add a `schedule:` trigger to run every Monday at 6 AM UTC.

Commit and push. Confirm the workflow triggers on your push.

---

## Part C — Branch Protection (10 min)

Set up branch protection on `main`:
1. Go to `repo → Settings → Branches → Add rule`
2. Branch name pattern: `main`
3. Enable: **Require status checks to pass before merging**
4. Search for your workflow job name and add it
5. Enable: **Require branches to be up to date before merging**
6. Save

Test it:
- Create a new branch: `git checkout -b test/ci-gate`
- Intentionally break a test (change a `must_include` keyword to something wrong)
- Push and open a PR
- Confirm the PR shows a red ✗ and cannot be merged

---

## Part D — Bonus: PR Comment with Results (optional, +15 min)

Add a step that posts a test result summary as a PR comment using the GitHub CLI or `actions/github-script`:

```yaml
- name: Comment test results on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      // Read pytest output or a summary file
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '## Test Results\n✅ X passed, ❌ Y failed'
      })
```

---

## Self-Check

- [ ] Workflow appears in the Actions tab and runs green
- [ ] Artifact (HTML report) is downloadable from the run page
- [ ] `paths:` filter is in place (workflow doesn't trigger on README changes)
- [ ] Weekly schedule trigger is configured
- [ ] Branch protection blocks a PR with a failing test
- [ ] You understand what "status check" means in GitHub terms
