#!/bin/bash
set -e

# demo_e2e.sh - End-to-End Demo/Test for Supervisor-Contributor Loop
# ===================================================================
# This script simulates a full cycle:
# 1. Setup a dummy repo
# 2. Configure 'Supervisor' role -> Mock fetch issue -> Generate Task
# 3. Configure 'Contributor' role -> Pick up Task -> Execute Work -> Commit
# 4. Verify results

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="${PROJECT_ROOT}/test_env_$(date +%s)"
WORK_DIR="${TEST_DIR}/workspace"

echo "🧪 Starting E2E Demo in: ${TEST_DIR}"
mkdir -p "${WORK_DIR}"

# --- Setup Dummy Repo ---
cd "${WORK_DIR}"
git init
git config user.email "bot@example.com"
git config user.name "Test Bot"
touch README.md
git add README.md
git commit -m "Initial commit"

# Copy scripts to workspace (simulating the agent operating in the repo)
# In a real scenario, the agent has the scripts in its toolbelt, or cloned.
# For this demo, we assume the scripts are available to the agent.
mkdir -p scripts
cp "${PROJECT_ROOT}/scripts/"*.py scripts/

# Create work directories
mkdir -p work/requests work/results

# --- Phase 1: Supervisor ---
echo "---------------------------------------------------"
echo "👮 Phase 1: Supervisor (Mock Mode)"
echo "---------------------------------------------------"

# Mock config for Supervisor
cat > .agent_role.json <<EOF
{
  "role": "supervisor",
  "repo_url": "https://github.com/dummy/repo",
  "token_env_var": "GITHUB_TOKEN",
  "workspace_root": "."
}
EOF

# Run Supervisor Loop for a few seconds to generate the task
# We use 'timeout' to run it briefly.
export MOCK_MODE=1
export GITHUB_TOKEN="mock_token"

echo "   Running supervisor_loop.py (timeout 5s)..."
timeout 5s python3 scripts/supervisor_loop.py > supervisor.log 2>&1 || true
cat supervisor.log

if [ -f "work/requests/issue-101.json" ]; then
    echo "   ✅ Task generated: work/requests/issue-101.json"
else
    echo "   ❌ Failed to generate task"
    exit 1
fi

# --- Phase 2: Contributor ---
echo "---------------------------------------------------"
echo "👷 Phase 2: Contributor"
echo "---------------------------------------------------"

# Mock config for Contributor
cat > .agent_role.json <<EOF
{
  "role": "contributor",
  "repo_url": "https://github.com/dummy/repo",
  "token_env_var": "GITHUB_TOKEN",
  "workspace_root": "."
}
EOF

# Define an execution hook (simple echo and file creation)
# This overrides the default 'touch'
export AGENT_EXEC_CMD="bash -c 'echo \"Doing work for {task_id}\" && touch implemented_{task_id}.txt'"

echo "   Running contributor_loop.py (timeout 5s)..."
timeout 5s python3 scripts/contributor_loop.py || true

# --- Verification ---
echo "---------------------------------------------------"
echo "🔍 Verification"
echo "---------------------------------------------------"

# 1. Check if branch was created
if git show-ref --verify --quiet refs/heads/worker/issue-101; then
    echo "   ✅ Branch 'worker/issue-101' exists"
else
    echo "   ❌ Branch 'worker/issue-101' missing"
    exit 1
fi

# 2. Check if file exists and was committed
git checkout worker/issue-101 > /dev/null 2>&1
if [ -f "implemented_issue-101.txt" ]; then
    echo "   ✅ Work artifact 'implemented_issue-101.txt' found"
else
    echo "   ❌ Work artifact missing"
    exit 1
fi

# 3. Check report
if [ -f "work/results/issue-101/report.md" ]; then
    echo "   ✅ Report generated"
else
    echo "   ❌ Report missing"
    exit 1
fi

echo "---------------------------------------------------"
echo "🎉 E2E Demo Passed!"
echo "---------------------------------------------------"
