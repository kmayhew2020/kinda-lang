#!/bin/bash
#
# MCP Server Setup Script for Claude Code CLI
#
# Usage: ./setup-cli.sh [GITHUB_TOKEN]
#
# This script:
# 1. Builds the MCP server (required on every fresh clone)
# 2. Configures Claude Code CLI to use the MCP server
# 3. Verifies the connection
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 MCP Server Setup for Claude Code CLI"
echo "========================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Install from: https://nodejs.org/"
    echo "   Required version: 18 or higher"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js version $NODE_VERSION is too old"
    echo "   Required version: 18 or higher"
    echo "   Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "   npm should come with Node.js"
    echo "   Reinstall Node.js from: https://nodejs.org/"
    exit 1
fi

echo "✅ npm $(npm --version)"

# Check Claude Code CLI
if ! command -v claude &> /dev/null; then
    echo "❌ Error: Claude Code CLI is not installed"
    echo "   Install from: https://docs.claude.com/en/docs/claude-code"
    exit 1
fi

echo "✅ Claude Code CLI installed"
echo ""

# Step 1: Build the MCP server
echo "📦 Step 1: Building MCP server..."
cd "$SCRIPT_DIR"

echo "   Installing npm dependencies..."
if ! npm install --silent; then
    echo "❌ Error: npm install failed"
    echo "   Check your internet connection and npm configuration"
    exit 1
fi

echo "   Compiling TypeScript..."
if ! npm run build --silent; then
    echo "❌ Error: TypeScript build failed"
    echo "   Check mcp-agent-server.ts for syntax errors"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/build/mcp-agent-server.js" ]; then
    echo "❌ Error: Build failed - mcp-agent-server.js not found"
    exit 1
fi

echo "✅ Build complete"
echo ""

# Step 2: Get GitHub token
GITHUB_TOKEN="${1:-}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "🔑 Step 2: GitHub Token"
    echo ""
    echo "You need a GitHub Personal Access Token with 'repo' and 'workflow' scopes."
    echo "Create one at: https://github.com/settings/tokens/new"
    echo ""
    read -p "Enter your GitHub token (or press Enter to skip): " GITHUB_TOKEN
    echo ""
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Skipping GitHub token configuration"
    echo "   You'll need to manually configure .env file later"
    GITHUB_TOKEN="your_token_here"
else
    echo "✅ GitHub token received"
fi
echo ""

# Step 3: Add to Claude Code CLI
echo "🔗 Step 3: Configuring Claude Code CLI..."
echo ""

# Check if already configured
if claude mcp list 2>/dev/null | grep -q "kinda-agent-workflow"; then
    echo "⚠️  MCP server already configured"
    read -p "Remove existing config and reconfigure? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        claude mcp remove kinda-agent-workflow 2>/dev/null || true
        echo "Removed existing configuration"
    else
        echo "Keeping existing configuration"
        echo ""
        echo "✅ Setup complete! MCP server is ready."
        echo ""
        echo "To use MCP tools:"
        echo "  1. Exit this Claude session (if in one): exit"
        echo "  2. Start fresh session: claude"
        echo "  3. MCP tools will be available automatically"
        exit 0
    fi
fi

# Add the MCP server
claude mcp add kinda-agent-workflow node "$SCRIPT_DIR/build/mcp-agent-server.js" --scope user \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -e GITHUB_OWNER=kinda-lang-dev \
  -e GITHUB_REPO=kinda-lang \
  -e WORKING_DIR="$REPO_ROOT"

echo ""
echo "✅ MCP server configured"
echo ""

# Step 4: Verify
echo "🔍 Step 4: Verifying connection..."
echo ""

if claude mcp list | grep -q "✓ Connected"; then
    echo "✅ MCP server is connected!"
else
    echo "⚠️  MCP server may not be connected. Check 'claude mcp list' output:"
    claude mcp list
fi

echo ""
echo "════════════════════════════════════════"
echo "✅ Setup complete! MCP server is ready."
echo "════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Exit this Claude session (if in one): exit"
echo "  2. Start fresh session: claude"
echo "  3. MCP tools will be available automatically"
echo ""
echo "Available MCP tools:"
echo "  • start_task - Initialize agent task tracking"
echo "  • run_tests - Automated test execution"
echo "  • run_local_ci - Full CI validation"
echo "  • save_context - Agent state preservation"
echo "  • complete_task - Task completion validation"
echo "  • get_requirements - Get incomplete requirements"
echo "  • github_issue - GitHub integration"
echo ""
echo "Verify tools loaded: Run 'claude' and check tool list"
echo ""
