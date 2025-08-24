# 🤖 Kinda-Lang Agent Development Workflow

## Overview
This document defines how the three Claude Code agents work together in our development process.

## 🔄 Development Flow

### 1. 🏗️ Project Manager/Architect Planning
```
Issue created/assigned → 
"Use the kinda-lang project manager agent to plan [feature/fix]" →
PM Agent creates TodoWrite breakdown →
Hands off to Coder Agent
```

### 2. 💻 Coder Implementation  
```
PM Agent handoff →
"Use the kinda-lang coder agent to implement these tasks" →
Coder implements on feature branch →
Updates TodoWrite progress →
Hands off to Code Reviewer Agent (BEFORE PR)
```

### 3. 🔍 Code Review (Pre-PR)
```
Coder implementation complete →
"Use the kinda-lang code reviewer agent to review this implementation" →
Reviewer Agent runs comprehensive analysis →
Either: Approves + ready for PR
Or: Creates improvement todos + back to Coder
```

### 4. 📋 PR Creation (Only After Agent Approval)
```
Code Reviewer approval received →
Create PR with agent approval pasted in template →
Human review (if architecture/security) →
Merge when all requirements met
```

## 🚨 Quality Gates

### Required for ALL PRs:
- ✅ Code Reviewer Agent approval (pasted in PR)
- ✅ All CI tests passing
- ✅ TodoWrite tasks marked complete
- ✅ No breaking changes (or documented)

### Additional Requirements by Category:

**Architecture Changes:**
- ✅ Human architect review required
- ✅ Long-term impact assessment
- ✅ Alignment with kinda philosophy

**Security Changes:**  
- ✅ Human security review required
- ✅ Security analysis documented
- ✅ No new vulnerabilities introduced

**Standard Features/Fixes:**
- ✅ Agent review sufficient
- ✅ Fast-track merge possible

## 🎯 Agent Responsibilities Summary

### Project Manager/Architect Agent:
- Strategic planning and task breakdown
- Architecture decisions and design patterns
- Quality gate definitions
- Coordinates with human for major decisions

### Coder Agent:
- Feature implementation following PM specifications
- Test creation and verification
- Code quality and standards adherence
- Progress tracking via TodoWrite

### Code Reviewer Agent:
- **BLOCKING REVIEW** - no PR without approval
- Security analysis and vulnerability checks
- Test coverage verification
- Standards compliance validation
- Integration testing

## 📊 Metrics We Track

- **Agent Review Coverage**: % of PRs with agent approval
- **Human Review Trigger Rate**: % requiring human review
- **Quality Incidents**: Issues found post-merge
- **Velocity**: Time from issue → merged PR

## 🔧 Process Improvements

This workflow will evolve based on:
- Agent effectiveness in catching issues
- Developer experience feedback  
- Quality metrics and incident analysis
- Kinda project growth and complexity

---

*"Even our development process embraces uncertainty, but with structure."* 🎲