# MCP Server Setup Guide

This guide explains how to set up the Kinda-Lang MCP (Model Context Protocol) server from scratch. Everything needed is in this repository.

## Prerequisites

- **Node.js 18+** - Install from https://nodejs.org/
- **Claude Code** - AI-powered development environment
- **GitHub Personal Access Token** - Create at https://github.com/settings/tokens

## Quick Setup (Automated)

```bash
# From the kinda-lang repository root
cd .mcp-server
./install.sh  # Interactive - does everything in one step
# Restart Claude Code when prompted
```

The installer will guide you through:
- Installing dependencies and building
- Configuring your GitHub token
- Setting up Claude Code (automatic or manual)

That's it! The MCP server will be available as `kinda-agent-workflow`.

## Manual Setup (Step by Step)

### Step 1: Install Node.js Dependencies

```bash
cd /workspace/kinda-lang/.mcp-server
npm install
```

### Step 2: Build the TypeScript Server

```bash
npm run build
```

This creates `build/mcp-agent-server.js` from the TypeScript source.

### Step 3: Configure Environment

Create `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your GitHub token:

```bash
# Get a token from: https://github.com/settings/tokens
# Required scopes: repo, workflow

GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_OWNER=kinda-lang-dev
GITHUB_REPO=kinda-lang
WORKING_DIR=/workspace/kinda-lang
```

### Step 4: Add to Claude Code Configuration

**Linux/macOS:**
```bash
nano ~/.config/claude/claude_desktop_config.json
```

**Windows:**
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (replace paths with your absolute paths):

```json
{
  "mcpServers": {
    "kinda-agent-workflow": {
      "command": "node",
      "args": ["/absolute/path/to/kinda-lang/.mcp-server/build/mcp-agent-server.js"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_OWNER": "kinda-lang-dev",
        "GITHUB_REPO": "kinda-lang",
        "WORKING_DIR": "/absolute/path/to/kinda-lang"
      }
    }
  }
}
```

### Step 5: Restart Claude Code

The MCP server will automatically connect on startup.

## Verification

After setup, verify the MCP server is working:

1. Open Claude Code
2. The MCP tools should be available in the agent interface
3. Try the `get_requirements` tool to test connectivity

## Available Tools

Once configured, agents have access to these tools:

| Tool | Purpose |
|------|---------|
| `start_task` | Initialize a new agent task with tracking |
| `run_tests` | Execute test suite with coverage reporting |
| `run_local_ci` | Run complete local CI validation |
| `save_context` | Save agent state and progress |
| `complete_task` | Mark task complete with validation |
| `github_issue` | Fetch/update GitHub issues |
| `get_requirements` | Load project requirements |

See `README.md` for detailed tool documentation.

## Troubleshooting

### Build Fails

**Error:** `Cannot find module '../lib/tsc.js'`

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### MCP Server Not Connecting

**Check:**
1. Build succeeded: `ls -la build/mcp-agent-server.js`
2. Paths are absolute (not relative) in config
3. GITHUB_TOKEN is valid and not expired
4. Claude Code was restarted after configuration

### GitHub API Errors

**Error:** `Bad credentials` or `401 Unauthorized`

**Solution:**
- Verify GITHUB_TOKEN in `.env` matches the one in Claude config
- Check token hasn't expired at https://github.com/settings/tokens
- Ensure token has `repo` and `workflow` scopes

### Wrong Repository

**Error:** Accessing wrong fork or upstream

**Solution:**
Update `.env` and Claude config:
```bash
GITHUB_OWNER=kinda-lang-dev  # Your fork
GITHUB_REPO=kinda-lang
```

## Security Notes

⚠️ **Never commit secrets:**
- `.env` file is gitignored
- Don't commit GitHub tokens to version control
- Use environment variables for sensitive data

⚠️ **Token permissions:**
- Minimum required: `repo`, `workflow`
- Don't use tokens with more permissions than needed
- Rotate tokens regularly

## Development

### Rebuild After Changes

```bash
npm run rebuild  # Clean + build
```

### Run in Development Mode

```bash
npm run dev  # Uses tsx for hot reload
```

### Project Structure

```
.mcp-server/
├── mcp-agent-server.ts    # Main TypeScript implementation
├── package.json            # npm configuration with scripts
├── tsconfig.json          # TypeScript compiler settings
├── README.md              # Tool documentation
├── SETUP.md               # This file
├── install.sh             # Automated installation script
├── setup-claude-config.sh # Automated Claude configuration
├── .env.example           # Environment template
├── .env                   # Your configuration (gitignored)
├── build/                 # Compiled JS output (gitignored)
└── node_modules/          # Dependencies (gitignored)
```

## Integration with 5-Agent Workflow

The MCP server enhances the existing `.claude/` bash script infrastructure:

- **Bash scripts** - Manual workflow execution (always available)
- **MCP server** - Automated workflow enforcement (requires setup)

Both systems work together:
- Bash scripts for quick manual tasks
- MCP server for enforced quality gates
- Agents can use either or both

See `.claude/README.md` for bash script documentation.

## Next Steps

After setup:

1. Read `README.md` for tool usage examples
2. Review `.claude/agents/` for agent-specific workflows
3. See `CLAUDE.md` for repository setup and fork workflow
4. Check `ROADMAP.md` for current project status

## Support

- **Issues:** https://github.com/kinda-lang-dev/kinda-lang/issues
- **Workflow Questions:** Review `.claude/agents/` agent profiles
- **MCP Server Help:** See `README.md` in this directory
