# Fork Review Scripts

Scripts to simplify reviewing contributions from GitHub forks.

## Quick Start

### Review a Fork PR
```bash
./scripts/review-fork-pr.sh <username:branch>
```

**Example:**
```bash
./scripts/review-fork-pr.sh siddhantparadox:feat/instruction-proposal-tracker
```

This will:
1. Add the contributor's fork as a remote
2. Fetch their branch
3. Create a local review branch with a descriptive name
4. Check out the branch for review
5. Show helpful review commands

### Clean Up After Review
```bash
./scripts/cleanup-fork-review.sh <username:branch>
```

**Example:**
```bash
./scripts/cleanup-fork-review.sh siddhantparadox:feature/pre-optimization-summary
```

This will:
1. Switch back to main
2. Delete the local review branch
3. Remove the contributor's remote

## Scripts Overview

### `review-fork-pr.sh`
- **Purpose**: Set up a local environment to review a fork contribution
- **Usage**: `./scripts/review-fork-pr.sh <username:branch> [local_branch_name]`
- **Features**:
  - Automatically detects repository info
  - Creates descriptive local branch names
  - Handles existing remotes/branches gracefully
  - Error handling with cleanup on failure
  - Provides helpful next-step commands

### `cleanup-fork-review.sh`
- **Purpose**: Clean up after reviewing a fork contribution
- **Usage**: `./scripts/cleanup-fork-review.sh <username:branch>`
- **Features**:
  - Auto-derives the local branch name from username:branch
  - Safe cleanup that won't delete important branches
  - Shows remaining remotes and branches for verification
  - Handles cases where items are already deleted

## Typical Workflow

1. **Start Review:**
   ```bash
   ./scripts/review-fork-pr.sh siddhantparadox:feature/pre-optimization-summary
   ```

2. **Review the Changes:**
   ```bash
   git diff main --name-status          # See what files changed
   git diff main                        # See detailed changes
   git log main..HEAD --oneline         # See commit history
   python -m pytest tests/ -v          # Run tests
   ```

3. **Clean Up:**
   ```bash
   ./scripts/cleanup-fork-review.sh siddhantparadox:feature/pre-optimization-summary
   ```

## Benefits

- **Consistent Naming**: Automatically creates descriptive branch names
- **Safe Operations**: Built-in error handling and cleanup
- **Time Saving**: Reduces multiple git commands to a single script call
- **Helpful Output**: Provides next-step guidance and cleanup instructions
- **Reusable**: Works with any GitHub fork contribution

## Examples

### Reviewing a bug fix:
```bash
./scripts/review-fork-pr.sh johndoe:fix/memory-leak
# Creates: pr-review-johndoe-fix-memory-leak
```

### Reviewing a feature:
```bash
./scripts/review-fork-pr.sh alice:feature/new-optimization
# Creates: pr-review-alice-feature-new-optimization
```

### Custom local branch name:
```bash
./scripts/review-fork-pr.sh bob:hotfix/critical-issue my-custom-review-branch
# Creates: my-custom-review-branch
```
