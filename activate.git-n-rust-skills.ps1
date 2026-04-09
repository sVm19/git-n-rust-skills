# activate.git-n-rust-skills.ps1
# ============================================================
# Stageira Skills — Universal MCP Activator (All Coding Agents)
# ============================================================
#
# LOCAL mode (reads from this directory):
#     .\activate.git-n-rust-skills.ps1
#
# GITHUB mode (no local clone needed on any machine):
#     .\activate.git-n-rust-skills.ps1 -GithubRepo "you/git-n-rust-skills"
#     .\activate.git-n-rust-skills.ps1 -GithubRepo "you/git-n-rust-skills" -Branch "main"
#     .\activate.git-n-rust-skills.ps1 -GithubRepo "you/repo" -GithubToken "ghp_xxx"
#
# Registers with ALL detected MCP-compatible agents:
#   Claude Desktop | Cursor | Windsurf | VS Code (Cline) | Zed
# ============================================================

param(
    [string]$GithubRepo  = "",
    [string]$Branch      = "main",
    [string]$GithubToken = "",
    [switch]$ForceLocal,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$SkillsRoot   = $PSScriptRoot
$ServerScript = Join-Path $SkillsRoot "mcp_server\server.py"
$ReqFile      = Join-Path $SkillsRoot "mcp_server\requirements.txt"
$IsGitHub     = ($GithubRepo -ne "") -and (-not $ForceLocal)
$ModeLabel    = if ($IsGitHub) { "GitHub ($GithubRepo @ $Branch)" } else { "Local" }

# ── Colors ────────────────────────────────────────────────────────────────────
function Green($msg)  { Write-Host $msg -ForegroundColor Green }
function Yellow($msg) { Write-Host $msg -ForegroundColor Yellow }
function Cyan($msg)   { Write-Host $msg -ForegroundColor Cyan }
function Red($msg)    { Write-Host $msg -ForegroundColor Red }
function Gray($msg)   { Write-Host $msg -ForegroundColor DarkGray }

# ── Banner ────────────────────────────────────────────────────────────────────
Write-Host ""
Cyan "  ╔══════════════════════════════════════════════════╗"
Cyan "  ║  git-n-rust-skills — Universal MCP Activator    ║"
Cyan "  ║  Mode: $ModeLabel"
Cyan "  ╚══════════════════════════════════════════════════╝"
Write-Host ""

# ── Step 1: Python ────────────────────────────────────────────────────────────
Yellow "[1/4] Checking Python..."
$PythonCmd = $null
foreach ($c in @("python", "python3", "py")) {
    try { if ((& $c --version 2>&1) -match "Python 3\.") { $PythonCmd = $c; break } } catch {}
}
if (-not $PythonCmd) { Red "  ✗ Python 3 not found. Install from https://python.org"; exit 1 }
Green "  ✓ $PythonCmd $(& $PythonCmd --version 2>&1)"
$PythonPath = (Get-Command $PythonCmd).Source

# ── Step 2: Install deps ──────────────────────────────────────────────────────
Yellow "[2/4] Installing dependencies..."
if (-not $DryRun) { & $PythonCmd -m pip install -q -r $ReqFile }
Green "  ✓ mcp, pyyaml, pydantic ready"

# ── Step 3: Build server entry ────────────────────────────────────────────────
Yellow "[3/4] Building MCP server configuration..."

if ($IsGitHub) {
    $ServerArgs = @($ServerScript, "--github-repo", $GithubRepo, "--branch", $Branch)
} else {
    $ServerArgs = @($ServerScript, "--skills-root", $SkillsRoot)
}

$EnvVars = @{ PYTHONPATH = $SkillsRoot }
if ($GithubToken -ne "") { $EnvVars["GITHUB_TOKEN"] = $GithubToken }

# Standard mcpServers entry (Claude Desktop / Cursor / Windsurf format)
$serverEntry = @{
    command = $PythonPath
    args    = $ServerArgs
    env     = $EnvVars
}

# Zed format (context_servers, different shape)
$zedEntry = @{
    command = @{
        path = $PythonPath
        args = $ServerArgs
        env  = $EnvVars
    }
}

Green "  ✓ Server entry built"

# ─────────────────────────────────────────────────────────────────────────────
# Helper: merge mcpServers-style JSON config
# ─────────────────────────────────────────────────────────────────────────────
function Merge-McpConfig {
    param([string]$ConfigPath, [string]$ServerKey, [hashtable]$Entry)
    $config = @{ mcpServers = @{} }
    if (Test-Path $ConfigPath) {
        try {
            $raw = Get-Content $ConfigPath -Raw -Encoding UTF8
            $parsed = $raw | ConvertFrom-Json -AsHashtable
            $config = $parsed
            if (-not $config.ContainsKey("mcpServers")) { $config["mcpServers"] = @{} }
        } catch { $config = @{ mcpServers = @{} } }
    }
    $config["mcpServers"][$ServerKey] = $Entry
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path (Split-Path $ConfigPath) -Force | Out-Null
        ($config | ConvertTo-Json -Depth 10) | Set-Content -Path $ConfigPath -Encoding UTF8
    }
}

