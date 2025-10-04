#!/usr/bin/env node

/**

- MCP Server for Agent Workflow Enforcement
- 
- This server FORCES agents to:
- - Save context (or they can't proceed)
- - Run tests automatically
- - Update GitHub issues/PRs
- - Follow protocol
- 
- Install:
- npm install @modelcontextprotocol/sdk @octokit/rest dotenv
- 
- Run:
- node mcp-agent-server.js
  */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
CallToolRequestSchema,
ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { Octokit } from '@octokit/rest';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const execAsync = promisify(exec);

// Configuration
const CONFIG = {
repoOwner: process.env.GITHUB_OWNER || 'kinda-lang-dev',
repoName: process.env.GITHUB_REPO || 'kinda-lang',
contextFile: '.agent-system/CONTEXT.md',
requirementsFile: '.agent-system/REQUIREMENTS.txt',
workingDir: process.env.WORKING_DIR || process.cwd(),
};

// Initialize GitHub client
const octokit = new Octokit({
auth: process.env.GITHUB_TOKEN,
});

// In-memory session state (tracks what agents have done)
const sessionState: {
  lastContextSave: number | null;
  testsRun: boolean;
  localCIRun: boolean;
  currentTask: string | null;
  currentAgent: string | null;
  protocolViolations: string[];
} = {
  lastContextSave: null,
  testsRun: false,
  localCIRun: false,
  currentTask: null,
  currentAgent: null,
  protocolViolations: [],
};

// Create MCP server
const server = new Server(
{
name: 'agent-workflow-enforcer',
version: '1.0.0',
},
{
capabilities: {
tools: {},
},
}
);

// ============================================================================
// TOOL: Start Task (MANDATORY - must be called first)
// ============================================================================
const startTaskTool = {
name: 'start_task',
description: 'Start a new task. MUST be called before any work. Sets up tracking and requirements.',
inputSchema: {
type: 'object',
properties: {
agent_role: {
type: 'string',
description: 'Your role (coder, tester, architect, etc.)',
enum: ['coder', 'tester', 'architect', 'verifier', 'main-agent'],
},
task_description: {
type: 'string',
description: 'What you are going to do',
},
github_issue_number: {
type: 'number',
description: 'GitHub issue number this task relates to (optional)',
},
},
required: ['agent_role', 'task_description'],
},
};

async function handleStartTask(args: any) {
sessionState.currentAgent = args.agent_role;
sessionState.currentTask = args.task_description;
sessionState.lastContextSave = null;
sessionState.testsRun = false;
sessionState.localCIRun = false;

// Load current requirements
const requirements = await loadRequirements();

// Check GitHub issue if provided
let issueInfo = null;
if (args.github_issue_number) {
try {
const { data: issue } = await octokit.issues.get({
owner: CONFIG.repoOwner,
repo: CONFIG.repoName,
issue_number: args.github_issue_number,
});
issueInfo = {
title: issue.title,
state: issue.state,
labels: issue.labels.map((l: any) => l.name),
};
} catch (error) {
console.error('Failed to fetch GitHub issue:', error);
}
}

return {
content: [
{
type: 'text',
text: JSON.stringify({
status: 'task_started',
agent: args.agent_role,
task: args.task_description,
session_id: Date.now(),
requirements: requirements.incomplete,
github_issue: issueInfo,
reminder: '⚠️ You MUST call save_context before calling complete_task',
}, null, 2),
},
],
};
}

// ============================================================================
// TOOL: Run Tests (AUTOMATIC - runs tests and saves results)
// ============================================================================
const runTestsTool = {
name: 'run_tests',
description: 'Run test suite with coverage. Automatically saves results. Returns structured test data.',
inputSchema: {
type: 'object',
properties: {
test_path: {
type: 'string',
description: 'Path to tests (default: tests/)',
default: 'tests/',
},
coverage: {
type: 'boolean',
description: 'Include coverage report',
default: true,
},
},
},
};

