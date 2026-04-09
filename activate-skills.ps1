# activate-skills.ps1
# ============================================================
# Stageira Skills — One-Command MCP Activation for Windows
# ============================================================
# LOCAL mode (reads from this directory):
#     .\activate-skills.ps1
#
# GITHUB mode (fetches from your GitHub repo):
#     .\activate-skills.ps1 -GithubRepo "yourusername/git-n-rust-skills"
#     .\activate-skills.ps1 -GithubRepo "yourusername/git-n-rust-skills" -Branch "main"
#     .\activate-skills.ps1 -GithubRepo "yourusername/git-n-rust-skills" -GithubToken "ghp_xxx"
# ============================================================

param(
    [string]$GithubRepo  = "",
    [string]$Branch      = "main",
    [string]$GithubToken = "",
    [switch]$ForceLocal
)

$ErrorActionPreference = "Stop"
$SkillsRoot    = $PSScriptRoot
$ServerScript  = Join-Path $SkillsRoot "mcp_server\server.py"
$RequirementsFile = Join-Path $SkillsRoot "mcp_server\requirements.txt"

# ── Determine mode ────────────────────────────────────────────────────────────
$IsGitHubMode = ($GithubRepo -ne "") -and (-not $ForceLocal)
$ModeLabel    = if ($IsGitHubMode) { "GitHub ($GithubRepo @ $Branch)" } else { "Local ($SkillsRoot)" }

# ── Banner ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   Stageira Skills — MCP Activator                ║" -ForegroundColor Cyan
Write-Host "  ║   Mode: $ModeLabel" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check Python ──────────────────────────────────────────────────────
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow

$PythonCmd = $null
foreach ($c in @("python", "python3", "py")) {
    try {
        $v = & $c --version 2>&1
        if ($v -match "Python 3\.") { $PythonCmd = $c; break }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Host "  ✗ Python 3 not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ $($PythonCmd): $(& $PythonCmd --version 2>&1)" -ForegroundColor Green

# ── Step 2: Install deps ──────────────────────────────────────────────────────
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
& $PythonCmd -m pip install -q -r $RequirementsFile
Write-Host "  ✓ mcp, pyyaml, pydantic installed" -ForegroundColor Green

# ── Step 3: Find config ───────────────────────────────────────────────────────
Write-Host "[3/4] Locating Claude Desktop config..." -ForegroundColor Yellow

$ClaudeConfigDir  = Join-Path $env:APPDATA "Claude"
$ClaudeConfigFile = Join-Path $ClaudeConfigDir "claude_desktop_config.json"
if (-not (Test-Path $ClaudeConfigDir)) {
    New-Item -ItemType Directory -Path $ClaudeConfigDir -Force | Out-Null
}
Write-Host "  ✓ $ClaudeConfigFile" -ForegroundColor Green

# ── Step 4: Build server args & register ─────────────────────────────────────
Write-Host "[4/4] Registering stageira-skills MCP server..." -ForegroundColor Yellow

$PythonPath = (Get-Command $PythonCmd).Source

# Build arg list based on mode
if ($IsGitHubMode) {
    $ServerArgs = @($ServerScript, "--github-repo", $GithubRepo, "--branch", $Branch)
} else {
    $ServerArgs = @($ServerScript, "--skills-root", $SkillsRoot)
}

$EnvVars = @{ PYTHONPATH = $SkillsRoot }
if ($GithubToken -ne "") {
    $EnvVars["GITHUB_TOKEN"] = $GithubToken
    Write-Host "  ✓ GitHub token added to environment" -ForegroundColor Green
}

# Load / create config
$config = @{ mcpServers = @{} }
if (Test-Path $ClaudeConfigFile) {
    try {
        $config = (Get-Content $ClaudeConfigFile -Raw -Encoding UTF8) | ConvertFrom-Json -AsHashtable
        if (-not $config.ContainsKey("mcpServers")) { $config["mcpServers"] = @{} }
        Write-Host "  ✓ Loaded existing config (other servers preserved)" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Could not parse existing config — starting fresh" -ForegroundColor Yellow
        $config = @{ mcpServers = @{} }
    }
}

$config["mcpServers"]["stageira-skills"] = @{
    command = $PythonPath
    args    = $ServerArgs
    env     = $EnvVars
}

($config | ConvertTo-Json -Depth 10) | Set-Content -Path $ClaudeConfigFile -Encoding UTF8
Write-Host "  ✓ 'stageira-skills' registered in Claude config" -ForegroundColor Green

# ── Show summary ──────────────────────────────────────────────────────────────
$SkillCount = (Get-ChildItem -Path $SkillsRoot -Recurse -Filter "SKILL.md" -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "  ══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅  ACTIVATION COMPLETE" -ForegroundColor Green
Write-Host "  ══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Mode:    $ModeLabel" -ForegroundColor White
Write-Host "  Config:  $ClaudeConfigFile" -ForegroundColor White
if ($IsGitHubMode) {
    Write-Host "  Cache:   $env:USERPROFILE\.cache\stageira-skills\" -ForegroundColor White
    Write-Host "  Refresh: Claude calls reload_skills() to pull latest from GitHub" -ForegroundColor DarkGray
} else {
    Write-Host "  Skills:  $SkillCount SKILL.md files found locally" -ForegroundColor White
}
Write-Host ""
Write-Host "  NEXT STEP: Restart Claude Desktop" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Available tools in Claude:" -ForegroundColor White
Write-Host "    list_skills()            — Browse all skills" -ForegroundColor Cyan
Write-Host "    search_skills('query')   — Find skills by keyword" -ForegroundColor Cyan
Write-Host "    read_skill('name')       — Load full skill instructions" -ForegroundColor Cyan
Write-Host "    reload_skills()          — Pull latest from GitHub" -ForegroundColor Cyan
Write-Host ""

# ── Optionally restart Claude ─────────────────────────────────────────────────
$claudeExe = "$env:LOCALAPPDATA\Claude\Claude.exe"
if (Test-Path $claudeExe) {
    $ans = Read-Host "  Restart Claude Desktop now? [Y/n]"
    if ($ans -eq "" -or $ans -match "^[Yy]") {
        Stop-Process -Name "Claude" -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        Start-Process $claudeExe
        Write-Host "  ✓ Claude Desktop restarted." -ForegroundColor Green
    }
}
Write-Host ""
