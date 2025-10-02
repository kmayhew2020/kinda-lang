const path = require('path');

// Test validateFilename function from index.js
function validateFilename(filename) {
  const basename = path.basename(filename);
  if (!basename.endsWith('.md')) {
    throw new Error('Invalid file extension - only .md files allowed');
  }
  if (basename !== filename || filename.includes('..') || filename.includes(path.sep)) {
    throw new Error('Invalid filename: path traversal detected');
  }
  if (filename.includes('\0') || /[<>:"|?*]/.test(filename)) {
    throw new Error('Invalid filename: contains illegal characters');
  }
  return basename;
}

// Test sanitizeReason function
function sanitizeReason(reason) {
  if (!reason || typeof reason !== 'string') {
    return 'no-reason';
  }
  return reason
    .replace(/[^a-zA-Z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 50) || 'no-reason';
}

// Test cases for validateFilename
const filenameCases = [
  { input: '2025-10-02-test.md', shouldPass: true, desc: 'Valid filename' },
  { input: '../../../etc/passwd', shouldPass: false, desc: 'Path traversal (Unix)' },
  { input: '../../.ssh/id_rsa', shouldPass: false, desc: 'Path traversal (ssh)' },
  { input: 'path/to/file.md', shouldPass: false, desc: 'Path with separators' },
  { input: 'test<script>.md', shouldPass: false, desc: 'HTML injection attempt' },
  { input: 'file.txt', shouldPass: false, desc: 'Wrong extension' },
  { input: 'test\0file.md', shouldPass: false, desc: 'Null byte injection' },
  { input: 'file|pipe.md', shouldPass: false, desc: 'Pipe character' },
  { input: 'file:colon.md', shouldPass: false, desc: 'Colon character' },
  { input: 'file"quote.md', shouldPass: false, desc: 'Quote character' },
  { input: 'file*wildcard.md', shouldPass: false, desc: 'Wildcard character' },
  { input: 'file?question.md', shouldPass: false, desc: 'Question mark' },
];

// Test cases for sanitizeReason
const reasonCases = [
  { input: 'Not relevant anymore', expected: 'Not-relevant-anymore', desc: 'Normal text' },
  { input: '<script>alert("xss")</script>', expected: 'scriptalertxssscript', desc: 'XSS attempt' },
  { input: '../../../etc/passwd', expected: 'etcpasswd', desc: 'Path traversal in reason' },
  { input: 'Test & Special | Chars / Here', expected: 'Test-Special-Chars-Here', desc: 'Special characters' },
  { input: '', expected: 'no-reason', desc: 'Empty string' },
  { input: null, expected: 'no-reason', desc: 'Null value' },
  { input: 'A'.repeat(100), expected: 'A'.repeat(50), desc: 'Length limit (100 chars)' },
];

console.log('=== SECURITY VALIDATION TEST RESULTS ===\n');

console.log('1. validateFilename() Tests:\n');
let passCount = 0;
let failCount = 0;

filenameCases.forEach(({ input, shouldPass, desc }) => {
  try {
    const result = validateFilename(input);
    if (shouldPass) {
      console.log('✅ PASS:', desc);
      console.log('   Input:', input, '→ Allowed:', result);
      passCount++;
    } else {
      console.log('❌ FAIL:', desc);
      console.log('   Input:', input, '→ SHOULD HAVE REJECTED but got:', result);
      failCount++;
    }
  } catch (error) {
    if (!shouldPass) {
      console.log('✅ PASS:', desc);
      console.log('   Input:', input, '→ Rejected:', error.message);
      passCount++;
    } else {
      console.log('❌ FAIL:', desc);
      console.log('   Input:', input, '→ SHOULD HAVE ALLOWED but got:', error.message);
      failCount++;
    }
  }
});

console.log('\n2. sanitizeReason() Tests:\n');

reasonCases.forEach(({ input, expected, desc }) => {
  const result = sanitizeReason(input);
  if (result === expected) {
    console.log('✅ PASS:', desc);
    console.log('   Input:', JSON.stringify(input), '→', result);
    passCount++;
  } else {
    console.log('❌ FAIL:', desc);
    console.log('   Input:', JSON.stringify(input));
    console.log('   Expected:', expected);
    console.log('   Got:', result);
    failCount++;
  }
});

console.log('\n=== SUMMARY ===');
console.log('Total Tests:', passCount + failCount);
console.log('Passed:', passCount);
console.log('Failed:', failCount);
console.log('Success Rate:', Math.round((passCount / (passCount + failCount)) * 100) + '%');

process.exit(failCount > 0 ? 1 : 0);
