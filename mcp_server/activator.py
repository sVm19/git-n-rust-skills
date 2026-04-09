import json
import os
import sys
import platform
from pathlib import Path

def get_python_exe():
    return sys.executable

def merge_mcp_config(config_path: Path, server_key: str, entry: dict):
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}
        
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        
    config["mcpServers"][server_key] = entry
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def merge_zed_config(config_path: Path, server_key: str, entry: dict):
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    else:
        config = {}
        
    if "context_servers" not in config:
        config["context_servers"] = {}
        
    config["context_servers"][server_key] = entry
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def main():
    print("")
    print("  +==================================================+")
    print("  |  git-n-rust-skills -- Universal MCP Activator   |")
    print("  +==================================================+")
    print("")
    
    python_exe = get_python_exe()
    
    # We use python -m mcp_server.server to ensure it is run in this exact python environment
    server_args = ["-m", "mcp_server.server"]
    env_vars = {}
    
    server_entry = {
        "command": python_exe,
        "args": server_args,
        "env": env_vars
    }
    
    zed_entry = {
        "command": {
            "path": python_exe,
            "args": server_args,
            "env": env_vars
        }
    }
    
    print("[1/1] Detecting and registering with coding agents...\n")
    
    results = []
    
    # Paths depend on OS
    system = platform.system()
    home = Path.home()
    
    # Defaults for Windows
    appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    localappdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    
    if system == "Darwin":
        claude_config = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = home / ".config" / "zed" / "settings.json"
    elif system == "Linux":
        # Rough equivalents, Claude desktop unofficial
        claude_config = home / ".config" / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = home / ".config" / "zed" / "settings.json"
    else: # Windows
        claude_config = appdata / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = appdata / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = appdata / "Zed" / "settings.json"

    # Claude Desktop
    if claude_config.parent.exists():
        merge_mcp_config(claude_config, "stageira-skills", server_entry)
        results.append(("Claude Desktop", "[OK] Registered", claude_config))
    else:
        results.append(("Claude Desktop", "[--] Not found", ""))
        
    # Cursor
    if cursor_config.parent.exists() or (home / ".cursor").exists():
        merge_mcp_config(cursor_config, "stageira-skills", server_entry)
        results.append(("Cursor", "[OK] Registered", cursor_config))
    else:
        results.append(("Cursor", "[--] Not found", ""))

    # Windsurf
    if windsurf_config.parent.exists() or (home / ".codeium" / "windsurf").exists():
        merge_mcp_config(windsurf_config, "stageira-skills", server_entry)
        results.append(("Windsurf", "[OK] Registered", windsurf_config))
    else:
        results.append(("Windsurf", "[--] Not found", ""))
        
    # VS Code Cline
    if cline_config.parent.parent.exists():
        merge_mcp_config(cline_config, "stageira-skills", server_entry)
        results.append(("VS Code / Cline", "[OK] Registered", cline_config))
    else:
        results.append(("VS Code / Cline", "[--] Not found", ""))
        
    # Zed
    if zed_config.parent.exists():
        merge_zed_config(zed_config, "stageira-skills", zed_entry)
        results.append(("Zed", "[OK] Registered", zed_config))
    else:
        results.append(("Zed", "[--] Not found", ""))

    # Antigravity (Google Deepmind)
    antigravity_config = home / ".gemini" / "antigravity" / "mcp_config.json"
    if antigravity_config.parent.exists():
        merge_mcp_config(antigravity_config, "stageira-skills", server_entry)
        results.append(("Antigravity (Gemini)", "[OK] Registered", antigravity_config))
    else:
        results.append(("Antigravity (Gemini)", "[--] Not found", ""))

    # Continue.dev
    continue_config = home / ".continue" / "config.json"
    if continue_config.parent.exists():
        try:
            with open(continue_config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        if "mcpServers" not in cfg:
            cfg["mcpServers"] = []
            
        mcp_servers = [s for s in cfg["mcpServers"] if isinstance(s, dict) and s.get("name") != "stageira-skills"]
        mcp_servers.append({
            "name": "stageira-skills",
            "command": python_exe,
            "args": server_args,
            "env": env_vars
        })
        cfg["mcpServers"] = mcp_servers
        
        continue_config.parent.mkdir(parents=True, exist_ok=True)
        with open(continue_config, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            
        results.append(("Continue.dev", "[OK] Registered", continue_config))
    else:
        results.append(("Continue.dev", "[--] Not found", ""))

    print("  ==================================================")
    registered_count = sum(1 for r in results if "[OK]" in r[1])
    print(f"  DONE -- Registered with {registered_count} / {len(results)} agents")
    print("  ==================================================\n")
    
    for agent, status, path in results:
        print(f"  {agent:<20} {status}")
        
    print("\n  NEXT STEP: Restart all open editors/agents to activate.\n")

if __name__ == "__main__":
    main()
