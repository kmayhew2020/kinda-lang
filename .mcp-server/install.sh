#!/bin/bash
# MCP Server Installation Script for Kinda-Lang

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
    echo "⚠️  Please edit .env and add your GitHub token"
    echo ""
else
    echo "✅ .env already exists"
    echo ""
fi

# Get absolute path for configuration
ABS_PATH="$SCRIPT_DIR/build/mcp-agent-server.js"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "✅ MCP Server installed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Configure GitHub Token"
echo "   Edit .env and add your GitHub token:"
echo "   $ nano $SCRIPT_DIR/.env"
echo ""
echo "   Get a token from: https://github.com/settings/tokens"
echo "   Required permissions: repo, workflow"
echo ""
echo "2. Add to Claude Code Configuration"
echo ""
echo "   Linux/macOS: ~/.config/claude/claude_desktop_config.json"
echo "   Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo ""
echo "   Add this configuration:"
echo ""
echo '   {'
echo '     "mcpServers": {'
echo '       "kinda-agent-workflow": {'
echo '         "command": "node",'
echo "         \"args\": [\"$ABS_PATH\"],"
echo '         "env": {'
echo '           "GITHUB_TOKEN": "your_github_token_here",'
echo '           "GITHUB_OWNER": "kinda-lang-dev",'
echo '           "GITHUB_REPO": "kinda-lang",'
echo "           \"WORKING_DIR\": \"$REPO_ROOT\""
echo '         }'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "3. Restart Claude Code"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation: $SCRIPT_DIR/README.md"
echo ""
