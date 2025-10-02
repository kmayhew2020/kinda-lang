# Profile Update Suggestion

**Date:** 2025-10-02T02:30:00Z
**Profile:** kinda-pr-reviewer
**Category:** authentication
**Severity:** critical
**Issue/PR:** #139

## Summary
Reviewer must use dedicated reviewer token for GitHub authentication to submit formal PR approvals

## Reason
During PR #139 review, the reviewer posted comments but did not submit formal GitHub approval because they used the wrong authentication token. The reviewer needs to use the reviewer token (`~/.config/reviewer-token.txt`) in their startup sequence to ensure `gh pr review --approve` commands are properly authenticated.

Without this, PRs show reviewDecision as empty and no formal reviews are recorded, blocking the merge workflow.

## Suggested Addition
```markdown
## Authentication Token

**CRITICAL**: You MUST use your dedicated reviewer token for all GitHub operations.

In your startup sequence, before any GitHub operations:
```bash
export GITHUB_TOKEN=$(cat ~/.config/reviewer-token.txt)
gh auth status  # Verify authentication
```

This ensures that when you run `gh pr review --approve`, the approval is:
- Recorded in GitHub's review system
- Shows proper reviewer attribution
- Updates the PR's reviewDecision status
- Allows PM to merge the PR

**DO NOT** use other tokens (coder-token.txt, etc.) as this will result in comments instead of formal reviews.
```
