# Cursor MCP Configuration

This directory contains Model Context Protocol (MCP) server configurations for Cursor AI.

## 📁 Files

- **`mcp.json`** - Your personal MCP configuration with tokens (git-ignored ✅)
- **`mcp.local.json.example`** - Example for alternative local override approach
- **`README.md`** - This file

**Note:** The root `.cursor/mcp.json` is git-ignored. The template version is in `project-template/.cursor/mcp.json` and IS committed to Git.

## 📋 Prerequisites

Before setting up MCP servers, ensure you have the following installed:

### Required Software

1. **Node.js and npm** (for `npx` command)
   - Download: https://nodejs.org/
   - Verify installation: `npx --version`
   - Required for: GitHub, Filesystem, and PostgreSQL MCPs

2. **Python 3.8+** (optional - for future Python-based MCPs)
   - Download: https://www.python.org/downloads/
   - Verify installation: `python --version`
   - Note: NOT required for current setup (GitHub, Filesystem, PostgreSQL, Atlassian MCPs)

### Installation Commands

```powershell
# Windows PowerShell

# 1. Check if Node.js/npx is installed
npx --version

# 2. Check if Python is installed
python --version

# 3. All prerequisites installed!
# Note: Official Atlassian MCP Server requires NO additional installs
```

---

## 🚀 Quick Setup

### Current Setup (Direct Token in mcp.json)

This project uses a simplified approach where `mcp.json` contains the actual token:

1. **Copy the template** from `project-template/.cursor/mcp.json` to `.cursor/mcp.json`

2. **Edit `.cursor/mcp.json`** and replace `${GITHUB_TOKEN}` with your actual token:
   ```json
   "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_YOUR_ACTUAL_TOKEN_HERE"
   ```

3. **Restart Cursor**

4. **✅ `.cursor/mcp.json` is git-ignored** - Your token stays safe and won't be committed

### Alternative: Using Environment Variables

If you prefer environment variables:

1. Set environment variables for tokens:
   ```powershell
   # Windows PowerShell
   $env:GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
   ```

2. Keep `${GITHUB_TOKEN}` reference in `mcp.json`

3. Restart Cursor

**Note:** Environment variable expansion may not work consistently with all MCP servers.

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

### Atlassian (Jira + Confluence) MCP
- **Server**: Official Atlassian Remote MCP Server
- **Provider**: Atlassian (Official Product)
- **URL**: https://mcp.atlassian.com/v1/sse
- **License**: Official Atlassian ✅ (No third-party licensing concerns)
- **Transport**: SSE (Server-Sent Events)
- **Prerequisites**: None! Remote server (no local installation)
- **Features**: Jira issues (create/read/update/search), Confluence pages, JQL queries
- **Setup**: Requires `ATLASSIAN_SITE_URL`, `ATLASSIAN_EMAIL`, and `ATLASSIAN_API_TOKEN` env vars
- **Rate Limit**: 500 calls/hour (Free plan)
- **Docs**: https://www.atlassian.com/platform/remote-mcp-server
- **GitHub**: https://github.com/atlassian/atlassian-mcp-server

### Slack MCP (Example Only)
- **Package**: `@modelcontextprotocol/server-slack` (may not exist yet)
- **Features**: Send messages, read channels
- **Setup**: Copy from `mcp.local.json.example` if available

## 🔒 Security

### ✅ DO:
- ✅ Keep tokens in your personal `.cursor/mcp.json` (git-ignored)
- ✅ Verify `.cursor/mcp.json` is listed in `.gitignore`
- ✅ Rotate tokens every 90 days
- ✅ Use development-only tokens (not production)

### ❌ DON'T:
- ❌ Commit `.cursor/mcp.json` with real tokens (it's git-ignored, but double-check!)
- ❌ Share tokens in team chat or documentation
- ❌ Use production tokens for development
- ❌ Copy tokens to other non-ignored files

### 🛡️ Protection Status:
- ✅ **`.cursor/mcp.json`** - Git-ignored (your personal config with tokens)
- ✅ **`.cursor/mcp.local.json`** - Git-ignored (if you use the alternative approach)
- ✅ **`project-template/.cursor/mcp.json`** - Committed (template without tokens)

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

### Test Atlassian MCP
```
Ask Cursor: "List all issues in the [YOUR-PROJECT] project"
Expected: Shows Jira issues without browser
```

## 🐛 Troubleshooting

### MCP Server Not Loading?

1. **Check prerequisites are installed:**
   ```powershell
   npx --version        # Should show version number
   python --version     # Should show Python 3.8+
   python -m uv --version  # Should show uv version
   ```

2. **Verify JSON syntax is valid** (no trailing commas)

3. **Restart Cursor after changes**

4. **Check Cursor's MCP Logs:**
   - Open Output panel: `Ctrl+Shift+U` (Windows) or `Cmd+Shift+U` (Mac)
   - Select "MCP Logs" from dropdown
   - Look for specific error messages

5. **Common Issues:**
   - "command not found: npx" → Install Node.js
   - "No tools prompts or resources" → Check MCP logs for specific error
   - Connection failed → Check internet connection (Atlassian MCP requires internet)
   - PATH not updated → Restart terminal/Cursor after installing tools

**Token not working?**
1. Verify environment variable is set: `echo $env:GITHUB_TOKEN`
2. Check token hasn't expired
3. Verify token has correct permissions
4. Try regenerating the token

**Cannot find MCP package?**
1. Some MCPs may not exist yet
2. Check official list: https://github.com/modelcontextprotocol/servers
3. Remove or comment out non-existent servers
4. For remote servers (like Atlassian), verify the URL is correct

**Atlassian MCP Specific Issues:**
1. **"Cannot connect to Atlassian MCP"**
   - Solution: Verify your Atlassian API token is valid
   - Check your site URL is correct (e.g., `https://yoursite.atlassian.net`)
   - Ensure you have internet connection (remote server required)
   
2. **"No tools prompts or resources"**
   - Check MCP Logs in Cursor Output panel (`Ctrl+Shift+U`)
   - Verify all three env vars are set: `ATLASSIAN_SITE_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`
   - Restart Cursor completely
   
3. **"Rate limit exceeded"**
   - Free plan allows 500 calls/hour
   - Wait for the hour to reset, or upgrade to Standard (1000 calls/hour)

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

