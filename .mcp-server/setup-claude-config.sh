#!/bin/bash
# Setup Claude Code MCP Configuration for Kinda-Lang

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_SERVER_JS="$SCRIPT_DIR/build/mcp-agent-server.js"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
fi

echo "🔧 Kinda-Lang MCP Server Configuration Setup"
echo ""

# Check if MCP server is built
if [ ! -f "$MCP_SERVER_JS" ]; then
    echo "❌ MCP server not built yet!"
    echo "Run: cd .mcp-server && ./install.sh"
    exit 1
fi

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ .env file not found!"
    echo "Run: cd .mcp-server && cp .env.example .env"
    echo "Then edit .env with your GitHub token"
    exit 1
fi

# Load GitHub token from .env
if ! grep -q "^GITHUB_TOKEN=" "$SCRIPT_DIR/.env" || grep -q "^GITHUB_TOKEN=ghp_your_github" "$SCRIPT_DIR/.env"; then
    echo "❌ GITHUB_TOKEN not configured in .env"
    echo "Edit $SCRIPT_DIR/.env and add your GitHub token"
    echo "Get a token from: https://github.com/settings/tokens"
    exit 1
fi

GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$SCRIPT_DIR/.env" | cut -d'=' -f2)

echo "✅ MCP server built: $MCP_SERVER_JS"
echo "✅ GitHub token configured"
echo ""

# Create config directory if needed
CLAUDE_CONFIG_DIR=$(dirname "$CLAUDE_CONFIG")
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "📁 Creating Claude config directory: $CLAUDE_CONFIG_DIR"
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Backup existing config
if [ -f "$CLAUDE_CONFIG" ]; then
    BACKUP="$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing config to: $BACKUP"
    cp "$CLAUDE_CONFIG" "$BACKUP"
fi

# Create or update configuration
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "📝 Updating existing Claude config..."

    # Use Python to merge JSON (more reliable than jq for complex merging)
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
    "args": ["$MCP_SERVER_JS"],
    "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN",
        "GITHUB_OWNER": "kinda-lang-dev",
        "GITHUB_REPO": "kinda-lang",
        "WORKING_DIR": "$REPO_ROOT"
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration updated successfully")
EOF

else
    echo "📝 Creating new Claude config..."
    cat > "$CLAUDE_CONFIG" <<EOF
{
  "mcpServers": {
    "kinda-agent-workflow": {
      "command": "node",
      "args": ["$MCP_SERVER_JS"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN",
        "GITHUB_OWNER": "kinda-lang-dev",
        "GITHUB_REPO": "kinda-lang",
        "WORKING_DIR": "$REPO_ROOT"
      }
    }
  }
}
EOF
    echo "✅ Configuration created successfully"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ MCP Server Configured Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration file: $CLAUDE_CONFIG"
echo "MCP Server: kinda-agent-workflow"
echo ""
echo "🔄 Next Step: Restart Claude Code"
echo ""
echo "After restart, the following MCP tools will be available:"
echo "  - start_task"
echo "  - run_tests"
echo "  - run_local_ci"
echo "  - save_context"
echo "  - complete_task"
echo "  - github_issue"
echo "  - get_requirements"
echo ""
echo "See .mcp-server/README.md for tool documentation"
echo ""
