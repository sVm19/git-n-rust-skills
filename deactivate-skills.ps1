# deactivate-skills.ps1
# Remove stageira-skills from Claude Desktop MCP config

$ClaudeConfigFile = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"

if (-not (Test-Path $ClaudeConfigFile)) {
    Write-Host "No Claude config found at $ClaudeConfigFile" -ForegroundColor Yellow
    exit 0
}

$config = Get-Content $ClaudeConfigFile -Raw | ConvertFrom-Json -AsHashtable

if ($config.ContainsKey("mcpServers") -and $config["mcpServers"].ContainsKey("stageira-skills")) {
    $config["mcpServers"].Remove("stageira-skills")
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $ClaudeConfigFile -Encoding UTF8
    Write-Host "✓ Removed 'stageira-skills' from Claude Desktop config." -ForegroundColor Green
    Write-Host "  Restart Claude Desktop to apply." -ForegroundColor Yellow
} else {
    Write-Host "⚠ 'stageira-skills' was not registered — nothing to do." -ForegroundColor Yellow
}
