# Kinda-Lang MCP Agent Server

This is a Model Context Protocol (MCP) server that enforces the 5-agent workflow for the kinda-lang project. It provides tools for task tracking, testing automation, GitHub integration, and context preservation.

## 🚀 Quick Start

```bash
cd .mcp-server
./install.sh  # Interactive installer does everything
# Restart Claude Code when prompted
```

The installer will:
1. Install npm dependencies
2. Build TypeScript to JavaScript
3. Prompt for your GitHub token (or skip to configure manually)
4. Optionally configure Claude Code automatically
5. Show you the MCP tools that will be available

**Manual configuration:** If you skip auto-config, the installer shows you exactly what to add to your Claude Code settings.

## 📋 Available Tools

### Core Workflow Tools

#### `start_task`
Start a new agent task. **MUST be called first** before any work.

**Parameters:**
- `agent_role` (required): Your role (coder, tester, architect, verifier, main-agent)
- `task_description` (required): What you are going to do
- `github_issue_number` (optional): Related GitHub issue number

**Example:**
```typescript
start_task({
  agent_role: "coder",
  task_description: "Implement ~fuzzy_unless construct",
  github_issue_number: 142
})
```

#### `run_tests`
Run the test suite with coverage reporting.

**Parameters:**
- `test_path` (optional): Path to tests (default: "tests/")
- `coverage` (optional): Include coverage report (default: true)

**Example:**
```typescript
run_tests({
  test_path: "tests/python/",
  coverage: true
})
```

#### `run_local_ci`
Run full local CI validation before pushing.

**Returns:** Structured results from formatting, type checking, and tests.

**Example:**
```typescript
run_local_ci()
```

#### `save_context`
Save current agent context and state. **REQUIRED before completing task.**

**Parameters:**
- `summary` (required): Summary of what was done
- `files_changed` (required): Array of changed file paths
- `tests_added` (optional): Array of new test descriptions
- `issues_addressed` (optional): Array of issue numbers addressed

**Example:**
```typescript
save_context({
  summary: "Implemented ~fuzzy_unless with full test coverage",
  files_changed: ["kinda/grammar/python/constructs.py", "tests/python/test_conditionals.py"],
  tests_added: ["test_fuzzy_unless_basic", "test_fuzzy_unless_with_personality"],
  issues_addressed: [142]
})
```

#### `complete_task`
Mark task as complete. **Enforces that context was saved.**

**Parameters:**
- `success` (required): Whether task completed successfully
- `next_steps` (optional): What should happen next
- `blocked_by` (optional): What is blocking completion (if not successful)

**Example:**
```typescript
complete_task({
  success: true,
  next_steps: "Ready for testing by kinda-tester agent"
})
```

### GitHub Integration Tools

#### `github_issue`
Fetch or update GitHub issues.

**Parameters:**
- `action` (required): "get", "comment", "update", "create"
- `issue_number` (optional): Issue number (required for get/comment/update)
- `comment` (optional): Comment text (for comment action)
- `title` (optional): Issue title (for create/update)
- `body` (optional): Issue body (for create/update)
- `labels` (optional): Array of label names (for create/update)
- `state` (optional): "open" or "closed" (for update)

**Example:**
```typescript
github_issue({
  action: "comment",
  issue_number: 142,
  comment: "Implementation complete. Tests passing. Ready for review."
})
```

### Requirements Management

#### `get_requirements`
Get current project requirements and their status.

**Returns:** List of requirements with completion status.

## 🔒 Workflow Enforcement

The MCP server enforces the following policies:

### Before Task Completion
- ✅ Context must be saved via `save_context`
- ✅ Tests must be run and passing (for coder/tester roles)
- ✅ Local CI must be run (for tester role)

### Agent-Specific Policies

**Coder:**
- Must run tests before completing
- Must save context with files_changed
- Should update related GitHub issues

**Tester:**
- Must run full local CI
- Must achieve 75%+ test coverage
- Must save test results in context

**Architect:**
- Must document design decisions
- Must save architectural context
- Should link to specifications

## 🛠️ Development

### Build from Source

```bash
npm run build
```

### Run in Development Mode

```bash
npm run dev
```

### Project Structure

```
.mcp-server/
├── mcp-agent-server.ts    # Main MCP server implementation
├── package.json            # Node.js dependencies
├── tsconfig.json          # TypeScript configuration
├── .env.example           # Environment template
├── .env                   # Your config (gitignored)
└── build/                 # Compiled output (gitignored)
```

## 🔧 Troubleshooting

### "Unknown tool" Error
- Restart Claude Code after configuration changes
- Verify MCP server path is absolute, not relative
- Check that build/ directory exists and contains .js files

### GitHub API Errors
- Verify GITHUB_TOKEN has correct permissions (repo, workflow)
- Check that token is not expired
- Ensure GITHUB_OWNER and GITHUB_REPO match your fork

### "Context not saved" Error
- Call `save_context` before `complete_task`
- Ensure you're providing required parameters
- Check that .agent-system/ directory exists

### Tests Not Running
- Verify WORKING_DIR points to kinda-lang root
- Check that pytest is installed (`pip install -e .[dev]`)
- Ensure test files exist in the specified path

## 📚 Integration with 5-Agent Workflow

This MCP server integrates with the existing `.claude/` infrastructure:

- **Complements bash scripts**: Provides programmatic API for workflow steps
- **Enforces quality gates**: Prevents task completion without proper validation
- **Tracks context**: Maintains agent state across sessions
- **GitHub integration**: Automated issue updates and PR management

See `.claude/README.md` and `CLAUDE.md` for complete workflow documentation.

## 🔐 Security Notes

- ⚠️ `.env` file contains secrets and is gitignored
- ⚠️ Never commit GitHub tokens to version control
- ⚠️ Use environment variables or Claude Code MCP config for tokens
- ⚠️ Limit token permissions to minimum required (repo, workflow)

## 📄 License

This MCP server follows the same dual-license model as kinda-lang:
- Open Source (AGPL v3) for research/education
- Commercial License for production use

See `LICENSE-DUAL.md` for details.
