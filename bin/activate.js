#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const process = require('process');
const os = require('os');
const { spawnSync } = require('child_process');

console.log("\n📦 Scaffolding Stageira Skills via npx...\n");

function fetchLatestSkills() {
    console.log("==> 1. Fetching latest skills from GitHub...");
    let tempDir;
    try {
        tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stageira-skills-'));
        const cloneRes = spawnSync('git', ['clone', '--depth', '1', 'https://github.com/sVm19/git-n-rust-skills.git', tempDir], { stdio: 'ignore' });
        
        if (cloneRes.status === 0) {
            return { root: tempDir, isTemp: true };
        } else {
            console.warn("⚠️ Failed to pull from GitHub. Falling back to local package cache.");
            // If failed, clean up the empty temp dir
            fs.rmSync(tempDir, { recursive: true, force: true });
            return { root: path.join(__dirname, ".."), isTemp: false };
        }
    } catch (e) {
        console.warn("⚠️ Error pulling from GitHub:", e.message, "\nFalling back to local package cache.");
        return { root: path.join(__dirname, ".."), isTemp: false };
    }
}

function parseSkillFrontmatter(skillPath) {
    const text = fs.readFileSync(skillPath, { encoding: "utf-8" });
    const match = text.match(/^---\s*\n([\s\S]*?)\n---/);
    
    let meta = {
        name: path.basename(path.dirname(skillPath)),
        description: "",
        body: text
    };
    
    if (match) {
        meta.body = text.substring(match[0].length);
        const block = match[1];
        const lines = block.split('\n');
        for (const line of lines) {
            const idx = line.indexOf(':');
            if (idx !== -1) {
                const key = line.substring(0, idx).trim();
                let val = line.substring(idx + 1).trim();
                // strip quotes
                if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
                    val = val.substring(1, val.length - 1);
                }
                meta[key] = val;
            }
        }
    }
    return meta;
}

function collectSkills(root) {
    let skills = [];
    
    const entries = fs.readdirSync(root, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.isDirectory() && /^\d+/.test(entry.name)) {
            const catPath = path.join(root, entry.name);
            const walk = (dir) => {
                const subEntries = fs.readdirSync(dir, { withFileTypes: true });
                for (const sub of subEntries) {
                    const res = path.join(dir, sub.name);
                    if (sub.isDirectory()) {
                        walk(res);
                    } else if (sub.name === 'SKILL.md') {
                        let meta = parseSkillFrontmatter(res);
                        meta.category = entry.name;
                        meta.path = res;
                        skills.push(meta);
                    }
                }
            };
            walk(catPath);
        }
    }
    return skills;
}

function initProject(projectDir, skills) {
    if (!skills.length) return { claude: "[--] No skills found", codex: "[--] No skills found" };
    
    const skillsDir = path.join(projectDir, ".rustskills");
    fs.mkdirSync(skillsDir, { recursive: true });
    
    // Write the skill markdown files into .rustskills/
    for (const s of skills) {
        const skillFile = path.join(skillsDir, `${s.name}.md`);
        const header = `---\nname: ${s.name}\ndescription: ${s.description}\n---\n`;
        fs.writeFileSync(skillFile, header + s.body, "utf-8");
    }
    
    // Build CLAUDE.md for Claude agents
    let claudeLines = [
        "# Stageira Skills\n",
        "This project includes an AI skill library. Scoped rules live in `.rustskills/`.\n",
        "## Available Skills\n"
    ];
    
    for (const s of skills) {
        let desc = s.description.substring(0, 120);
        claudeLines.push(`- **${s.name}** (${s.category}): ${desc}`);
    }
    
    claudeLines.push("\n## How To Use\n");
    claudeLines.push("Just describe what you need. AI will match your request to the right skill via the rule files in `.rustskills/`.\n");
    fs.writeFileSync(path.join(projectDir, "CLAUDE.md"), claudeLines.join("\n"), "utf-8");
    
    // Build AGENTS.md for Codex / other agents
    let codexLines = [
        "# Stageira Skills — Agent Instructions\n",
        "This project includes an AI skill library. Codex reads this file and the per-skill files inside `.rustskills/` automatically.\n",
        "## Skill Index\n"
    ];
    
    for (const s of skills) {
        let desc = s.description.substring(0, 120);
        codexLines.push(`- **${s.name}** (${s.category}): ${desc}`);
        codexLines.push(`  → Full instructions: \`.rustskills/${s.name}.md\``);
    }
    
    codexLines.push("\n## How To Use\n");
    codexLines.push("Describe your task. The right skill will be matched automatically. If you need a specific skill, reference its name directly.\n");
    fs.writeFileSync(path.join(projectDir, "AGENTS.md"), codexLines.join("\n"), "utf-8");
    
    return {
        claude: `[OK] CLAUDE.md generated`,
        codex: `[OK] AGENTS.md generated`,
        skills: `[OK] ${skills.length} skills in .rustskills/`
    };
}

function main() {
    const targetDir = process.cwd();
    let skillsRootData;
    let skills = [];
    
    try {
        skillsRootData = fetchLatestSkills();
        skills = collectSkills(skillsRootData.root);
    } catch (e) {
        console.error("❌ Failed to collect skills:", e.message);
        process.exit(1);
    } finally {
        if (skillsRootData && skillsRootData.isTemp) {
            try {
                fs.rmSync(skillsRootData.root, { recursive: true, force: true });
            } catch (e) { /* ignore cleanup errors */ }
        }
    }
    
    console.log(`    Found ${skills.length} skills!`);
    
    console.log(`\n==> 2. Generating project-level skill dirs in ${targetDir}...`);
    
    const statuses = initProject(targetDir, skills);
    
    console.log(`  Claude Config    (CLAUDE.md)   ${statuses.claude}`);
    console.log(`  Codex Config     (AGENTS.md)   ${statuses.codex}`);
    console.log(`  Skills Logic   (.rustskills/)  ${statuses.skills}`);
    
    console.log(`\n  Files written to: ${targetDir}`);
    console.log("  Commit these to your repo so agents auto-discover them.\n");
}

main();
