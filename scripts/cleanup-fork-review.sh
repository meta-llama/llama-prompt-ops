#!/bin/bash

# Script to cleanup fork contribution review setup
# Usage: ./scripts/cleanup-fork-review.sh <username:branch>
# Examples:
#   ./scripts/cleanup-fork-review.sh siddhantparadox:feature/pre-optimization-summary
#   ./scripts/cleanup-fork-review.sh Sangamesh26:feature/validation-min-records-dataset

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
    echo "Usage: $0 <username:branch>"
    echo ""
    echo "Examples:"
    echo "  $0 siddhantparadox:feature/pre-optimization-summary"
    echo "  $0 Sangamesh26:feature/validation-min-records-dataset"
    echo ""
    echo "Arguments:"
    echo "  username:branch       - GitHub username and branch name separated by colon"
    echo "                          (auto-derives local branch name as pr-review-<username>-<sanitized-branch>)"
    echo ""
    echo "This script will:"
    echo "  1. Switch back to main branch"
    echo "  2. Delete the specified local review branch"
    echo "  3. Remove the contributor's remote"
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

# Sanitize branch name for local branch (replace / and other special chars with -)
SANITIZED_BRANCH=$(echo "$BRANCH_NAME" | sed 's/[^a-zA-Z0-9-]/-/g')
LOCAL_BRANCH_NAME="pr-review-${GITHUB_USERNAME}-${SANITIZED_BRANCH}"

# Validate that we have both username and branch name
if [ -z "$GITHUB_USERNAME" ] || [ -z "$BRANCH_NAME" ]; then
    print_error "Both username and branch name are required"
    show_usage
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

print_status "Cleaning up fork review for:"
print_status "  Contributor: ${GITHUB_USERNAME}"
print_status "  Local branch: ${LOCAL_BRANCH_NAME}"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")

# Switch to main if we're on the review branch
if [ "$CURRENT_BRANCH" = "$LOCAL_BRANCH_NAME" ]; then
    print_status "Switching from review branch to main..."
    git checkout main
else
    print_status "Currently on branch: ${CURRENT_BRANCH}"
fi

# Delete the local review branch if it exists
if git branch | grep -q " ${LOCAL_BRANCH_NAME}$"; then
    print_status "Deleting local branch: ${LOCAL_BRANCH_NAME}"
    git branch -D "$LOCAL_BRANCH_NAME"
    print_success "Deleted local branch: ${LOCAL_BRANCH_NAME}"
else
    print_warning "Local branch '${LOCAL_BRANCH_NAME}' not found"
fi

# Remove the contributor's remote if it exists
if git remote | grep -q "^${GITHUB_USERNAME}$"; then
    print_status "Removing remote: ${GITHUB_USERNAME}"
    git remote remove "$GITHUB_USERNAME"
    print_success "Removed remote: ${GITHUB_USERNAME}"
else
    print_warning "Remote '${GITHUB_USERNAME}' not found"
fi

print_success "Cleanup completed!"
print_status "You are now on: $(git branch --show-current)"

# Show remaining remotes and branches for verification
echo ""
echo "📋 Remaining remotes:"
git remote -v | sed 's/^/  /'

echo ""
echo "📋 Local branches:"
git branch | sed 's/^/  /'
