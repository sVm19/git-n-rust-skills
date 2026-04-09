# deactivate.git-n-rust-skills.ps1
# Remove stageira-skills from ALL detected coding agent configs

$ErrorActionPreference = "Stop"
$ServerKey = "stageira-skills"

function Green($msg)  { Write-Host $msg -ForegroundColor Green }
function Gray($msg)   { Write-Host $msg -ForegroundColor DarkGray }
function Yellow($msg) { Write-Host $msg -ForegroundColor Yellow }

Write-Host ""
Write-Host "  Removing 'stageira-skills' from all coding agents..." -ForegroundColor Cyan
Write-Host ""

function Remove-McpEntry {
    param([string]$ConfigPath, [string]$Key, [string]$AgentName)
    if (-not (Test-Path $ConfigPath)) {
        Gray "  –  $AgentName  (config not found — skipped)"
        return
    }
    try {
        $config = (Get-Content $ConfigPath -Raw -Encoding UTF8) | ConvertFrom-Json -AsHashtable
        if ($config.ContainsKey("mcpServers") -and $config["mcpServers"].ContainsKey($Key)) {
            $config["mcpServers"].Remove($Key)
            ($config | ConvertTo-Json -Depth 10) | Set-Content -Path $ConfigPath -Encoding UTF8
            Green "  ✓  $AgentName  →  removed"
        } else {
            Gray "  –  $AgentName  (not registered — skipped)"
        }
    } catch {
        Yellow "  ⚠  $AgentName  (parse error: $_)"
    }
}

function Remove-ZedEntry {
    param([string]$ConfigPath)
    if (-not (Test-Path $ConfigPath)) { Gray "  –  Zed  (config not found — skipped)"; return }
    try {
        $config = (Get-Content $ConfigPath -Raw -Encoding UTF8) | ConvertFrom-Json -AsHashtable
        if ($config.ContainsKey("context_servers") -and $config["context_servers"].ContainsKey($ServerKey)) {
            $config["context_servers"].Remove($ServerKey)
            ($config | ConvertTo-Json -Depth 10) | Set-Content -Path $ConfigPath -Encoding UTF8
            Green "  ✓  Zed  →  removed"
        } else { Gray "  –  Zed  (not registered — skipped)" }
    } catch { Yellow "  ⚠  Zed  (parse error: $_)" }
}

Remove-McpEntry (Join-Path $env:APPDATA "Claude\claude_desktop_config.json") $ServerKey "Claude Desktop"
Remove-McpEntry (Join-Path $env:USERPROFILE ".cursor\mcp.json") $ServerKey "Cursor"
Remove-McpEntry (Join-Path $env:USERPROFILE ".codeium\windsurf\mcp_server_config.json") $ServerKey "Windsurf"
Remove-McpEntry (Join-Path $env:APPDATA "Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json") $ServerKey "VS Code / Cline"
Remove-ZedEntry (Join-Path $env:APPDATA "Zed\settings.json")
Remove-McpEntry (Join-Path $env:USERPROFILE ".continue\config.json") $ServerKey "Continue.dev"

Write-Host ""
Yellow "  Restart any open editors to complete deactivation."
Write-Host ""
