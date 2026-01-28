# CI/CD Workflow Troubleshooting Log

## Goal
Set up per-service auto-incrementing semantic version tags (e.g., `frontend-1.0.1`, `insights_api-1.0.2`) that trigger Docker image builds and pushes to GHCR for ArgoCD deployments.

## Desired Flow
```
Push to main (changes to service X)
  ↓
CI runs tests for service X
  ↓
Create version tag (e.g., service-1.0.x)
  ↓
CD detects new tag and deploys service X
  ↓
Docker image pushed to GHCR with 3 tags:
  - service-1.0.x (semantic version)
  - <sha> (commit SHA)
  - latest
```

## What We Tried

### Attempt 1: workflow_run with path-filter
**Setup:**
- CI workflow on push to main
- Tagging workflow triggered by `workflow_run` on CI completion
- CD workflow triggered by `workflow_run` on tagging completion
- Used `dorny/paths-filter` to detect changed services

**Issue:**
When triggered via `workflow_run`, `paths-filter` couldn't detect changes properly:
```
Warning: 'before' field is missing in event payload - changes will be detected from last commit
Detected 397 changed files
```

**Result:** All services tagged on every run, causing duplicate builds and wrong version bumps.

---

### Attempt 2: Combined CI + Tagging with path-filter
**Setup:**
- Combined CI and tagging into one workflow
- Path detection runs on `push` event (has proper git context)
- CD triggered by `workflow_run`

**Issue 1: GitHub Token Permissions**
Tags created with default `GITHUB_TOKEN` didn't trigger subsequent workflows.