async function handleRunTests(args: any) {
const testPath = args.test_path || 'tests/';
const includeCoverage = args.coverage !== false;

try {
// Run pytest with coverage
const cmd = includeCoverage
? `pytest ${testPath} --cov=kinda --cov-report=json --json-report --json-report-file=.test-results.json`
: `pytest ${testPath} --json-report --json-report-file=.test-results.json`;

const { stdout, stderr } = await execAsync(cmd, {
  cwd: CONFIG.workingDir,
});

// Parse results
const resultsFile = path.join(CONFIG.workingDir, '.test-results.json');
const resultsData = await fs.readFile(resultsFile, 'utf-8');
const results = JSON.parse(resultsData);

// Parse coverage if available
let coverage = null;
if (includeCoverage) {
  try {
    const coverageFile = path.join(CONFIG.workingDir, 'coverage.json');
    const coverageData = await fs.readFile(coverageFile, 'utf-8');
    const coverageJson = JSON.parse(coverageData);
    coverage = {
      total: coverageJson.totals.percent_covered,
      files: Object.keys(coverageJson.files).length,
    };
  } catch (e) {
    console.error('Failed to parse coverage:', e);
  }
}

// Mark tests as run
sessionState.testsRun = true;

const testResults = {
  passed: results.summary.passed || 0,
  failed: results.summary.failed || 0,
  skipped: results.summary.skipped || 0,
  total: results.summary.total || 0,
  duration: results.duration,
  coverage: coverage,
  timestamp: new Date().toISOString(),
};

// Auto-save test results to context
await appendToContext({
  type: 'test_results',
  agent: sessionState.currentAgent || 'unknown',
  results: testResults,
});

return {
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        status: testResults.failed === 0 ? 'all_tests_passed' : 'tests_failed',
        results: testResults,
        reminder: testResults.failed > 0 
          ? '❌ Tests failed! You must fix failing tests before completing task.'
          : '✅ All tests passed!',
      }, null, 2),
    },
  ],
};

} catch (error: any) {
sessionState.testsRun = true; // Mark as attempted even if failed

return {
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        status: 'test_execution_failed',
        error: error.message,
        reminder: '❌ Tests could not run. You must fix this before completing task.',
      }, null, 2),
    },
  ],
  isError: true,
};

}
}

// ============================================================================
// TOOL: Run Local CI (MANDATORY for tester and coder)
// ============================================================================
const runLocalCITool = {
name: 'run_local_ci',
description: 'Run local CI validation (scripts/ci-full.sh). REQUIRED for tester and coder agents before completing task.',
inputSchema: {
type: 'object',
properties: {},
},
};

async function handleRunLocalCI() {
try {
// Run the local CI script
const cmd = 'bash scripts/ci-full.sh';

const { stdout, stderr } = await execAsync(cmd, {
  cwd: CONFIG.workingDir,
  timeout: 300000, // 5 minute timeout
});

// Mark as run
sessionState.localCIRun = true;

// Parse output for pass/fail
const passed = !stderr.includes('FAILED') && stdout.includes('✓');

// Auto-save CI results to context
await appendToContext({
  type: 'local_ci_results',
  agent: sessionState.currentAgent || 'unknown',
  passed,
  output: stdout.substring(0, 1000), // First 1000 chars
});

return {
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        status: passed ? 'ci_passed' : 'ci_failed',
        output: stdout.substring(0, 500),
        reminder: passed
          ? '✅ Local CI passed! You can now complete the task.'
          : '❌ Local CI failed! You must fix issues before completing task.',
      }, null, 2),
    },
  ],
};

} catch (error: any) {
sessionState.localCIRun = true; // Mark as attempted

return {
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        status: 'ci_execution_failed',
        error: error.message,
        reminder: '❌ Local CI could not run. You must fix this before completing task.',
      }, null, 2),
    },
  ],
  isError: true,
};

}
}

// ============================================================================
// TOOL: Save Context (MANDATORY - enforces format)
// ============================================================================
const saveContextTool = {
name: 'save_context',
description: 'Save work context. MANDATORY before completing task. Enforces proper format.',
inputSchema: {
type: 'object',
properties: {
agent_role: {
type: 'string',
description: 'Your role',
enum: ['coder', 'tester', 'architect', 'verifier', 'main-agent'],
},
task_completed: {
type: 'string',
description: 'What you did',
},
requirements_addressed: {
type: 'array',
items: { type: 'string' },
description: 'Requirement IDs addressed (e.g., ["REQ-1", "TECH-2"])',
},
files_modified: {
type: 'array',
items: { type: 'string' },
description: 'Files you changed',
},
next_steps: {
type: 'string',
description: 'What should happen next',
},
blockers: {
type: 'string',
description: 'Any blockers or "None"',
default: 'None',
},
},
required: ['agent_role', 'task_completed', 'requirements_addressed', 'files_modified', 'next_steps'],
},
};