# Helper: merge Zed context_servers JSON config
function Merge-ZedConfig {
    param([string]$ConfigPath, [string]$ServerKey, [hashtable]$Entry)
    $config = @{}
    if (Test-Path $ConfigPath) {
        try { $config = (Get-Content $ConfigPath -Raw -Encoding UTF8) | ConvertFrom-Json -AsHashtable } catch {}
    }
    if (-not $config.ContainsKey("context_servers")) { $config["context_servers"] = @{} }
    $config["context_servers"][$ServerKey] = $Entry
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path (Split-Path $ConfigPath) -Force | Out-Null
        ($config | ConvertTo-Json -Depth 10) | Set-Content -Path $ConfigPath -Encoding UTF8
    }
}

# ── Step 4: Register with every detected agent ────────────────────────────────
Yellow "[4/4] Detecting and registering with coding agents..."
Write-Host ""

$results = @()

# ────────────────────────────── Claude Desktop ────────────────────────────────
$claudeConfig = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
$claudeExe    = Join-Path $env:LOCALAPPDATA "Claude\Claude.exe"
$claudeDetected = (Test-Path $claudeConfig) -or (Test-Path $claudeExe) -or
                  (Test-Path (Join-Path $env:APPDATA "Claude"))
if ($claudeDetected) {
    Merge-McpConfig -ConfigPath $claudeConfig -ServerKey "stageira-skills" -Entry $serverEntry
    Green "  ✓ Claude Desktop  →  $claudeConfig"
    $results += [PSCustomObject]@{ Agent = "Claude Desktop"; Status = "✅ Registered"; Config = $claudeConfig }
} else {
    Gray "  –  Claude Desktop     not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "Claude Desktop"; Status = "– Not found"; Config = "" }
}

# ──────────────────────────────── Cursor ─────────────────────────────────────
$cursorConfig  = Join-Path $env:USERPROFILE ".cursor\mcp.json"
$cursorExe     = Join-Path $env:LOCALAPPDATA "Programs\cursor\Cursor.exe"
$cursorAlt     = Join-Path $env:APPDATA "Cursor"
$cursorDetected = (Test-Path $cursorExe) -or (Test-Path $cursorAlt) -or
                  (Test-Path (Join-Path $env:USERPROFILE ".cursor"))
if ($cursorDetected) {
    Merge-McpConfig -ConfigPath $cursorConfig -ServerKey "stageira-skills" -Entry $serverEntry
    Green "  ✓ Cursor           →  $cursorConfig"
    $results += [PSCustomObject]@{ Agent = "Cursor"; Status = "✅ Registered"; Config = $cursorConfig }
} else {
    Gray "  –  Cursor             not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "Cursor"; Status = "– Not found"; Config = "" }
}

# ───────────────────────────── Windsurf ──────────────────────────────────────
$windsurfConfig  = Join-Path $env:USERPROFILE ".codeium\windsurf\mcp_server_config.json"
$windsurfExe     = Join-Path $env:LOCALAPPDATA "Programs\Windsurf\Windsurf.exe"
$windsurfAlt     = Join-Path $env:USERPROFILE ".codeium\windsurf"
$windsurfDetected = (Test-Path $windsurfExe) -or (Test-Path $windsurfAlt)
if ($windsurfDetected) {
    Merge-McpConfig -ConfigPath $windsurfConfig -ServerKey "stageira-skills" -Entry $serverEntry
    Green "  ✓ Windsurf         →  $windsurfConfig"
    $results += [PSCustomObject]@{ Agent = "Windsurf"; Status = "✅ Registered"; Config = $windsurfConfig }
} else {
    Gray "  –  Windsurf           not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "Windsurf"; Status = "– Not found"; Config = "" }
}

# ─────────────────────────── VS Code + Cline ─────────────────────────────────
# Cline stores its MCP config at a predictable globalStorage path
$vsCodeBase    = Join-Path $env:APPDATA "Code\User\globalStorage"
$clineConfig   = Join-Path $vsCodeBase "saoudrizwan.claude-dev\settings\cline_mcp_settings.json"
$vsCodeExe     = Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code\Code.exe"
$vsCodeDetected = (Test-Path $vsCodeExe) -or (Test-Path $vsCodeBase)
if ($vsCodeDetected) {
    Merge-McpConfig -ConfigPath $clineConfig -ServerKey "stageira-skills" -Entry $serverEntry
    Green "  ✓ VS Code (Cline)  →  $clineConfig"
    $results += [PSCustomObject]@{ Agent = "VS Code / Cline"; Status = "✅ Registered"; Config = $clineConfig }
} else {
    Gray "  –  VS Code / Cline    not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "VS Code / Cline"; Status = "– Not found"; Config = "" }
}