**Research Finding:**
- GitHub Actions intentionally prevents `GITHUB_TOKEN` from triggering workflows
- This prevents infinite workflow loops
- Source: [GitHub Discussion #25617](https://github.com/orgs/community/discussions/25617)

**Fix Attempted:** Created Personal Access Token (PAT) and used it for checkout and tagging:
```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.PAT_TOKEN }}

- uses: anothrNick/github-tag-action@v1
  env:
    GITHUB_TOKEN: ${{ secrets.PAT_TOKEN }}
    GIT_API_TAGGING: false
```

**Issue 2: Tag Detection in CD**
Even with tags being pushed, CD workflow couldn't reliably detect which services to deploy:
- Used `git tag --points-at HEAD` but context was unclear in `workflow_run`
- Tags existed but detection failed

---

### Attempt 3: Trigger CD on tag push
**Setup:**
```yaml
# cd.yaml
on:
  push:
    tags:
      - 'frontend-*'
      - 'insights_api-*'
      # etc...
```

**Issue:**
Even with PAT_TOKEN, `on.push.tags` **never triggered** when tags were created from workflows.

**Research Finding:**
- Multiple users report `on.push.tags` is unreliable when tags come from Actions
- Sources:
  - [GitHub Discussion #27194](https://github.com/orgs/community/discussions/27194)
  - [GitHub Discussion #27028](https://github.com/orgs/community/discussions/27028)
  - [GitHub Discussion #26840](https://github.com/orgs/community/discussions/26840)

**Evidence:** Tag was successfully pushed (`* [new tag] data_ingestion-1.0.2 -> data_ingestion-1.0.2`), but CD workflow showed 0 new runs.

---

### Attempt 4: Back to workflow_run with explicit tag checking
**Setup:**
```yaml
on:
  workflow_run:
    workflows:
      - CI + Tagging Workflow
    types:
      - completed

jobs:
  get-tags:
    steps:
      - run: git fetch --tags --force
      - run: git tag --points-at "${{ github.event.workflow_run.head_sha }}"
```

**Status:** Currently testing, but CD workflow still not triggering at all.

---

## Why Not Just Use Simple workflow_run + Path Detection?

### The Original Problem
We tried this first! Here's why it didn't work:

**Scenario 1: Separate Workflows (CI → Tagging → CD)**
```yaml
# tagging.yaml
on:
  workflow_run:
    workflows: [CI Workflow]
    types: [completed]
```

**Problem:** `workflow_run` events don't include the `before` field in the event payload, which `dorny/paths-filter` needs to compute the diff. Result: All files detected as changed.

**Scenario 2: Combined CI + Tagging → CD**
```yaml
# ci.yaml - runs on push (has git context) ✓
# cd.yaml - runs on workflow_run
```

**Problem:** CD workflow triggered successfully, but couldn't determine which services to deploy because:
1. Path detection in CD runs with `workflow_run` context (same issue as above)
2. Tag detection via `git tag --points-at HEAD` was unreliable in `workflow_run` context

### Alternative: Use tj-actions/changed-files
Research suggested `tj-actions/changed-files` handles `workflow_run` context better than `dorny/paths-filter`.

**Why we didn't try it yet:**
- Already spent significant time on multiple approaches
- Fundamental issue might be deeper (tag push events not triggering)

---

## Current Status

### What's Working
✓ CI runs tests on changed services
✓ Tags are created successfully with PAT_TOKEN
✓ Tags are pushed to remote repository

### What's NOT Working
✗ CD workflow doesn't trigger after tags are pushed
✗ No automatic deployments happening

### Evidence
CI output shows successful tag creation:
```
Bumping tag data_ingestion-1.0.1 - New tag data_ingestion-1.0.2
EVENT: creating local tag data_ingestion-1.0.2
EVENT: pushing tag data_ingestion-1.0.2 to origin
To https://github.com/Vchen7629/Cyphria
 * [new tag]         data_ingestion-1.0.2 -> data_ingestion-1.0.2
```

But CD shows no runs after the latest tag pushes.

---

## Recommended Next Steps

### Option 1: Combine Everything into One Workflow
Stop fighting GitHub's workflow trigger limitations. Put CI + Tagging + CD in one file:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  path-filter:
    # detects changes (works on push)

  frontend-ci:
    # runs tests

  frontend-tag:
    needs: frontend-ci
    # creates tag

  frontend-cd:
    needs: frontend-tag
    # builds and pushes docker image
```

**Pros:**
- No workflow_run context issues
- Path detection works perfectly
- Everything runs in sequence
- Simple mental model

**Cons:**
- Less separation of concerns
- One big workflow file
- Can't rerun just CD without rerunning CI

### Option 2: Use Repository Dispatch
Create tags in CI, then use repository_dispatch to trigger CD:

```yaml
# ci.yaml
- run: gh workflow run cd.yaml -f service=frontend -f tag=frontend-1.0.1

# cd.yaml
on:
  workflow_dispatch:
    inputs:
      service:
        required: true
      tag:
        required: true
```

**Pros:**
- Explicit control over what gets deployed
- Decoupled workflows
- Can manually trigger deployments

**Cons:**
- More complex
- Requires GitHub CLI in workflow
- Additional API calls

### Option 3: Use Artifacts for Communication
CI/Tagging writes JSON file with deployment info, CD reads it:

```yaml
# ci.yaml
- run: echo '{"frontend":"frontend-1.0.1"}' > deploy.json
- uses: actions/upload-artifact@v4

# cd.yaml
- uses: actions/download-artifact@v4
  # Read deploy.json to know what to deploy
```

**Cons:**
- Artifacts in workflow_run context are tricky
- More complexity

---

## Why Is This So Hard?

1. **GitHub's Security Model:** `GITHUB_TOKEN` can't trigger workflows (by design)
2. **workflow_run Limitations:** Missing git context for path detection
3. **Tag Push Events:** Unreliable when tags come from workflows, even with PAT
4. **Context Isolation:** Each workflow run has its own isolated environment

This is a well-known pain point in the GitHub Actions ecosystem, with no perfect solution.

---

## Conclusion

After multiple attempts and research, the root issue is **GitHub Actions' workflow trigger limitations**. The most reliable solution is likely to **combine CI, tagging, and CD into a single workflow** to avoid cross-workflow trigger issues entirely.

The "best practice" of separating CI and CD workflows works well for simple cases, but breaks down when you need:
- Dynamic, per-service deployments
- Auto-incrementing version tags
- Tags to trigger deployments

**Recommendation:** Simplify to a single workflow that does everything in sequence.
