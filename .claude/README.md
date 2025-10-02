# Claude Code Infrastructure for Kinda-Lang

This directory contains portable workflow infrastructure for Claude Code development sessions. All scripts and documentation here sync across sessions via version control, ensuring consistent development practices.

## 🚀 Quick Start

**At the start of ANY new session, run:**

```bash
bash .claude/workflows/sync-session.sh
```

This ensures you have the latest workflow infrastructure and validates your environment.

## 📁 Directory Structure

```
.claude/
├── README.md                    # This file
├── preflight/                   # Pre-work validation
│   └── validate.sh             # Validates repo, remotes, CI script
├── status/                      # Visual workflow tracking
│   ├── update-status.sh        # Update current workflow status
│   └── show-workflow.sh        # Show 5-agent pipeline position
├── ci/                          # Smart CI execution
│   └── smart-ci.sh             # Only run CI when needed
├── sessions/                    # Agent session persistence
│   └── session-manager.sh      # Save/restore agent context
├── workflows/                   # Portable sync process
│   └── sync-session.sh         # Sync infrastructure across sessions
└── agents/                      # Agent profiles
    ├── kinda-pm.md             # Project Manager
    ├── kinda-architect.md      # System Architect
    ├── kinda-coder.md          # Implementation Specialist
    ├── kinda-tester.md         # Quality Assurance Tester
    └── kinda-pr-reviewer.md    # Code Reviewer
```

## 🔧 Core Tools

### Pre-Flight Validation

**Run BEFORE any work:**
```bash
bash .claude/preflight/validate.sh
```

Validates:
- ✅ Correct repository (fork vs upstream)
- ✅ Remotes configured properly
- ✅ No prohibited .md status files
- ✅ Local CI script exists
- ✅ Not accidentally on release branch

### Visual Status Tracking

**Update workflow status:**
```bash
bash .claude/status/update-status.sh <agent> <issue#> <status>
```

Example:
```bash
bash .claude/status/update-status.sh coder 106 "implementing fix"
```

**Show pipeline position:**
```bash
bash .claude/status/show-workflow.sh <agent>
```

Example:
```bash
bash .claude/status/show-workflow.sh tester
```

### Smart CI Execution

**Run CI only when needed:**
```bash
bash .claude/ci/smart-ci.sh
```

Benefits:
- Skips redundant CI runs on unchanged commits
- Analyzes file changes to determine scope
- Tracks CI state across sessions
- Saves time on documentation-only changes

**Force full CI:**
```bash
bash scripts/ci-full.sh
```

### Session Management

**Save agent state:**
```bash
bash .claude/sessions/session-manager.sh save <agent> <issue#> <pr#> <status> [notes]
```

**Load agent state:**
```bash
bash .claude/sessions/session-manager.sh load <agent>
```

**List all sessions:**
```bash
bash .claude/sessions/session-manager.sh list
```

**Clear agent state:**
```bash
bash .claude/sessions/session-manager.sh clear <agent>
```

## 🔄 Fork/Release Workflow

### Daily Development (All Agents)

✅ Work on fork: `kinda-lang-dev/kinda-lang`
✅ All PRs target fork's `dev` branch
✅ Iterate on `dev` until milestone complete

### Release Process (PM ONLY)

✅ Create `release/vX.Y.Z` branch on fork
✅ PR from fork's release branch → upstream's `main`
✅ Upstream PRs ONLY for version releases

See `CLAUDE.md` for detailed workflow documentation.

## 📋 5-Agent Workflow

```
PM → Architect → Coder → Tester → Reviewer → PM (merge)
```

Each agent has a profile in `.claude/agents/` with:
- Role and responsibilities
- Mandatory pre-flight validation
- Startup sequence
- Quality standards
- Handoff criteria

## 🛠️ Infrastructure Updates

When workflow improvements are made:

1. **On the branch with updates:**
   - Changes committed to `.claude/` directory
   - PR merged to `dev` branch
   - Infrastructure syncs via version control

2. **On other sessions:**
   - Run `bash .claude/workflows/sync-session.sh`
   - Pulls latest `.claude/` from `dev`
   - All sessions instantly updated

## 🔒 Security & Privacy

### Version Controlled (Portable)
- All scripts and agent profiles
- Workflow documentation
- Infrastructure code

### NOT Version Controlled (Session-Specific)
- `.claude/status/` - Current workflow state
- `.claude/sessions/` - Agent session data
- `.claude/ci/last-ci-state.txt` - CI state
- `.claude/ci/ci-history.log` - CI history

See `.gitignore` for complete exclusion list.

## 📚 Documentation

- **CLAUDE.md** - Main guidance, fork/release workflow, project overview
- **Agent Profiles** - Individual agent instructions in `.claude/agents/`
- **ROADMAP.md** - Project status, epic tracking, development timeline
- **This README** - Infrastructure usage and reference

## 🚦 Workflow Gates

### Before Starting Work
1. ✅ Run sync-session.sh
2. ✅ Run preflight validation
3. ✅ Check agent profile
4. ✅ Update workflow status

### Before Committing
1. ✅ Run black formatting
2. ✅ Run mypy type checking
3. ✅ Run tests locally
4. ✅ Run smart CI

### Before Creating PR
1. ✅ All tests passing
2. ✅ CI validation complete
3. ✅ Documentation updated
4. ✅ No runtime files in commit

### Before Merging (PM Only)
1. ✅ Reviewer approval
2. ✅ CI passed on fork
3. ✅ Requirements fulfilled
4. ✅ Targeting correct branch (dev for features, main for releases)

## 💡 Best Practices

1. **Start Every Session:** Run `sync-session.sh` to get latest infrastructure
2. **Pre-Flight Always:** Validate environment before work
3. **Track Status:** Update status for visibility across agents
4. **Smart CI:** Use smart-ci.sh to avoid redundant validation
5. **Save Sessions:** Use session manager for context preservation
6. **Read Your Profile:** Each agent has specific responsibilities
7. **Follow Fork Workflow:** Dev on fork, releases on upstream

## 🐛 Troubleshooting

**"Wrong repo" error:**
```bash
git remote set-url origin https://github.com/kinda-lang-dev/kinda-lang.git
git remote add upstream https://github.com/kmayhew2020/kinda-lang.git
```

**Missing infrastructure:**
```bash
git checkout origin/dev -- .claude/
```

**CI state corruption:**
```bash
rm .claude/ci/last-ci-state.txt
bash scripts/ci-full.sh
```

**Session conflicts:**
```bash
bash .claude/sessions/session-manager.sh clear <agent>
```

## 📞 Support

- **Issues:** File on GitHub at kinda-lang-dev/kinda-lang
- **Workflow Questions:** Review agent profiles in `.claude/agents/`
- **Infrastructure Updates:** PR to fork's `dev` branch

---

**Remember:** This infrastructure is portable and version-controlled. Improvements made by any agent in any session benefit all future sessions.
