# Kinda Agent Validation & Profile Manager

A comprehensive system to ensure agents complete all required tasks and learn from their work.

## Core Features

### 1. Agent Task Validation
- **Enforce completion checklists**: Prevents agents from finishing without completing required steps
- **Role-specific validation**: Different requirements for PM/Architect/Coder/Tester/Reviewer
- **Interactive checklists**: CLI tool guides agents through required tasks
- **Automated verification**: Validates completion before handoff

### 2. Profile Learning System
- **List pending updates**: View all profile update suggestions awaiting review
- **Review updates**: Get detailed content of specific updates
- **Approve/Reject**: Manage update approval workflow
- **Apply updates**: Automatically apply approved updates to agent profiles
- **Statistics**: Track profile learning metrics

## Installation

```bash
cd mcp/profile-manager
npm install
```

## Usage

### As MCP Server

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "kinda-profile-manager": {
      "command": "node",
      "args": ["/path/to/kinda-lang/mcp/profile-manager/index.js"]
    }
  }
}
```

### Agent Validation CLI

**AGENTS: Use this tool to verify you've completed all required tasks before finishing!**

```bash
# List all agents and their validation categories
npm run validate:list

# Show checklist for your agent (replace with your role)
npm run validate:coder        # For Coder agent
npm run validate:tester       # For Tester agent
npm run validate:reviewer     # For Reviewer agent
npm run validate:pm           # For PM agent
npm run validate:architect    # For Architect agent

# Show specific category checklist
node validate-agent.cjs checklist kinda-coder task_complete
node validate-agent.cjs checklist kinda-tester before_handoff
node validate-agent.cjs checklist kinda-pr-reviewer before_approval

# Get agent summary (all requirements)
node validate-agent.cjs summary kinda-coder
```

### Profile Management CLI

```bash
# List pending updates
npm run profile:list

# Interactive review
npm run profile:review

# Apply approved updates
npm run profile:apply

# View statistics
npm run profile:stats
```

## MCP Tools Available

1. **list_pending_updates** - List all pending profile updates
2. **get_update_details** - Get detailed content of a specific update
3. **approve_update** - Approve a pending update
4. **reject_update** - Reject an update with reason
5. **apply_approved_updates** - Apply all approved updates to profiles
6. **get_statistics** - Get statistics about profile updates

## Directory Structure

```
.agent-system/profile-updates/
├── pending/          # New suggestions awaiting review
├── approved/         # Reviewed and approved for application
├── applied/          # Successfully applied to profiles
├── auto-approved/    # Automatically approved updates
└── rejected/         # Rejected updates with reasons
```

## Agent Workflow

### Before Finishing ANY Task

**CRITICAL**: Agents MUST validate completion before marking work as done!

1. **Run validation for your role**:
   ```bash
   cd ~/kinda-lang/mcp/profile-manager
   npm run validate:coder  # or your agent role
   ```

2. **Review the checklist** - Ensure ALL items are completed

3. **For specific phases** (e.g., before commit, before PR):
   ```bash
   node validate-agent.cjs checklist kinda-coder before_commit
   node validate-agent.cjs checklist kinda-tester before_handoff
   ```

4. **Only proceed when ALL checks pass** - No exceptions!

### Profile Learning Workflow

1. Agents detect gaps/improvements during work
2. Suggestions saved to `.agent-system/profile-updates/pending/`
3. Review via MCP tools or CLI (`npm run profile:review`)
4. Approve/reject updates
5. Apply approved updates (`npm run profile:apply`)
6. Commit updated profiles to git

## Example

```javascript
// MCP tool call
{
  "name": "list_pending_updates",
  "arguments": {}
}

// Response
{
  "status": "success",
  "count": 3,
  "updates": [
    {
      "file": "2025-10-02-reviewer-token-auth.md",
      "profile": "kinda-pr-reviewer",
      "category": "authentication",
      "severity": "critical",
      "summary": "Add reviewer token authentication",
      "issue": "#139"
    }
  ]
}
```