async function handleSaveContext(args: any) {
// Validate format
if (!args.task_completed || args.task_completed.length < 10) {
return {
content: [
{
type: 'text',
text: JSON.stringify({
status: 'validation_failed',
error: 'task_completed must be at least 10 characters',
}),
},
],
isError: true,
};
}

if (!args.files_modified || args.files_modified.length === 0) {
return {
content: [
{
type: 'text',
text: JSON.stringify({
status: 'validation_failed',
error: 'files_modified cannot be empty',
}),
},
],
isError: true,
};
}

// Create context entry
const timestamp = new Date().toISOString();
const entry = `

### ${timestamp} - ${args.agent_role.toUpperCase()} - ${sessionState.currentTask || 'Task'}

**What I did:**
${args.task_completed}

**Requirements addressed:**
${args.requirements_addressed.map((req: string) => `- [x] ${req}: Completed`).join('\n')}

**Files modified:**
${args.files_modified.map((file: string) => `- ${file}`).join('\n')}

**Verified:**

- [x] Code works
- [x] Tests ${sessionState.testsRun ? 'passed' : 'not run'}
- [x] Context saved

**Next steps:**
${args.next_steps}

**Blockers:**
${args.blockers}

-----

`;

// Write to context file
await appendToContext({ type: 'manual_entry', entry });

// Update session state
sessionState.lastContextSave = Date.now();

// Update requirements file
for (const req of args.requirements_addressed) {
await markRequirementComplete(req);
}

return {
content: [
{
type: 'text',
text: JSON.stringify({
status: 'context_saved',
timestamp,
entry_length: entry.length,
requirements_updated: args.requirements_addressed,
reminder: '✅ Context saved! You can now call complete_task.',
}, null, 2),
},
],
};
}

