#!/usr/bin/env node

const { Command } = require('commander');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

// Find project root
function findProjectRoot() {
  let current = process.cwd();
  while (current !== '/') {
    const agentDir = path.join(current, '.claude');
    try {
      fs.accessSync(agentDir);
      return current;
    } catch {
      current = path.dirname(current);
    }
  }
  return path.resolve(__dirname, '../..');
}

const PROJECT_ROOT = findProjectRoot();
const RULES_FILE = path.join(__dirname, 'agent-validation-rules.json');

// Load validation rules
function loadRules() {
  try {
    const content = fs.readFileSync(RULES_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(chalk.red('Error loading validation rules:'), error.message);
    process.exit(1);
  }
}

// Interactive checklist
function interactiveChecklist(agentName, category) {
  const rules = loadRules();
  const agent = rules[agentName];

  if (!agent) {
    console.error(chalk.red(`Unknown agent: ${agentName}`));
    console.log(chalk.yellow('Available agents:'), Object.keys(rules).join(', '));
    process.exit(1);
  }

  console.log(chalk.bold.blue(`\n${agent.role} - ${category || 'All Checks'}\n`));

  let allChecks = [];
  let categoryName = '';

  if (category) {
    if (agent.required_checks && agent.required_checks[category]) {
      allChecks = agent.required_checks[category];
      categoryName = category;
    } else {
      console.error(chalk.red(`Unknown category: ${category}`));
      console.log(chalk.yellow('Available categories:'), Object.keys(agent.required_checks || {}).join(', '));
      process.exit(1);
    }
  } else {
    // Show all checks
    if (agent.startup_sequence) {
      console.log(chalk.bold.cyan('Startup Sequence:'));
      agent.startup_sequence.forEach((step, i) => {
        console.log(chalk.cyan(`${i + 1}.`), step);
      });
      console.log();
    }

    if (agent.pre_analysis) {
      console.log(chalk.bold.cyan('Pre-Analysis Required:'));
      agent.pre_analysis.forEach((step, i) => {
        console.log(chalk.cyan(`${i + 1}.`), step);
      });
      console.log();
    }

    if (agent.critical_enforcement) {
      console.log(chalk.bold.red('CRITICAL ENFORCEMENT:'));
      Object.entries(agent.critical_enforcement).forEach(([key, rule]) => {
        console.log(chalk.red(`\n${key}:`));
        console.log(chalk.yellow(`  ${rule.description}`));
        if (rule.required_command) {
          console.log(chalk.white(`  Required: ${rule.required_command}`));
        }
        if (rule.validation_command) {
          console.log(chalk.white(`  Check: ${rule.validation_command}`));
        }
        if (rule.validation) {
          console.log(chalk.white(`  Verify: ${rule.validation}`));
        }
        if (rule.failure_message) {
          console.log(chalk.red(`  If failed: ${rule.failure_message}`));
        }
      });
      console.log();
    }

    if (agent.absolute_rejection_criteria) {
      console.log(chalk.bold.red('Absolute Rejection Criteria:'));
      agent.absolute_rejection_criteria.forEach((criterion, i) => {
        console.log(chalk.red(`${i + 1}.`), criterion);
      });
      console.log();
    }

    if (agent.review_phases) {
      console.log(chalk.bold.magenta('Review Phases:'));
      Object.entries(agent.review_phases).forEach(([phase, description]) => {
        console.log(chalk.magenta(`${phase}:`), description);
      });
      console.log();
    }

    if (agent.required_checks) {
      Object.entries(agent.required_checks).forEach(([cat, checks]) => {
        console.log(chalk.bold.green(`${cat.replace(/_/g, ' ').toUpperCase()}:`));
        checks.forEach((check, i) => {
          console.log(chalk.green(`  ${i + 1}.`), check);
        });
        console.log();
      });
    }
    return;
  }

  // Display checklist for specific category
  console.log(chalk.bold.green(`${categoryName.replace(/_/g, ' ').toUpperCase()}:\n`));
  allChecks.forEach((check, i) => {
    console.log(chalk.green(`  ☐ ${i + 1}.`), check);
  });
  console.log();

  console.log(chalk.yellow('Copy this checklist and mark items as complete: ☐ → ☑'));
}

// Validate completion
function validateCompletion(agentName, category, checkboxList) {
  const rules = loadRules();
  const agent = rules[agentName];

  if (!agent || !agent.required_checks || !agent.required_checks[category]) {
    console.error(chalk.red('Invalid agent or category'));
    process.exit(1);
  }

  const requiredChecks = agent.required_checks[category];
  const completedCount = (checkboxList.match(/☑/g) || []).length;
  const totalRequired = requiredChecks.length;

  console.log(chalk.bold.blue(`\nValidation Results for ${agent.role} - ${category}\n`));

  if (completedCount >= totalRequired) {
    console.log(chalk.green('✅ ALL REQUIRED CHECKS COMPLETED'));
    console.log(chalk.green(`   ${completedCount}/${totalRequired} items verified\n`));
    return true;
  } else {
    console.log(chalk.red('❌ INCOMPLETE - CANNOT PROCEED'));
    console.log(chalk.red(`   ${completedCount}/${totalRequired} items completed`));
    console.log(chalk.red(`   ${totalRequired - completedCount} items still required\n`));

    console.log(chalk.yellow('Missing items:'));
    requiredChecks.forEach((check, i) => {
      const checkPattern = new RegExp(`${i + 1}\\..*☑`, 'g');
      if (!checkboxList.match(checkPattern)) {
        console.log(chalk.yellow(`  ☐ ${i + 1}.`), check);
      }
    });
    console.log();
    return false;
  }
}

// Show summary
function showSummary(agentName) {
  const rules = loadRules();
  const agent = rules[agentName];

  if (!agent) {
    console.error(chalk.red(`Unknown agent: ${agentName}`));
    process.exit(1);
  }

  console.log(chalk.bold.blue(`\n${agent.role} - Validation Summary\n`));

  let totalChecks = 0;

  if (agent.startup_sequence) {
    console.log(chalk.cyan('Startup sequence:'), agent.startup_sequence.length, 'steps');
    totalChecks += agent.startup_sequence.length;
  }

  if (agent.pre_analysis) {
    console.log(chalk.cyan('Pre-analysis:'), agent.pre_analysis.length, 'steps');
    totalChecks += agent.pre_analysis.length;
  }

  if (agent.absolute_rejection_criteria) {
    console.log(chalk.red('Rejection criteria:'), agent.absolute_rejection_criteria.length, 'items');
    totalChecks += agent.absolute_rejection_criteria.length;
  }

  if (agent.required_checks) {
    Object.entries(agent.required_checks).forEach(([category, checks]) => {
      console.log(chalk.green(`${category}:`), checks.length, 'required checks');
      totalChecks += checks.length;
    });
  }

  console.log(chalk.bold(`\nTotal validation points: ${totalChecks}\n`));
}

// CLI Program
const program = new Command();

program
  .name('validate-agent')
  .description('Agent task completion validation tool')
  .version('1.0.0');

program
  .command('checklist <agent> [category]')
  .description('Show interactive checklist for an agent')
  .action((agent, category) => {
    interactiveChecklist(agent, category);
  });

program
  .command('validate <agent> <category>')
  .description('Validate checklist completion (pipe checklist to stdin)')
  .action((agent, category) => {
    let input = '';
    process.stdin.on('data', chunk => input += chunk);
    process.stdin.on('end', () => {
      const isValid = validateCompletion(agent, category, input);
      process.exit(isValid ? 0 : 1);
    });
  });

program
  .command('summary <agent>')
  .description('Show validation summary for an agent')
  .action((agent) => {
    showSummary(agent);
  });

program
  .command('list')
  .description('List all available agents and their categories')
  .action(() => {
    const rules = loadRules();
    console.log(chalk.bold.blue('\nAvailable Agents:\n'));

    Object.entries(rules).forEach(([name, config]) => {
      console.log(chalk.green(`${name}:`), config.role);
      if (config.required_checks) {
        console.log(chalk.yellow('  Categories:'), Object.keys(config.required_checks).join(', '));
      }
      console.log();
    });
  });

program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
