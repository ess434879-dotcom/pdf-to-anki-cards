#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const packageRoot = path.resolve(__dirname, "..");
const skillName = "pdf-to-anki-cards";

function usage() {
  console.log(`PDF to Anki Cards

Usage:
  pdf-to-anki-cards install --target claude|codex|all [--force]
  pdf-to-anki-cards install --dir /custom/skills/dir [--force]
  pdf-to-anki-cards path

Examples:
  npx github:ess434879-dotcom/pdf-to-anki-cards install --target claude
  npm install -g github:ess434879-dotcom/pdf-to-anki-cards
  pdf-to-anki-cards install --target codex --force
`);
}

function parseArgs(argv) {
  const opts = { target: "claude", force: false, dir: null };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--target") opts.target = argv[++i];
    else if (arg === "--dir") opts.dir = argv[++i];
    else if (arg === "--force") opts.force = true;
    else if (arg === "-h" || arg === "--help") opts.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return opts;
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
    fs.chmodSync(dest, stat.mode);
  }
}

function installTo(skillsDir, force) {
  const dest = path.join(skillsDir, skillName);
  if (fs.existsSync(dest)) {
    if (!force) {
      throw new Error(`${dest} already exists. Re-run with --force to replace it.`);
    }
    fs.rmSync(dest, { recursive: true, force: true });
  }
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of ["SKILL.md", "scripts", "references"]) {
    copyRecursive(path.join(packageRoot, entry), path.join(dest, entry));
  }
  return dest;
}

function targetDirs(target, customDir) {
  if (customDir) return [path.resolve(customDir)];
  const home = os.homedir();
  if (target === "claude") return [path.join(home, ".claude", "skills")];
  if (target === "codex") return [path.join(home, ".codex", "skills")];
  if (target === "all") {
    return [path.join(home, ".claude", "skills"), path.join(home, ".codex", "skills")];
  }
  throw new Error("--target must be claude, codex, or all");
}

function main() {
  const [command, ...rest] = process.argv.slice(2);
  if (!command || command === "help" || command === "--help" || command === "-h") {
    usage();
    return;
  }
  if (command === "path") {
    console.log(packageRoot);
    return;
  }
  if (command !== "install") {
    throw new Error(`Unknown command: ${command}`);
  }
  const opts = parseArgs(rest);
  if (opts.help) {
    usage();
    return;
  }
  const installed = targetDirs(opts.target, opts.dir).map((dir) => installTo(dir, opts.force));
  for (const dest of installed) {
    console.log(`Installed ${skillName} to ${dest}`);
  }
  console.log("Restart Claude Code/Codex or start a new session so the skill list refreshes.");
}

try {
  main();
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
