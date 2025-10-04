# Cursor MCP Configuration

This directory contains Model Context Protocol (MCP) server configurations for Cursor AI.

## 📁 Files

- **`mcp.json`** - Main MCP configuration (safe to commit to Git)
- **`mcp.local.json.example`** - Example for local overrides with tokens
- **`mcp.local.json`** - Your local overrides (DO NOT COMMIT - git-ignored)
- **`README.md`** - This file

## 🚀 Quick Setup

### Option 1: Using Environment Variables (Recommended)

1. Set environment variables for tokens:
   ```powershell
   # Windows PowerShell
   $env:GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
   ```
   
   ```bash
   # Mac/Linux
   export GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
   ```

2. The `mcp.json` file will automatically use `${GITHUB_TOKEN}` from your environment

3. Restart Cursor

### Option 2: Using Local Override File

1. Copy the example file:
   ```powershell
   Copy-Item .cursor\mcp.local.json.example .cursor\mcp.local.json
   ```

2. Edit `mcp.local.json` and add your actual tokens

3. Cursor will merge both `mcp.json` and `mcp.local.json`

4. Restart Cursor

## 🔌 Configured MCP Servers

### GitHub MCP (Enabled)
- **Package**: `@modelcontextprotocol/server-github`
- **License**: MIT ✅
- **Features**: Create/manage issues, PRs, comments, view commits
- **Setup**: Requires `GITHUB_TOKEN` environment variable
- **Docs**: https://github.com/modelcontextprotocol/servers

### Filesystem MCP (Enabled)
- **Package**: `@modelcontextprotocol/server-filesystem`
- **License**: MIT ✅
- **Features**: Read/write files, search project
- **Setup**: Pre-configured for this project
- **Path**: `c:\dev\complianceflow`

### PostgreSQL MCP (Enabled)
- **Package**: `@modelcontextprotocol/server-postgres`
- **License**: MIT ✅
- **Features**: Query databases, inspect schemas
- **Setup**: Pre-configured for local development
- **Connection**: `postgresql://localhost/complianceflow`

### Jira MCP (Example Only)
- **Package**: `@modelcontextprotocol/server-jira` (may not exist yet)
- **Features**: Create/manage stories, epics, tasks
- **Setup**: Copy from `mcp.local.json.example` if available

### Slack MCP (Example Only)
- **Package**: `@modelcontextprotocol/server-slack` (may not exist yet)
- **Features**: Send messages, read channels
- **Setup**: Copy from `mcp.local.json.example` if available

## 🔒 Security

### ✅ DO:
- ✅ Commit `mcp.json` with environment variable references
- ✅ Use environment variables for tokens
- ✅ Keep tokens in `mcp.local.json` (git-ignored)
- ✅ Rotate tokens every 90 days

### ❌ DON'T:
- ❌ Commit `mcp.local.json` (contains real tokens)
- ❌ Hard-code tokens in `mcp.json`
- ❌ Share tokens in team chat or documentation
- ❌ Use production tokens for development

## 🧪 Testing MCP Integration

After setup, test each MCP server:

### Test GitHub MCP
```
Ask Cursor: "List all open issues in complianceflow"
Expected: Shows issues without browser
```

### Test Filesystem MCP
```
Ask Cursor: "Find all Python files in the services directory"
Expected: Lists Python files
```

### Test PostgreSQL MCP
```
Ask Cursor: "Show me the schema for the users table"
Expected: Displays table structure
```

## 🐛 Troubleshooting

**MCP server not loading?**
1. Check if `npx` is available: `npx --version`
2. Verify JSON syntax is valid (no trailing commas)
3. Restart Cursor after changes
4. Check Cursor's output panel for errors

**Token not working?**
1. Verify environment variable is set: `echo $env:GITHUB_TOKEN`
2. Check token hasn't expired
3. Verify token has correct permissions
4. Try regenerating the token

**Cannot find MCP package?**
1. Some MCPs may not exist yet (especially Jira, Slack)
2. Check official list: https://github.com/modelcontextprotocol/servers
3. Remove or comment out non-existent servers

## 📚 Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
- **Cursor AI Docs**: https://docs.cursor.com/
- **Project MCP Guide**: `docs/MCP_Setup_Guide.md`

## 📝 Adding New MCP Servers

To add a new MCP server:

1. Find the MCP package (e.g., on npm or GitHub)
2. Check the license (must be MIT, Apache 2.0, BSD, etc. - NO GPL!)
3. Add to `mcp.json` if no secrets required
4. Add to `mcp.local.json.example` if secrets required
5. Document in this README
6. Restart Cursor

---

**Last Updated**: October 4, 2025  
**Maintained By**: ComplianceFlow Development Team