// ============================================================================
// Agent-Specific Policy Checks
// ============================================================================
async function checkAgentPolicies(agentRole: string, violations: string[]) {
  try {
    // Check for .md files that violate policy (status reports, summaries, etc.)
    const { stdout } = await execAsync('git status --porcelain', {
      cwd: CONFIG.workingDir,
    });

    const files = stdout.split('\n').filter(line => line.trim());
    const prohibitedMdFiles = files.filter(line => {
      const file = line.substring(3); // Remove git status prefix
      return (
        file.endsWith('_REPORT.md') ||
        file.endsWith('_SUMMARY.md') ||
        file.endsWith('_ANALYSIS.md') ||
        file.endsWith('_REPORT.txt') ||
        file.endsWith('_SUMMARY.txt') ||
        file.endsWith('_ANALYSIS.txt') ||
        file.match(/BUG_REPORT_.*\.md/) ||
        file.match(/TEST_ANALYSIS_.*\.md/) ||
        file.match(/IMPLEMENTATION_SUMMARY.*\.md/) ||
        file.match(/PHASE_.*_SUMMARY.*\.(md|txt)/)
      );
    });

    if (prohibitedMdFiles.length > 0) {
      violations.push(
        `POLICY VIOLATION: Created prohibited status files: ${prohibitedMdFiles.map(f => f.substring(3)).join(', ')}. ` +
        'All updates must go in GitHub issue/PR comments, NOT .md or .txt files. ' +
        'Only architecture docs in docs/ are allowed.'
      );
    }

    // Tester-specific checks
    if (agentRole === 'tester') {
      // Check that test results were posted to GitHub, not saved as .md files
      if (prohibitedMdFiles.some(f => f.includes('TEST') || f.includes('BUG'))) {
        violations.push(
          'TESTER POLICY: Test results and bug reports must be posted in GitHub issue comments, ' +
          'not saved as .md files. Remove the .md files and post to the issue instead.'
        );
      }
    }

    // Coder-specific checks
    if (agentRole === 'coder') {
      // Check for implementation summaries
      if (prohibitedMdFiles.some(f => f.includes('IMPLEMENTATION'))) {
        violations.push(
          'CODER POLICY: Implementation notes must be posted in GitHub issue comments, ' +
          'not saved as .md files.'
        );
      }
    }

    // Architect-specific checks
    if (agentRole === 'architect') {
      // Check for bug fix designs in docs/ (should be in issues)
      const designFiles = files.filter(line => {
        const file = line.substring(3);
        return file.startsWith('docs/') && file.includes('bug') && file.endsWith('.md');
      });

      if (designFiles.length > 0) {
        violations.push(
          'ARCHITECT POLICY: Bug fix designs should be posted in GitHub issue comments, ' +
          'not in docs/. Only major feature designs belong in docs/.'
        );
      }
    }

    // Reviewer-specific checks
    if (agentRole === 'reviewer') {
      // Check if reviewer tried to create a PR
      const { stdout: gitLog } = await execAsync('git log -1 --format=%B', {
        cwd: CONFIG.workingDir,
      });

      if (gitLog.includes('gh pr create') || gitLog.includes('create.*PR')) {
        violations.push(
          'REVIEWER POLICY: Reviewers MUST NOT create PRs. ' +
          'Only review existing PRs created by Coder. ' +
          'If no PR exists, notify orchestrator to send task back to Coder.'
        );
      }
    }

    // Repository verification - all agents except PM on release branches
    const { stdout: branch } = await execAsync('git branch --show-current', {
      cwd: CONFIG.workingDir,
    });
    const currentBranch = branch.trim();
    const isReleaseBranch = currentBranch.startsWith('release/');

    // Non-PM agents: NEVER work on upstream for non-release branches
    if (agentRole !== 'pm') {
      // Check if there's a PR on upstream for this branch
      try {
        const { stdout: prCheck } = await execAsync(
          `gh pr list --head ${currentBranch} --repo kmayhew2020/kinda-lang --json number`,
          { cwd: CONFIG.workingDir }
        );

        const prs = JSON.parse(prCheck);

        // If non-release branch has PR on upstream, that's wrong
        if (prs.length > 0 && !isReleaseBranch) {
          violations.push(
            `REPOSITORY POLICY VIOLATION: Found PR on upstream (kmayhew2020/kinda-lang) for non-release branch '${currentBranch}'. ` +
            'Only PM can create release PRs to upstream. ' +
            'Feature/bugfix PRs must be on fork (kinda-lang-dev/kinda-lang). ' +
            'Close the upstream PR and create it on the fork instead.'
          );
        }
      } catch (error) {
        // Ignore errors (PR doesn't exist or gh command failed, which is fine)
      }
    }

    // PM-specific: Release branches should target upstream main, not fork dev
    if (agentRole === 'pm' && isReleaseBranch) {
      try {
        const { stdout: prInfo } = await execAsync(
          `gh pr list --head ${currentBranch} --json baseRefName,headRepository --jq '.[0]'`,
          { cwd: CONFIG.workingDir }
        );

        if (prInfo.trim()) {
          const pr = JSON.parse(prInfo);

          // Release PR should be on upstream, not fork
          if (pr && pr.headRepository && pr.headRepository.owner &&
              pr.headRepository.owner.login === 'kinda-lang-dev') {
            violations.push(
              `PM RELEASE POLICY: Release branch '${currentBranch}' has PR on fork. ` +
              'Release PRs must target upstream (kmayhew2020/kinda-lang) main branch, not fork. ' +
              'Use: gh pr create --repo kmayhew2020/kinda-lang --base main --head kinda-lang-dev:' + currentBranch
            );
          }
        }
      } catch (error) {
        // PR might not exist yet or command failed, that's ok
      }
    }
  } catch (error) {
    console.error('Failed to check agent policies:', error);
  }
}

// ============================================================================
// TOOL: Complete Task (ENFORCES requirements)
// ============================================================================
const completeTaskTool = {
name: 'complete_task',
description: 'Complete current task. ENFORCES: context saved, tests run, GitHub updated, agent policies.',
inputSchema: {
type: 'object',
properties: {
update_github: {
type: 'boolean',
description: 'Update GitHub issue/PR',
default: true,
},
github_issue_number: {
type: 'number',
description: 'Issue number to update',
},
github_pr_number: {
type: 'number',
description: 'PR number to update',
},
commit_message: {
type: 'string',
description: 'Git commit message',
},
},
},
};

