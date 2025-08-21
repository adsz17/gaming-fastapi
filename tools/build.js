const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const distDir = path.join(repoRoot, 'dist');
const srcDir = path.join(repoRoot, 'frontend');

// Clean any existing dist directory
fs.rmSync(distDir, { recursive: true, force: true });
fs.mkdirSync(distDir, { recursive: true });

// Copy contents of frontend to dist
fs.cpSync(srcDir, distDir, { recursive: true });
