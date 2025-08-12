// Ensures typedoc-types-parsed.json exists before docusaurus start.
const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, '..', 'node_modules', '@apify', 'docusaurus-plugin-typedoc-api', 'lib', 'plugin', 'python', 'type-parsing');
const rawFile = path.join(baseDir, 'typedoc-types.raw');
const parsedFile = path.join(baseDir, 'typedoc-types-parsed.json');
const scriptFile = path.join(__dirname, '..', 'node_modules', '@apify', 'docusaurus-plugin-typedoc-api', 'python-scripts', 'type-parsing', 'parse_types.py');

function ensureParsed() {
  if (fs.existsSync(parsedFile)) return;
  if (!fs.existsSync(rawFile)) {
    // create empty raw file so parser produces empty object
    fs.writeFileSync(rawFile, '[]', 'utf8');
  }
  try {
    const { spawnSync } = require('child_process');
    const res = spawnSync('python', [scriptFile, rawFile]);
    if (res.status !== 0) {
      console.warn('[patch-typedoc-plugin] Failed to generate parsed types:', res.stderr?.toString());
      if (!fs.existsSync(parsedFile)) {
        fs.writeFileSync(parsedFile, '{}', 'utf8');
      }
    }
  } catch (e) {
    console.warn('[patch-typedoc-plugin] Error generating parsed types', e);
    if (!fs.existsSync(parsedFile)) {
      fs.writeFileSync(parsedFile, '{}', 'utf8');
    }
  }
}

ensureParsed();