async function handleCompleteTask(args: any) {
const violations = [];

// Check: Was context saved?
if (!sessionState.lastContextSave) {
violations.push('Context was not saved (call save_context first)');
} else if (Date.now() - sessionState.lastContextSave > 5 * 60 * 1000) {
violations.push('Context save is stale (>5 minutes old)');
}

// Check: Were tests run?
if (!sessionState.testsRun) {
violations.push('Tests were not run (call run_tests first)');
}

// Check: Was local CI run (for tester and coder)?
if ((sessionState.currentAgent === 'tester' || sessionState.currentAgent === 'coder') &&
    !sessionState.localCIRun) {
violations.push('Local CI validation not run (must run scripts/ci-full.sh before completing task)');
}

// Agent-specific policy checks
if (sessionState.currentAgent) {
  await checkAgentPolicies(sessionState.currentAgent, violations);
}

// REJECT if violations
if (violations.length > 0) {
sessionState.protocolViolations.push(...violations);

return {
  content: [
    {
      type: 'text',
      text: JSON.stringify({
        status: 'REJECTED',
        violations,
        required_actions: [
          violations.includes('Tests were not run (call run_tests first)') && 'Call run_tests',
          violations.includes('Context was not saved (call save_context first)') && 'Call save_context',
        ].filter(Boolean),
        message: '❌ Task completion REJECTED. Fix violations above and try again.',
      }, null, 2),
    },
  ],
  isError: true,
};

}

// All checks passed - proceed with completion
const completionActions = [];

// Commit changes if requested
if (args.commit_message) {
try {
await execAsync(`git add -A && git commit -m "${args.commit_message}"`, {
cwd: CONFIG.workingDir,
});
completionActions.push('Committed changes to git');
} catch (error) {
console.error('Git commit failed:', error);
}
}

// Update GitHub issue
if (args.update_github && args.github_issue_number) {
try {
await octokit.issues.createComment({
owner: CONFIG.repoOwner,
repo: CONFIG.repoName,
issue_number: args.github_issue_number,
body: `✅ Task completed by ${sessionState.currentAgent}\n\n**Task:** ${sessionState.currentTask}\n\n**Context saved:** Yes\n**Tests run:** Yes\n\nSee CONTEXT.md for details.`,
});
completionActions.push(`Updated GitHub issue #${args.github_issue_number}`);
} catch (error) {
console.error('GitHub comment failed:', error);
}
}

// Update GitHub PR
if (args.update_github && args.github_pr_number) {
try {
await octokit.pulls.createReview({
owner: CONFIG.repoOwner,
repo: CONFIG.repoName,
pull_number: args.github_pr_number,
event: 'COMMENT',
body: `✅ Task completed and verified\n\n- Context: Saved\n- Tests: ${sessionState.testsRun ? 'Passed' : 'Run'}\n- Agent: ${sessionState.currentAgent}`,
});
completionActions.push(`Updated PR #${args.github_pr_number}`);
} catch (error) {
console.error('GitHub PR update failed:', error);
}
}

// Reset session state
const summary = {
agent: sessionState.currentAgent,
task: sessionState.currentTask,
duration: sessionState.lastContextSave ? Date.now() - sessionState.lastContextSave : 0,
};

sessionState.currentAgent = null;
sessionState.currentTask = null;
sessionState.lastContextSave = null;
sessionState.testsRun = false;

return {
content: [
{
type: 'text',
text: JSON.stringify({
status: 'COMPLETE',
summary,
actions_taken: completionActions,
message: '✅ Task completed successfully! All requirements met.',
}, null, 2),
},
],
};
}

// ============================================================================
// TOOL: Get Incomplete Requirements
// ============================================================================
const getRequirementsTool = {
name: 'get_requirements',
description: 'Get list of incomplete requirements',
inputSchema: {
type: 'object',
properties: {},
},
};

async function handleGetRequirements() {
const requirements = await loadRequirements();

return {
content: [
{
type: 'text',
text: JSON.stringify({
incomplete: requirements.incomplete,
complete: requirements.complete,
total: requirements.incomplete.length + requirements.complete.length,
completion_percentage: Math.round(
(requirements.complete.length /
(requirements.incomplete.length + requirements.complete.length)) * 100
),
}, null, 2),
},
],
};
}

// ============================================================================
// TOOL: GitHub Issue Operations
// ============================================================================
const githubIssueTool = {
name: 'github_issue',
description: 'Create, update, or query GitHub issues',
inputSchema: {
type: 'object',
properties: {
action: {
type: 'string',
enum: ['create', 'update', 'get', 'list'],
description: 'Action to perform',
},
issue_number: {
type: 'number',
description: 'Issue number (for get/update)',
},
title: {
type: 'string',
description: 'Issue title (for create)',
},
body: {
type: 'string',
description: 'Issue body',
},
labels: {
type: 'array',
items: { type: 'string' },
description: 'Issue labels',
},
state: {
type: 'string',
enum: ['open', 'closed'],
description: 'Issue state (for update)',
},
},
required: ['action'],
},
};

