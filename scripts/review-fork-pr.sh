#!/bin/bash

# Script to quickly add a fork contribution and checkout for review
# Usage: ./scripts/review-fork-pr.sh <username:branch> [local_branch_name]
# Examples:
#   ./scripts/review-fork-pr.sh siddhantparadox:feature/pre-optimization-summary
#   ./scripts/review-fork-pr.sh Sangamesh26:feature/validation-min-records-dataset

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 <username:branch> [local_branch_name]"
    echo ""
    echo "Examples:"
    echo "  $0 siddhantparadox:feature/pre-optimization-summary"
    echo "  $0 Sangamesh26:feature/validation-min-records-dataset"
    echo "  $0 john-doe:fix/memory-leak pr-review-memory-fix"
    echo ""
    echo "Arguments:"
    echo "  username:branch      - GitHub username and branch name separated by colon"
    echo "  local_branch_name    - Optional: Custom name for local review branch"
    echo "                         (defaults to 'pr-review-<username>-<sanitized-branch>')"
}

# Check arguments
if [ $# -lt 1 ]; then
    print_error "Insufficient arguments provided"
    show_usage
    exit 1
fi

# Parse username:branch format
if [[ "$1" != *":"* ]]; then
    print_error "Invalid format. Expected 'username:branch'"
    show_usage
    exit 1
fi

GITHUB_USERNAME=$(echo "$1" | cut -d':' -f1)
BRANCH_NAME=$(echo "$1" | cut -d':' -f2)
LOCAL_BRANCH_NAME="$2"

# Validate that we have both username and branch
if [ -z "$GITHUB_USERNAME" ] || [ -z "$BRANCH_NAME" ]; then
    print_error "Both username and branch name are required"
    show_usage
    exit 1
fi

# Sanitize branch name for local branch (replace / and other special chars with -)
SANITIZED_BRANCH=$(echo "$BRANCH_NAME" | sed 's/[^a-zA-Z0-9-]/-/g')

# Set default local branch name if not provided
if [ -z "$LOCAL_BRANCH_NAME" ]; then
    LOCAL_BRANCH_NAME="pr-review-${GITHUB_USERNAME}-${SANITIZED_BRANCH}"
fi

# Get the current repository info
REPO_INFO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
if [ -z "$REPO_INFO" ]; then
    print_error "Could not determine repository info from origin remote"
    exit 1
fi

REPO_OWNER=$(echo "$REPO_INFO" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_INFO" | cut -d'/' -f2)

print_status "Repository: ${REPO_OWNER}/${REPO_NAME}"
print_status "Contributor: ${GITHUB_USERNAME}"
print_status "Branch: ${BRANCH_NAME}"
print_status "Local branch: ${LOCAL_BRANCH_NAME}"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Save current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
print_status "Current branch: ${CURRENT_BRANCH}"

# Function to cleanup on error
cleanup_on_error() {
    print_warning "Cleaning up due to error..."

    # Remove the remote if we added it
    if git remote | grep -q "^${GITHUB_USERNAME}$"; then
        print_status "Removing remote: ${GITHUB_USERNAME}"
        git remote remove "$GITHUB_USERNAME" 2>/dev/null || true
    fi

    # Remove the local branch if we created it
    if git branch | grep -q " ${LOCAL_BRANCH_NAME}$"; then
        print_status "Removing local branch: ${LOCAL_BRANCH_NAME}"
        git checkout "$CURRENT_BRANCH" 2>/dev/null || true
        git branch -D "$LOCAL_BRANCH_NAME" 2>/dev/null || true
    fi
}

# Set trap to cleanup on error
trap cleanup_on_error ERR

# Check if remote already exists
if git remote | grep -q "^${GITHUB_USERNAME}$"; then
    print_warning "Remote '${GITHUB_USERNAME}' already exists, updating..."
    git remote set-url "$GITHUB_USERNAME" "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    print_status "Adding remote for ${GITHUB_USERNAME}..."
    git remote add "$GITHUB_USERNAME" "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

# Fetch the specific branch
print_status "Fetching branch '${BRANCH_NAME}' from ${GITHUB_USERNAME}/${REPO_NAME}..."
git fetch "$GITHUB_USERNAME" "$BRANCH_NAME"

# Check if local branch already exists
if git branch | grep -q " ${LOCAL_BRANCH_NAME}$"; then
    print_warning "Local branch '${LOCAL_BRANCH_NAME}' already exists"
    read -p "Do you want to delete it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Switch to a different branch first if we're on the target branch
        if [ "$(git branch --show-current)" = "$LOCAL_BRANCH_NAME" ]; then
            git checkout "$CURRENT_BRANCH"
        fi
        git branch -D "$LOCAL_BRANCH_NAME"
    else
        print_status "Switching to existing branch..."
        git checkout "$LOCAL_BRANCH_NAME"
        print_success "Switched to existing branch: ${LOCAL_BRANCH_NAME}"
        exit 0
    fi
fi

# Create and checkout the new branch
print_status "Creating and checking out branch: ${LOCAL_BRANCH_NAME}"
git checkout -b "$LOCAL_BRANCH_NAME" "${GITHUB_USERNAME}/${BRANCH_NAME}"

print_success "Successfully set up fork contribution for review!"
print_status "You are now on branch: ${LOCAL_BRANCH_NAME}"

# Show some useful information
echo ""
echo "📋 Quick Review Commands:"
echo "  git diff main --name-status                    # See changed files"
echo "  git diff main                                  # See all changes"
echo "  git log main..HEAD --oneline                   # See commits"
echo "  python -m pytest tests/ -v                    # Run tests"
echo ""
echo "🧹 Cleanup Commands (when done reviewing):"
echo "  git checkout main                              # Switch back to main"
echo "  git branch -D ${LOCAL_BRANCH_NAME}             # Delete review branch"
echo "  git remote remove ${GITHUB_USERNAME}          # Remove contributor's remote"
echo ""
echo "🔄 Or use the cleanup script:"
echo "  ./scripts/cleanup-fork-review.sh ${GITHUB_USERNAME}:${BRANCH_NAME}"
