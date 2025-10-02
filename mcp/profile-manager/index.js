#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { promises as fs } from 'fs';
import path from 'path';

// MCP servers are started with the project root as CWD
// This matches how cli.cjs finds the project root dynamically
const PROJECT_ROOT = process.cwd();
const BASE_DIR = path.join(PROJECT_ROOT, '.agent-system/profile-updates');
const PROFILES_DIR = path.join(PROJECT_ROOT, '.claude/agents');

// MCP Server
const server = new Server(
  {
    name: "kinda-profile-manager",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool: List pending profile updates
async function listPendingUpdates() {
  const pendingDir = path.join(BASE_DIR, 'pending');

  try {
    const files = await fs.readdir(pendingDir);

    if (files.length === 0) {
      return { status: 'success', message: 'No pending profile updates', updates: [] };
    }

    const updates = [];

    for (const file of files) {
      const content = await fs.readFile(path.join(pendingDir, file), 'utf-8');

      const profileMatch = content.match(/\*\*Profile:\*\* (.+)/);
      const categoryMatch = content.match(/\*\*Category:\*\* (.+)/);
      const severityMatch = content.match(/\*\*Severity:\*\* (.+)/);
      const summaryMatch = content.match(/## Summary\n(.+)/);
      const issueMatch = content.match(/\*\*Issue\/PR:\*\* #(\d+)/);

      updates.push({
        file,
        profile: profileMatch ? profileMatch[1] : 'unknown',
        category: categoryMatch ? categoryMatch[1] : 'unknown',
        severity: severityMatch ? severityMatch[1] : 'unknown',
        summary: summaryMatch ? summaryMatch[1] : 'No summary',
        issue: issueMatch ? `#${issueMatch[1]}` : 'N/A'
      });
    }

    return { status: 'success', count: files.length, updates };

  } catch (error) {
    return { status: 'error', message: 'No pending updates found', updates: [] };
  }
}

// Security: Validate filename to prevent path traversal attacks
function validateFilename(filename) {
  // Remove any path separators and get basename
  const basename = path.basename(filename);

  // Only allow .md files
  if (!basename.endsWith('.md')) {
    throw new Error('Invalid file extension - only .md files allowed');
  }

  // Ensure no path traversal attempts
  if (basename !== filename || filename.includes('..') || filename.includes(path.sep)) {
    throw new Error('Invalid filename: path traversal detected');
  }

  // Additional safety: check for null bytes and special characters
  if (filename.includes('\0') || /[<>:"|?*]/.test(filename)) {
    throw new Error('Invalid filename: contains illegal characters');
  }

  return basename;
}

// Security: Sanitize reason text for safe filename usage
function sanitizeReason(reason) {
  if (!reason || typeof reason !== 'string') {
    return 'no-reason';
  }
  // Remove special characters, keep only alphanumeric, spaces, and hyphens
  return reason
    .replace(/[^a-zA-Z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 50) || 'no-reason';
}

// Tool: Get update details
async function getUpdateDetails(filename) {
  const safeFilename = validateFilename(filename);
  const pendingDir = path.join(BASE_DIR, 'pending');
  const filePath = path.join(pendingDir, safeFilename);

  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return { status: 'success', content };
  } catch (error) {
    return { status: 'error', message: `File not found: ${filename}` };
  }
}

// Tool: Approve update
async function approveUpdate(filename) {
  const safeFilename = validateFilename(filename);
  const pendingDir = path.join(BASE_DIR, 'pending');
  const approvedDir = path.join(BASE_DIR, 'approved');

  await fs.mkdir(approvedDir, { recursive: true });

  try {
    await fs.rename(
      path.join(pendingDir, safeFilename),
      path.join(approvedDir, safeFilename)
    );
    return { status: 'success', message: `Approved: ${safeFilename}` };
  } catch (error) {
    return { status: 'error', message: error.message };
  }
}

// Tool: Reject update
async function rejectUpdate(filename, reason) {
  const safeFilename = validateFilename(filename);
  const safeReason = sanitizeReason(reason);
  const pendingDir = path.join(BASE_DIR, 'pending');
  const rejectedDir = path.join(BASE_DIR, 'rejected');

  await fs.mkdir(rejectedDir, { recursive: true });

  const rejectedFile = safeFilename.replace('.md', `-rejected-${safeReason}.md`);

  try {
    await fs.rename(
      path.join(pendingDir, safeFilename),
      path.join(rejectedDir, rejectedFile)
    );
    return { status: 'success', message: `Rejected: ${safeFilename}` };
  } catch (error) {
    return { status: 'error', message: error.message };
  }
}

// Tool: Apply approved updates
async function applyApprovedUpdates() {
  const approvedDir = path.join(BASE_DIR, 'approved');
  const appliedDir = path.join(BASE_DIR, 'applied');

  await fs.mkdir(appliedDir, { recursive: true });

  try {
    const files = await fs.readdir(approvedDir);

    if (files.length === 0) {
      return { status: 'success', message: 'No approved updates to apply', applied: [] };
    }

    const applied = [];

    for (const file of files) {
      const content = await fs.readFile(path.join(approvedDir, file), 'utf-8');

      const profileMatch = content.match(/\*\*Profile:\*\* (.+)/);
      const suggestionMatch = content.match(/## Suggested Addition\n```markdown\n([\s\S]+?)\n```/);
      const dateMatch = content.match(/\*\*Date:\*\* (.+)/);
      const issueMatch = content.match(/\*\*Issue\/PR:\*\* #(\d+)/);
      const summaryMatch = content.match(/## Summary\n(.+)/);

      if (profileMatch && suggestionMatch) {
        const profileName = profileMatch[1];
        const addition = suggestionMatch[1];
        const date = dateMatch ? dateMatch[1].split('T')[0] : new Date().toISOString().split('T')[0];
        const issue = issueMatch ? `#${issueMatch[1]}` : '';
        const summary = summaryMatch ? summaryMatch[1] : 'Learning';

        const profilePath = path.join(PROFILES_DIR, `${profileName}.md`);

        try {
          await fs.access(profilePath);

          const additionText = `\n\n### ${summary} [Added ${date}${issue ? `, Issue ${issue}` : ''}]\n${addition}\n`;

          await fs.appendFile(profilePath, additionText, 'utf-8');

          await fs.rename(
            path.join(approvedDir, file),
            path.join(appliedDir, file)
          );

          applied.push({ profile: profileName, summary, file });
        } catch (error) {
          applied.push({ profile: profileName, error: error.message, file });
        }
      }
    }

    return { status: 'success', count: applied.length, applied };

  } catch (error) {
    return { status: 'error', message: error.message };
  }
}

// Tool: Get statistics
async function getStatistics() {
  const dirs = {
    pending: path.join(BASE_DIR, 'pending'),
    approved: path.join(BASE_DIR, 'approved'),
    applied: path.join(BASE_DIR, 'applied'),
    'auto-approved': path.join(BASE_DIR, 'auto-approved'),
    rejected: path.join(BASE_DIR, 'rejected'),
  };

  const stats = {
    total: 0,
    counts: {},
    byProfile: {},
    byCategory: {},
    bySeverity: {},
  };

  for (const [status, dir] of Object.entries(dirs)) {
    try {
      const files = await fs.readdir(dir);
      const count = files.length;

      stats.counts[status] = count;
      stats.total += count;

      for (const file of files) {
        const content = await fs.readFile(path.join(dir, file), 'utf-8');

        const profileMatch = content.match(/\*\*Profile:\*\* (.+)/);
        const categoryMatch = content.match(/\*\*Category:\*\* (.+)/);
        const severityMatch = content.match(/\*\*Severity:\*\* (.+)/);

        if (profileMatch) {
          const profile = profileMatch[1];
          stats.byProfile[profile] = (stats.byProfile[profile] || 0) + 1;
        }

        if (categoryMatch) {
          const category = categoryMatch[1];
          stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
        }

        if (severityMatch) {
          const severity = severityMatch[1];
          stats.bySeverity[severity] = (stats.bySeverity[severity] || 0) + 1;
        }
      }

    } catch (error) {
      stats.counts[status] = 0;
    }
  }

  return { status: 'success', stats };
}

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "list_pending_updates",
      description: "List all pending profile updates",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_update_details",
      description: "Get detailed content of a specific update",
      inputSchema: {
        type: "object",
        properties: {
          filename: {
            type: "string",
            description: "The filename of the update to view",
          },
        },
        required: ["filename"],
      },
    },
    {
      name: "approve_update",
      description: "Approve a pending profile update",
      inputSchema: {
        type: "object",
        properties: {
          filename: {
            type: "string",
            description: "The filename of the update to approve",
          },
        },
        required: ["filename"],
      },
    },
    {
      name: "reject_update",
      description: "Reject a pending profile update with a reason",
      inputSchema: {
        type: "object",
        properties: {
          filename: {
            type: "string",
            description: "The filename of the update to reject",
          },
          reason: {
            type: "string",
            description: "Reason for rejection",
          },
        },
        required: ["filename", "reason"],
      },
    },
    {
      name: "apply_approved_updates",
      description: "Apply all approved updates to agent profiles",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_statistics",
      description: "Get statistics about profile updates",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "list_pending_updates":
        return { content: [{ type: "text", text: JSON.stringify(await listPendingUpdates(), null, 2) }] };

      case "get_update_details":
        return { content: [{ type: "text", text: JSON.stringify(await getUpdateDetails(args.filename), null, 2) }] };

      case "approve_update":
        return { content: [{ type: "text", text: JSON.stringify(await approveUpdate(args.filename), null, 2) }] };

      case "reject_update":
        return { content: [{ type: "text", text: JSON.stringify(await rejectUpdate(args.filename, args.reason), null, 2) }] };

      case "apply_approved_updates":
        return { content: [{ type: "text", text: JSON.stringify(await applyApprovedUpdates(), null, 2) }] };

      case "get_statistics":
        return { content: [{ type: "text", text: JSON.stringify(await getStatistics(), null, 2) }] };

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: JSON.stringify({ status: 'error', message: error.message }, null, 2)
      }]
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Kinda Profile Manager MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
