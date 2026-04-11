#!/usr/bin/env node

const { spawnSync } = require("child_process");
const process = require("process");
const path = require("path");

console.log("\n📦 Starting git-n-rust-skills activation via npx...\n");

// Check for --init flag
const initIndex = process.argv.indexOf("--init");
const hasInit = initIndex !== -1;

console.log("==> 1. Checking Python environment...");
let pythonExe = "python";
let res = spawnSync("python", ["--version"]);
if (res.error || res.status !== 0) {
    res = spawnSync("python3", ["--version"]);
    if (res.error || res.status !== 0) {
        console.error("❌ Python is required but not found in PATH.");
        process.exit(1);
    }
    pythonExe = "python3";
}

console.log(`==> 2. Installing git-n-rust-skills pip module via ${pythonExe}...`);
const packageRoot = path.join(__dirname, "..");
const pipArgs = ["-m", "pip", "install", "--upgrade", packageRoot];
const installRes = spawnSync(pythonExe, pipArgs, { stdio: "inherit" });

if (installRes.status !== 0) {
    console.error("❌ Failed to install Python dependencies.");
    process.exit(1);
}

// Build activator args
const activatorArgs = ["-m", "mcp_server.activator"];
if (hasInit) {
    // Use the directory after --init, or cwd if none specified
    const initDir = process.argv[initIndex + 1] || process.cwd();
    activatorArgs.push("--init", initDir);
    console.log(`\n==> 3. Generating project-level skill dirs in ${initDir}...`);
} else {
    console.log("\n==> 3. Running MCP Server Activator...");
}

const activateRes = spawnSync(pythonExe, activatorArgs, { stdio: "inherit" });

if (activateRes.status !== 0) {
    process.exit(activateRes.status || 1);
}
