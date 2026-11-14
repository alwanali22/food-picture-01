import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// Output directory configuration for make.fun submission packaging
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const srcPath = path.join(scriptDir, 'entry.png');
const destPath = path.join(outputDir, 'entry.png');

fs.copyFileSync(srcPath, destPath);

// Verify copied file exists and is non-empty
if (!fs.existsSync(destPath) || fs.statSync(destPath).size === 0) {
  throw new Error(`Failed to copy entry.png to ${destPath}`);
}

console.log(`Successfully copied entry.png to ${destPath} (${fs.statSync(destPath).size} bytes)`);