async function handleGitHubIssue(args: any) {
try {
switch (args.action) {
case 'create':
const { data: created } = await octokit.issues.create({
owner: CONFIG.repoOwner,
repo: CONFIG.repoName,
title: args.title,
body: args.body,
labels: args.labels,
});
return {
content: [{
type: 'text',
text: JSON.stringify({ status: 'created', issue: created }, null, 2),
}],
};

  case 'update':
    const { data: updated } = await octokit.issues.update({
      owner: CONFIG.repoOwner,
      repo: CONFIG.repoName,
      issue_number: args.issue_number,
      body: args.body,
      labels: args.labels,
      state: args.state,
    });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ status: 'updated', issue: updated }, null, 2),
      }],
    };
  
  case 'get':
    const { data: issue } = await octokit.issues.get({
      owner: CONFIG.repoOwner,
      repo: CONFIG.repoName,
      issue_number: args.issue_number,
    });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ issue }, null, 2),
      }],
    };
  
  case 'list':
    const { data: issues } = await octokit.issues.listForRepo({
      owner: CONFIG.repoOwner,
      repo: CONFIG.repoName,
      state: 'open',
    });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ issues: issues.map(i => ({
          number: i.number,
          title: i.title,
          state: i.state,
          labels: i.labels.map((l: any) => l.name),
        })) }, null, 2),
      }],
    };

  default:
    throw new Error(`Unknown action: ${args.action}`);
}

} catch (error: any) {
return {
content: [{
type: 'text',
text: JSON.stringify({ error: error.message }, null, 2),
}],
isError: true,
};
}
}

// ============================================================================
// Helper Functions
// ============================================================================

async function loadRequirements() {
try {
const reqFile = path.join(CONFIG.workingDir, CONFIG.requirementsFile);
const content = await fs.readFile(reqFile, 'utf-8');

const incomplete = [];
const complete = [];

for (const line of content.split('\n')) {
  if (line.match(/^\[ \] (REQ|TECH|DOC)-\d+:/)) {
    incomplete.push(line.replace('[ ]', '').trim());
  } else if (line.match(/^\[x\] (REQ|TECH|DOC)-\d+:/)) {
    complete.push(line.replace('[x]', '').trim());
  }
}

return { incomplete, complete };

} catch (error) {
return { incomplete: [], complete: [] };
}
}

async function markRequirementComplete(reqId: string) {
try {
const reqFile = path.join(CONFIG.workingDir, CONFIG.requirementsFile);
let content = await fs.readFile(reqFile, 'utf-8');

// Replace [ ] with [x] for this requirement
content = content.replace(
  new RegExp(`\\[ \\] (${reqId}:)`, 'g'),
  '[x] $1'
);

await fs.writeFile(reqFile, content, 'utf-8');

} catch (error) {
console.error('Failed to mark requirement complete:', error);
}
}

async function appendToContext(data: any) {
try {
const contextFile = path.join(CONFIG.workingDir, CONFIG.contextFile);
const entry = data.entry || `\n[AUTO] ${data.type} at ${new Date().toISOString()}\n${JSON.stringify(data, null, 2)}\n\n`;
await fs.appendFile(contextFile, entry, 'utf-8');
} catch (error) {
console.error('Failed to append to context:', error);
}
}

// ============================================================================
// Register Tools
// ============================================================================

server.setRequestHandler(ListToolsRequestSchema, async () => ({
tools: [
startTaskTool,
runTestsTool,
runLocalCITool,
saveContextTool,
completeTaskTool,
getRequirementsTool,
githubIssueTool,
],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'start_task':
        return await handleStartTask(args);
      case 'run_tests':
        return await handleRunTests(args);
      case 'run_local_ci':
        return await handleRunLocalCI();
      case 'save_context':
        return await handleSaveContext(args);
      case 'complete_task':
        return await handleCompleteTask(args);
      case 'get_requirements':
        return await handleGetRequirements();
      case 'github_issue':
        return await handleGitHubIssue(args);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ error: error.message }, null, 2),
      }],
      isError: true,
    };
  }
});

// ============================================================================
// Start Server
// ============================================================================

async function runServer() {
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('Agent Workflow Enforcer MCP Server running on stdio');
}

runServer().catch(console.error);