# ─────────────────────────────── Zed ─────────────────────────────────────────
# Zed uses "context_servers" key, different JSON shape
$zedConfig   = Join-Path $env:APPDATA "Zed\settings.json"
$zedExe      = Join-Path $env:LOCALAPPDATA "Programs\Zed\Zed.exe"
$zedDetected = (Test-Path $zedExe) -or (Test-Path (Join-Path $env:APPDATA "Zed"))
if ($zedDetected) {
    Merge-ZedConfig -ConfigPath $zedConfig -ServerKey "stageira-skills" -Entry $zedEntry
    Green "  ✓ Zed              →  $zedConfig"
    $results += [PSCustomObject]@{ Agent = "Zed"; Status = "✅ Registered"; Config = $zedConfig }
} else {
    Gray "  –  Zed                not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "Zed"; Status = "– Not found"; Config = "" }
}

# ─────────────────────────── Continue.dev ────────────────────────────────────
# Continue uses ~/.continue/config.json with a "mcpServers" array
$continueConfig   = Join-Path $env:USERPROFILE ".continue\config.json"
$continueDetected = (Test-Path (Join-Path $env:USERPROFILE ".continue"))
if ($continueDetected) {
    # Continue uses array format, not object format
    $cfg = @{}
    if (Test-Path $continueConfig) {
        try { $cfg = (Get-Content $continueConfig -Raw -Encoding UTF8) | ConvertFrom-Json -AsHashtable } catch {}
    }
    if (-not $cfg.ContainsKey("mcpServers")) { $cfg["mcpServers"] = @() }
    # Remove existing stageira-skills entry if present
    $cfg["mcpServers"] = @($cfg["mcpServers"] | Where-Object { $_.name -ne "stageira-skills" })
    $cfg["mcpServers"] += @{
        name    = "stageira-skills"
        command = $PythonPath
        args    = $ServerArgs
        env     = $EnvVars
    }
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path (Split-Path $continueConfig) -Force | Out-Null
        ($cfg | ConvertTo-Json -Depth 10) | Set-Content -Path $continueConfig -Encoding UTF8
    }
    Green "  ✓ Continue.dev     →  $continueConfig"
    $results += [PSCustomObject]@{ Agent = "Continue.dev"; Status = "✅ Registered"; Config = $continueConfig }
} else {
    Gray "  –  Continue.dev       not detected (skipped)"
    $results += [PSCustomObject]@{ Agent = "Continue.dev"; Status = "– Not found"; Config = "" }
}

# ── Summary table ─────────────────────────────────────────────────────────────
Write-Host ""
$registered = ($results | Where-Object { $_.Status -like "✅*" }).Count
Write-Host "  ══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅  DONE — Registered with $registered / $($results.Count) agents" -ForegroundColor Green
Write-Host "  ══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

foreach ($r in $results) {
    if ($r.Status -like "✅*") {
        Write-Host ("  {0,-20} {1}" -f $r.Agent, $r.Status) -ForegroundColor Green
    } else {
        Write-Host ("  {0,-20} {1}" -f $r.Agent, $r.Status) -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "  Mode:   $ModeLabel" -ForegroundColor White
if ($IsGitHub) {
    Write-Host "  Source: https://github.com/$GithubRepo" -ForegroundColor Cyan
    Write-Host "  Cache:  $env:USERPROFILE\.cache\stageira-skills\" -ForegroundColor DarkGray
}

Write-Host ""
Yellow "  NEXT STEP: Restart all open editors/agents to activate."
Write-Host ""
Write-Host "  Claude will then have:" -ForegroundColor White
Cyan "    list_skills()          — See all skills"
Cyan "    search_skills('query') — Find the right skill"
Cyan "    read_skill('name')     — Load full instructions"
Cyan "    reload_skills()        — Pull latest from GitHub"
Write-Host ""

if ($DryRun) { Yellow "  [DRY RUN] No files were modified." }

# ── Restart any running Claude Desktop ────────────────────────────────────────
$claudeExePath = Join-Path $env:LOCALAPPDATA "Claude\Claude.exe"
if ((Test-Path $claudeExePath) -and $registered -gt 0) {
    $ans = Read-Host "  Restart Claude Desktop now? [Y/n]"
    if ($ans -eq "" -or $ans -match "^[Yy]") {
        Stop-Process -Name "Claude" -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        Start-Process $claudeExePath
        Green "  ✓ Claude Desktop restarted."
    }
}
Write-Host ""
