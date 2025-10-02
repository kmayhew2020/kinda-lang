#!/usr/bin/env node

/**
 * Profile Update Management Scripts
 *
 * Install: npm install chalk commander
 *
 * Commands:
 * - npm run profile:list      - List pending profile updates
 * - npm run profile:review    - Interactive review of pending updates
 * - npm run profile:apply     - Apply all approved updates
 * - npm run profile:stats     - Show learning statistics
 */

const fs = require('fs').promises;
const path = require('path');
const { Command } = require('commander');
const chalk = require('chalk');

// Find project root (where .agent-system exists)
function findProjectRoot() {
  let current = process.cwd();
  while (current !== '/') {
    const agentDir = path.join(current, '.agent-system');
    try {
      require('fs').accessSync(agentDir);
      return current;
    } catch {
      current = path.dirname(current);
    }
  }
  // Fallback to 2 levels up from this script
  return path.resolve(__dirname, '../..');
}

const PROJECT_ROOT = findProjectRoot();
const BASE_DIR = path.join(PROJECT_ROOT, '.agent-system/profile-updates');
const PROFILES_DIR = path.join(PROJECT_ROOT, '.claude/agents');

// ============================================================================
// SECURITY FUNCTIONS
// ============================================================================

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

// ============================================================================
// List Pending Updates
// ============================================================================
async function listPendingUpdates() {
  const pendingDir = path.join(BASE_DIR, 'pending');

  try {
    const files = await fs.readdir(pendingDir);

    if (files.length === 0) {
      console.log(chalk.green('✓ No pending profile updates'));
      return;
    }

    console.log(chalk.bold(`\n📋 ${files.length} Pending Profile Update(s):\n`));

    for (const file of files) {
      const content = await fs.readFile(path.join(pendingDir, file), 'utf-8');

      const profileMatch = content.match(/\*\*Profile:\*\* (.+)/);
      const categoryMatch = content.match(/\*\*Category:\*\* (.+)/);
      const severityMatch = content.match(/\*\*Severity:\*\* (.+)/);
      const summaryMatch = content.match(/## Summary\n(.+)/);
      const issueMatch = content.match(/\*\*Issue\/PR:\*\* #(\d+)/);

      const profile = profileMatch ? profileMatch[1] : 'unknown';
      const category = categoryMatch ? categoryMatch[1] : 'unknown';
      const severity = severityMatch ? severityMatch[1] : 'unknown';
      const summary = summaryMatch ? summaryMatch[1] : 'No summary';
      const issue = issueMatch ? `#${issueMatch[1]}` : 'N/A';

      const severityColor =
        severity === 'critical' ? chalk.red :
        severity === 'important' ? chalk.yellow :
        chalk.blue;

      console.log(`${chalk.cyan(file)}`);
      console.log(`  Profile:  ${chalk.bold(profile)}`);
      console.log(`  Category: ${category}`);
      console.log(`  Severity: ${severityColor(severity)}`);
      console.log(`  Issue:    ${issue}`);
      console.log(`  Summary:  ${summary}`);
      console.log('');
    }

    console.log(chalk.dim(`Review: npm run profile:review`));
    console.log(chalk.dim(`Apply:  npm run profile:apply\n`));

  } catch (error) {
    console.log(chalk.yellow('No pending updates found'));
  }
}

// ============================================================================
// Interactive Review
// ============================================================================
async function interactiveReview() {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const question = (query) => new Promise((resolve) => rl.question(query, resolve));

  const pendingDir = path.join(BASE_DIR, 'pending');
  const approvedDir = path.join(BASE_DIR, 'approved');
  const rejectedDir = path.join(BASE_DIR, 'rejected');

  // Ensure directories exist
  await fs.mkdir(approvedDir, { recursive: true });
  await fs.mkdir(rejectedDir, { recursive: true });

  try {
    const files = await fs.readdir(pendingDir);

    if (files.length === 0) {
      console.log(chalk.green('✓ No pending updates to review'));
      rl.close();
      return;
    }

    console.log(chalk.bold(`\n📋 Reviewing ${files.length} pending update(s)\n`));

    for (const file of files) {
      const filePath = path.join(pendingDir, file);
      const content = await fs.readFile(filePath, 'utf-8');

      // Parse the suggestion
      const profileMatch = content.match(/\*\*Profile:\*\* (.+)/);
      const categoryMatch = content.match(/\*\*Category:\*\* (.+)/);
      const severityMatch = content.match(/\*\*Severity:\*\* (.+)/);
      const summaryMatch = content.match(/## Summary\n([\s\S]+?)\n\n/);
      const reasonMatch = content.match(/## Reason\n([\s\S]+?)\n\n/);
      const suggestionMatch = content.match(/## Suggested Addition\n```markdown\n([\s\S]+?)\n```/);

      console.log(chalk.bold.cyan(`\n${'='.repeat(60)}`));
      console.log(chalk.bold.cyan(`File: ${file}`));
      console.log(chalk.bold.cyan('='.repeat(60)));
      console.log(chalk.bold('Profile:  ') + (profileMatch ? profileMatch[1] : 'unknown'));
      console.log(chalk.bold('Category: ') + (categoryMatch ? categoryMatch[1] : 'unknown'));
      console.log(chalk.bold('Severity: ') + (severityMatch ? severityMatch[1] : 'unknown'));
      console.log('');
      console.log(chalk.bold('Summary:'));
      console.log(summaryMatch ? summaryMatch[1].trim() : 'No summary');
      console.log('');
      console.log(chalk.bold('Reason:'));
      console.log(reasonMatch ? reasonMatch[1].trim() : 'No reason');
      console.log('');
      console.log(chalk.bold('Suggested Addition:'));
      console.log(chalk.gray(suggestionMatch ? suggestionMatch[1].trim() : 'No suggestion'));
      console.log('');

      const answer = await question(
        chalk.yellow('Action: (a)pprove, (r)eject, (s)kip, (q)uit? ')
      );

      if (answer.toLowerCase() === 'q') {
        console.log(chalk.blue('\nReview cancelled'));
        break;
      } else if (answer.toLowerCase() === 'a') {
        await fs.rename(filePath, path.join(approvedDir, file));
        console.log(chalk.green('✓ Approved'));
      } else if (answer.toLowerCase() === 'r') {
        const reason = await question(chalk.yellow('Rejection reason: '));
        const safeReason = sanitizeReason(reason);
        const rejectedFile = file.replace('.md', `-rejected-${safeReason}.md`);
        await fs.rename(filePath, path.join(rejectedDir, rejectedFile));
        console.log(chalk.red('✗ Rejected'));
      } else {
        console.log(chalk.blue('○ Skipped'));
      }
    }

    console.log(chalk.bold('\n✓ Review complete'));
    console.log(chalk.dim('Apply approved updates: npm run profile:apply\n'));

  } catch (error) {
    console.error(chalk.red('Error during review:'), error);
  } finally {
    rl.close();
  }
}

// ============================================================================
// Apply Approved Updates
// ============================================================================
async function applyApprovedUpdates() {
  const approvedDir = path.join(BASE_DIR, 'approved');
  const appliedDir = path.join(BASE_DIR, 'applied');

  await fs.mkdir(appliedDir, { recursive: true });

  try {
    const files = await fs.readdir(approvedDir);

    if (files.length === 0) {
      console.log(chalk.yellow('No approved updates to apply'));
      return;
    }

    console.log(chalk.bold(`\n🚀 Applying ${files.length} approved update(s)...\n`));

    for (const file of files) {
      const content = await fs.readFile(path.join(approvedDir, file), 'utf-8');

      // Parse the suggestion
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

        // Append to profile
        const profilePath = path.join(PROFILES_DIR, `${profileName}.md`);

        try {
          // Check if profile exists
          await fs.access(profilePath);

          // Create the addition with metadata
          const additionText = `\n\n### ${summary} [Added ${date}${issue ? `, Issue ${issue}` : ''}]\n${addition}\n`;

          await fs.appendFile(profilePath, additionText, 'utf-8');

          console.log(chalk.green(`✓ Applied update to ${profileName}.md`));
          console.log(chalk.dim(`  ${summary}`));

          // Move to applied
          await fs.rename(
            path.join(approvedDir, file),
            path.join(appliedDir, file)
          );

        } catch (error) {
          console.error(chalk.red(`✗ Failed to apply update to ${profileName}.md:`), error.message);
        }
      }
    }

    console.log(chalk.bold('\n✓ All updates applied'));
    console.log(chalk.dim('Remember to commit the updated profile files:\n'));
    console.log(chalk.dim('  git add .agent-system/profiles/*.md .claude/agents/*.md'));
    console.log(chalk.dim('  git commit -m "docs(agent): apply profile learnings"'));
    console.log(chalk.dim('  git push\n'));

  } catch (error) {
    console.error(chalk.red('Error applying updates:'), error);
  }
}

// ============================================================================
// Show Statistics
// ============================================================================
async function showStats() {
  const dirs = {
    pending: path.join(BASE_DIR, 'pending'),
    approved: path.join(BASE_DIR, 'approved'),
    applied: path.join(BASE_DIR, 'applied'),
    'auto-approved': path.join(BASE_DIR, 'auto-approved'),
    rejected: path.join(BASE_DIR, 'rejected'),
  };

  console.log(chalk.bold('\n📊 Profile Update Statistics\n'));

  const stats = {
    total: 0,
    byProfile: {},
    byCategory: {},
    bySeverity: {},
  };

  for (const [status, dir] of Object.entries(dirs)) {
    try {
      const files = await fs.readdir(dir);
      const count = files.length;

      console.log(`${chalk.bold(status.padEnd(15))} ${count}`);

      stats.total += count;

      // Parse files for detailed stats
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
      console.log(`${chalk.dim(status.padEnd(15))} 0`);
    }
  }

  console.log(chalk.bold(`${'Total'.padEnd(15)} ${stats.total}\n`));

  if (Object.keys(stats.byProfile).length > 0) {
    console.log(chalk.bold('By Profile:'));
    for (const [profile, count] of Object.entries(stats.byProfile)) {
      console.log(`  ${profile.padEnd(20)} ${count}`);
    }
    console.log('');
  }

  if (Object.keys(stats.byCategory).length > 0) {
    console.log(chalk.bold('By Category:'));
    for (const [category, count] of Object.entries(stats.byCategory)) {
      console.log(`  ${category.padEnd(20)} ${count}`);
    }
    console.log('');
  }

  if (Object.keys(stats.bySeverity).length > 0) {
    console.log(chalk.bold('By Severity:'));
    for (const [severity, count] of Object.entries(stats.bySeverity)) {
      const color =
        severity === 'critical' ? chalk.red :
        severity === 'important' ? chalk.yellow :
        chalk.blue;
      console.log(`  ${color(severity.padEnd(20))} ${count}`);
    }
    console.log('');
  }
}

// ============================================================================
// CLI Setup
// ============================================================================
const program = new Command();

program
  .name('profile-updates')
  .description('Manage agent profile updates')
  .version('1.0.0');

program
  .command('list')
  .description('List pending profile updates')
  .action(listPendingUpdates);

program
  .command('review')
  .description('Interactive review of pending updates')
  .action(interactiveReview);

program
  .command('apply')
  .description('Apply all approved updates to profiles')
  .action(applyApprovedUpdates);

program
  .command('stats')
  .description('Show profile update statistics')
  .action(showStats);

program.parse();

// If no command specified, show help
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
