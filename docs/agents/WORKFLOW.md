# 🤖 Kinda-Lang 5-Agent Workflow Summary

## 🎯 Agent Roles & Responsibilities

### 1. 📋 **Project Manager** (`project_manager.md`)
**Owner:** Backlog, roadmap, issue assignment, PR merging
- Receives requirements from user and breaks down into issues
- Assigns issues to Architect with clear requirements
- Merges approved PRs after Reviewer approval
- Maintains project roadmap and milestone tracking

### 2. 🏛️ **Architect** (`architect.md`) 
**Owner:** Technical design, architecture documentation, implementation specs
- Receives issue assignments from PM
- Creates high-level architecture and detailed implementation specs
- Documents interfaces, APIs, and system design
- Hands off specifications to Coder

### 3. 💻 **Coder** (`coder.md`)
**Owner:** Implementation, unit tests, implementation documentation
- Receives specifications from Architect  
- Implements features with comprehensive unit tests
- Creates implementation docs and code comments
- Hands off completed implementation to Tester

### 4. 🧪 **Tester** (`tester.md`)
**Owner:** Testing, CI, quality validation, test enhancement  
- Receives implementations from Coder
- Runs comprehensive test suites and CI validation
- Writes additional tests for coverage gaps
- Routes bugs back to Coder or design issues to Architect
- Hands off tested implementations to Reviewer

### 5. 🔍 **Reviewer** (`reviewer.md`)
**Owner:** PR review, code quality, final approval
- Receives tested implementations from Tester
- Reviews code quality, security, and requirements compliance
- Approves PRs that meet standards or requests changes from Coder
- Hands off approved PRs to PM for merging

## 🔄 Workflow Flow

```
User Requirements → PM → Architect → Coder → Tester → Reviewer → PM → Merged
                    ↑      ↑         ↑       ↑        ↑
                    │      │         │       │        └─ Change Requests
                    │      │         │       └─ Bug Reports  
                    │      │         └─ Design Issues
                    │      └─ Implementation Questions
                    └─ Status Updates & Completions
```

## 📥 Input/Output Matrix

| Agent | Receives From | Provides To | Handoff Trigger |
|-------|---------------|-------------|-----------------|
| **PM** | User, Reviewer | Architect, User | Issue assignment, PR merge |
| **Architect** | PM, Coder, Tester | Coder, PM | Complete specification |
| **Coder** | Architect, Tester, Reviewer | Tester, Architect | Implementation + tests pass |
| **Tester** | Coder | Reviewer, Coder, Architect | All tests pass + coverage |
| **Reviewer** | Tester, Coder | PM, Coder | PR approval or change requests |

## 🔧 Pseudo-Code Logic Structure

All agents follow the same pseudo-code pattern:

```
STARTUP_SEQUENCE:
  load_persistent_state()
  check_inputs_from_other_agents()
  report_current_status()

MAIN_WORKFLOW:
  while (session_active):
    if (new_work_available):
      process_new_work()
    elif (feedback_received):
      handle_feedback()
    else:
      continue_current_work()

COMPLETION_SEQUENCE:
  hand_off_deliverables()
  update_progress_tracking()
  persist_state()
```

## 🛠️ Tool Usage by Agent

| Agent | Primary Tools | Key Usage |
|-------|---------------|-----------|
| **PM** | TodoWrite, Read, Bash, Write | Backlog tracking, git merges |
| **Architect** | Read, Write, Grep, Glob | Design docs, architecture analysis |
| **Coder** | Read, Write/Edit, Bash, Grep | Implementation, testing |
| **Tester** | Bash, Write, Read, Grep | Test execution, CI validation |
| **Reviewer** | Read, Bash, Grep, Glob | Code review, quality checks |

## ✅ Quality Gates

1. **PM → Architect**: Issue has clear requirements and acceptance criteria
2. **Architect → Coder**: Complete implementation specification with interfaces
3. **Coder → Tester**: Implementation complete + unit tests pass + local CI passes  
4. **Tester → Reviewer**: All tests pass + adequate coverage + no critical issues
5. **Reviewer → PM**: PR approved + all quality criteria met + requirements satisfied

## 🔄 Feedback Loops

- **Coder ↔ Architect**: Implementation feasibility and design clarification
- **Tester → Coder**: Bug reports and implementation issues
- **Tester → Architect**: Design flaws requiring specification changes
- **Reviewer → Coder**: Code quality improvements and change requests
- **All Agents → PM**: Progress updates, blockers, and status reports

## 🎲 Kinda-Specific Considerations

All agents understand Kinda's unique requirements:
- **Fuzzy Behavior**: Statistical testing and seed-based determinism
- **Personality System**: Mood and chaos-level integration  
- **Satirical Spirit**: Maintain fun while ensuring quality
- **Controlled Chaos**: Intentional unpredictability with reliable interfaces

## 🚀 Getting Started

Each agent should be invoked with their specific role:
```bash
# Example invocations in Claude Code
"Use the kinda-lang project manager agent to plan this feature"
"Use the kinda-lang architect agent to design this system"  
"Use the kinda-lang coder agent to implement this specification"
"Use the kinda-lang tester agent to validate this implementation"
"Use the kinda-lang reviewer agent to review this PR"
```

This workflow ensures clear separation of concerns, quality gates at each step, and maintains Kinda's chaotic spirit through professional development practices.