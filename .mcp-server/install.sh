#!/bin/bash
# MCP Server Installation Script for Kinda-Lang
# This script installs, builds, and configures the MCP server in one step

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Installing Kinda-Lang MCP Agent Server"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version too old (found v$NODE_VERSION, need v18+)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Check if build succeeded
if [ ! -f "build/mcp-agent-server.js" ]; then
    echo "❌ Build failed - build/mcp-agent-server.js not found"
    exit 1
fi

echo "✅ Build complete"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    NEED_TOKEN=true
else
    echo "✅ .env already exists"
    NEED_TOKEN=false
fi

# Check if GitHub token is configured
if ! grep -q "^GITHUB_TOKEN=" ".env" || grep -q "^GITHUB_TOKEN=ghp_your_github" ".env"; then
    NEED_TOKEN=true
fi

# Prompt for GitHub token if needed
if [ "$NEED_TOKEN" = true ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔑 GitHub Token Required"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Get a token from: https://github.com/settings/tokens"
    echo "Required scopes: repo, workflow"
    echo ""
    read -p "Enter your GitHub token (or press Enter to skip): " GITHUB_TOKEN

    if [ -n "$GITHUB_TOKEN" ]; then
        sed -i.bak "s|GITHUB_TOKEN=.*|GITHUB_TOKEN=$GITHUB_TOKEN|" .env
        rm .env.bak 2>/dev/null || true
        echo "✅ GitHub token configured"
        NEED_TOKEN=false
    else
        echo "⚠️  Skipped - you'll need to edit .env manually later"
        NEED_TOKEN=true
    fi
fi

echo ""

# Detect OS for Claude config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
fi

ABS_PATH="$SCRIPT_DIR/build/mcp-agent-server.js"

# Offer to configure Claude automatically
if [ "$NEED_TOKEN" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 Claude Code Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Configure Claude Code automatically? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Create config directory if needed
        CLAUDE_CONFIG_DIR=$(dirname "$CLAUDE_CONFIG")
        if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
            echo "📁 Creating Claude config directory..."
            mkdir -p "$CLAUDE_CONFIG_DIR"
        fi

        # Backup existing config
        if [ -f "$CLAUDE_CONFIG" ]; then
            BACKUP="$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
            echo "💾 Backing up existing config to: $(basename $BACKUP)"
            cp "$CLAUDE_CONFIG" "$BACKUP"
        fi

        # Get GitHub token from .env
        GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" .env | cut -d'=' -f2)

        # Create or update configuration using Python
        python3 - <<EOF
import json
import sys

config_file = "$CLAUDE_CONFIG"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['kinda-agent-workflow'] = {
    "command": "node",
    "args": ["$ABS_PATH"],
    "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN",
        "GITHUB_OWNER": "kinda-lang-dev",
        "GITHUB_REPO": "kinda-lang",
        "WORKING_DIR": "$REPO_ROOT"
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Claude Code configured successfully")
EOF

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ Installation Complete!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "🔄 Next Step: Restart Claude Code"
        echo ""
        echo "After restart, these MCP tools will be available:"
        echo "  - start_task"
        echo "  - run_tests"
        echo "  - run_local_ci"
        echo "  - save_context"
        echo "  - complete_task"
        echo "  - github_issue"
        echo "  - get_requirements"
        echo ""
    else
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 Manual Configuration Required"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Add to: $CLAUDE_CONFIG"
        echo ""
        cat <<CONFIG
{
  "mcpServers": {
    "kinda-agent-workflow": {
      "command": "node",
      "args": ["$ABS_PATH"],
      "env": {
        "GITHUB_TOKEN": "$(grep "^GITHUB_TOKEN=" .env | cut -d'=' -f2)",
        "GITHUB_OWNER": "kinda-lang-dev",
        "GITHUB_REPO": "kinda-lang",
        "WORKING_DIR": "$REPO_ROOT"
      }
    }
  }
}
CONFIG
        echo ""
        echo "Then restart Claude Code"
        echo ""
    fi
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Next Steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Edit .env and add your GitHub token:"
    echo "   $ nano $SCRIPT_DIR/.env"
    echo ""
    echo "2. Run this script again to configure Claude Code"
    echo "   $ ./install.sh"
    echo ""
fi

echo "📚 Documentation: $SCRIPT_DIR/README.md"
echo ""
