# MCP Setup Guide for ComplianceFlow

This guide documents the setup of Model Context Protocol (MCP) integrations for Cursor AI with GitHub and Jira.

## 🎯 Purpose

MCPs allow Cursor AI to directly interact with external tools:
- **GitHub MCP**: Create/manage issues, PRs, comments
- **Jira MCP**: Create/manage stories, tasks, epics

## 📋 Prerequisites

- Cursor AI installed
- Access to GitHub repository: https://github.com/tensargh/complianceflow
- Jira Free account (to be created)

## 🚀 Quick Start

**TL;DR - Where do MCP settings go?**

✅ **User-level (personal):** `%APPDATA%\Cursor\User\globalStorage\mcp.json` (Windows)  
✅ **Project-level (team):** `.cursor/mcp.json` in project root  
✅ **File format:** JSON with `"mcpServers"` or `"mcp.servers"` key

**✨ This project includes a pre-configured `.cursor/mcp.json` template!**

- Ready for GitHub, filesystem, and PostgreSQL MCPs
- Uses environment variables for secure token management
- See `.cursor/README.md` for setup instructions

**Note:** This guide was updated to reflect the correct MCP configuration locations. Previous versions incorrectly suggested using general user settings.

---

## 🎁 Using the Project Template (Easiest Method)

This project includes a pre-configured MCP setup in the `.cursor/` directory!

### Quick Setup Steps:

1. **Set your GitHub token as environment variable:**
   ```powershell
   # Windows PowerShell (add to your PowerShell profile for persistence)
   $env:GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
   ```
   
   To make it permanent, add to your profile:
   ```powershell
   notepad $PROFILE
   # Add: $env:GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
   ```

2. **Restart Cursor** - The `.cursor/mcp.json` file will be automatically detected

3. **Test it:** Ask Cursor to list GitHub issues

4. **(Optional) Add Jira/Slack:**
   - Copy `.cursor/mcp.local.json.example` to `.cursor/mcp.local.json`
   - Add your tokens (file is git-ignored)
   - Restart Cursor

### What's Included:

✅ **GitHub MCP** - Issues, PRs, commits (MIT License ✅)  
✅ **Filesystem MCP** - Project file operations (MIT License ✅)  
✅ **PostgreSQL MCP** - Database queries (MIT License ✅)  
📋 **Jira MCP** - Example configuration (if package exists)  
📋 **Slack MCP** - Example configuration (if package exists)

See `.cursor/README.md` for detailed documentation!

---

## 🐙 GitHub MCP Setup (Manual Method)

If you prefer to set up manually or use user-level configuration:

### Step 1: Create GitHub Personal Access Token (Fine-Grained)

1. Navigate to: https://github.com/settings/tokens?type=beta
2. Click **"Generate new token"**
3. Configure token:
   - **Token name**: `Cursor MCP - ComplianceFlow`
   - **Description**: `MCP integration for AI-assisted development`
   - **Expiration**: 90 days (or custom)
   - **Repository access**: "Only select repositories"
     - Select: `tensargh/complianceflow`
   - **Repository permissions**:
     - Contents: Read and write
     - Issues: Read and write
     - Pull requests: Read and write
     - Metadata: Read-only (automatic)
4. Click **"Generate token"**
5. **IMPORTANT**: Copy the token immediately (starts with `github_pat_...`)
6. Store securely (you won't see it again!)

### Step 2: Configure Cursor MCP Settings

MCP settings in Cursor are configured in a dedicated configuration file.

**Location Options:**

**Option A: User-level (recommended for personal use)**
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp.json`

**Option B: Project-level (recommended for team projects)**
- Create `.cursor/mcp.json` in your project root
- This can be committed to Git (without tokens - use environment variables)

**Steps to Configure:**

1. Create the MCP configuration file in your chosen location
2. Add the following configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

3. Replace `github_pat_YOUR_TOKEN_HERE` with your actual token
4. Save the file
5. Restart Cursor

**Note:** Some versions of Cursor may use `"mcp.servers"` instead of `"mcpServers"`. If one doesn't work, try the other.

### Step 3: Test GitHub MCP

Test by asking Cursor to perform GitHub operations:

**Test Commands:**
1. "Create a GitHub issue titled 'Test MCP Integration' with label 'test'"
2. "List all open issues in the complianceflow repository"
3. "Show me recent commits on the master branch"

**Expected Behavior:**
- Cursor should be able to create issues without opening a browser
- Issues should appear in: https://github.com/tensargh/complianceflow/issues

---

## 📊 Jira MCP Setup

### Step 1: Create Jira Free Account

1. Go to: https://www.atlassian.com/software/jira/free
2. Click **"Get it free"**
3. Sign up with email
4. Create site name: `complianceflow` (or your preferred name)
   - Your Jira URL will be: `https://complianceflow.atlassian.net`
5. Select template: **"Scrum"** (recommended) or **"Kanban"**
6. Create project:
   - Name: `ComplianceFlow`
   - Key: `CF` (auto-generated, used as prefix for issues)
   - Type: Software development

### Step 2: Create Jira API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Label: `Cursor MCP - ComplianceFlow`
4. Click **"Create"**
5. Copy the token immediately (store securely)

### Step 3: Configure Jira MCP in Cursor

**Option A: Official Jira MCP (if available)**

Check: https://github.com/modelcontextprotocol/servers

**Option B: Community Jira MCP**

Research community options:
- Search GitHub for: "mcp server jira"
- Check MCP Registry (if available)
- Community implementations may vary

**Example Configuration** (add to the same `mcp.json` file):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_YOUR_TOKEN_HERE"
      }
    },
    "jira": {
      "command": "npx",
      "args": [
        "-y",
        "@some-org/mcp-server-jira"
      ],
      "env": {
        "JIRA_URL": "https://complianceflow.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Note:** Replace `@some-org/mcp-server-jira` with the actual Jira MCP package when found.

### Step 4: Test Jira MCP

**Test Commands:**
1. "Create a Jira story in CF project: 'Setup User Service'"
2. "List all epics in ComplianceFlow project"
3. "Show me open stories assigned to me"

---

## 🏗️ Initial Jira Structure

Once Jira is configured, create initial epics:

### Epics to Create

1. **Infrastructure Setup** (CF-1)
   - Description: Azure infrastructure, Terraform, networking
   
2. **User Service** (CF-2)
   - Description: Authentication, SSO, user management
   
3. **Declaration Service** (CF-3)
   - Description: Declaration lifecycle, submissions
   
4. **Form Service** (CF-4)
   - Description: Dynamic form builder
   
5. **Rule Engine Service** (CF-5)
   - Description: Automated decision making
   
6. **Review Service** (CF-6)
   - Description: Human review workflow
   
7. **Case Service** (CF-7)
   - Description: Investigation management
   
8. **Notification Service** (CF-8)
   - Description: Email and notifications
   
9. **Analytics Service** (CF-9)
   - Description: Dashboards and reporting
   
10. **Frontend Application** (CF-10)
    - Description: React web application

---

## 📁 Project-Level MCP Configuration

If you want to use `.cursor/mcp.json` in your project root (for team collaboration):

### Safe Configuration for Git

**Option 1: Use Environment Variables**

Create `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Then set environment variable:
- Windows: `$env:GITHUB_TOKEN="github_pat_YOUR_TOKEN"`
- Mac/Linux: `export GITHUB_TOKEN="github_pat_YOUR_TOKEN"`

**Option 2: Separate Token File**

1. Create `.cursor/mcp.json` (commit to Git)
2. Create `.cursor/mcp.local.json` (add to `.gitignore`)
3. Put tokens in the `.local` file
4. Cursor should merge both files

**Important:** Always add token files to `.gitignore`:
```
.cursor/mcp.local.json
.cursor/*.token
```

---

## 🔒 Security Best Practices

### Token Management

1. **Never commit tokens to Git**
   - Tokens should only be in local Cursor settings
   - Add to `.gitignore`: `settings.json`, `*.token`

2. **Use fine-grained tokens**
   - GitHub: Fine-grained tokens with minimal scope
   - Jira: API tokens, not passwords

3. **Regular rotation**
   - Rotate tokens every 90 days
   - Update Cursor settings when rotated

4. **Revoke unused tokens**
   - Remove old tokens from GitHub/Jira settings
   - Keep only active tokens

### Environment Separation

- **Development tokens**: Use for local Cursor MCP
- **CI/CD tokens**: Separate tokens for GitHub Actions (stored in GitHub Secrets)
- **Never share tokens** between environments

---

## 🧪 Testing the Integration

### GitHub MCP Tests

```
Test 1: Create Issue
Ask Cursor: "Create a GitHub issue titled 'Test Issue' in complianceflow"
Verify: Check https://github.com/tensargh/complianceflow/issues

Test 2: List Issues
Ask Cursor: "Show me all open issues"
Verify: Cursor lists issues without browser

Test 3: Create PR
Ask Cursor: "Show me recent pull requests"
Verify: Cursor can access PR data
```

### Jira MCP Tests

```
Test 1: Create Story
Ask Cursor: "Create a Jira story: 'Test MCP Integration'"
Verify: Story appears in Jira board

Test 2: List Epics
Ask Cursor: "List all epics in ComplianceFlow project"
Verify: Cursor retrieves epic list

Test 3: Update Story
Ask Cursor: "Move story CF-XX to In Progress"
Verify: Story status changes in Jira
```

---

## 📊 AI-Assisted Workflow

Once MCPs are configured, your workflow becomes:

### From PRD to Implementation

1. **In Cursor**: "Read the User Service PRD and create Jira stories for each feature"
   - AI creates 15+ stories automatically
   
2. **In Cursor**: "Show me the next story in the backlog"
   - AI retrieves story from Jira
   
3. **Develop**: Implement the story with AI assistance
   
4. **In Cursor**: "Create a PR for this story and link to CF-XX"
   - AI creates PR with proper Jira reference
   
5. **In Cursor**: "Mark story CF-XX as done"
   - AI updates Jira status

### Benefits

- ✅ No context switching between Cursor, GitHub, and Jira
- ✅ AI understands full context (code + planning)
- ✅ Automatic linking between code and stories
- ✅ Faster velocity (less manual clicking)
- ✅ Better documentation (AI captures decisions)

---

## 🎓 Consulting Portfolio Content

Document your MCP setup experience:

### Blog Post Ideas

1. **"Setting Up Cursor AI with GitHub MCP"**
   - Step-by-step guide
   - Screenshots of configuration
   - Benefits and time savings
   
2. **"AI-Assisted Project Management with Jira MCP"**
   - Creating stories from PRDs
   - Workflow automation
   - Velocity improvements

### Video Demonstrations

1. **"From PRD to Jira Stories in 5 Minutes"** (2-3 min)
   - Show AI reading PRD
   - Show AI creating stories
   - Show stories in Jira
   
2. **"Complete Feature Development Without Leaving Cursor"** (5 min)
   - Get story from Jira
   - Write code with AI
   - Create PR via MCP
   - Update story status

---

## 🐛 Troubleshooting

### MCP Configuration Issues

**Problem**: "MCP server not loading" or "No MCP tools available"
- **Solution**: Verify `mcp.json` is in the correct location
- **Solution**: Check file uses `"mcpServers"` (try `"mcp.servers"` if that doesn't work)
- **Solution**: Ensure JSON is valid (no trailing commas, proper quotes)
- **Solution**: Restart Cursor after making changes

**Problem**: "Cannot find mcp.json file"
- **Solution (Windows)**: Type `%APPDATA%\Cursor\User\globalStorage\` in File Explorer
- **Solution (Mac)**: Press `Cmd+Shift+G` and go to `~/Library/Application Support/Cursor/User/globalStorage/`
- **Solution**: Create the directory if it doesn't exist
- **Solution**: Or use project-level: create `.cursor/mcp.json` in project root

### GitHub MCP Issues

**Problem**: "Cannot connect to GitHub MCP"
- **Solution**: Check token hasn't expired
- **Solution**: Verify token has correct permissions
- **Solution**: Check token is correctly formatted in `env.GITHUB_PERSONAL_ACCESS_TOKEN`
- **Solution**: Restart Cursor

**Problem**: "Permission denied when creating issues"
- **Solution**: Token needs "Issues: Read and write" permission
- **Solution**: Regenerate token with correct scope

### Jira MCP Issues

**Problem**: "Cannot find Jira MCP package"
- **Solution**: Check if official MCP exists
- **Solution**: Research community implementations
- **Solution**: May need to build custom MCP (consulting opportunity!)

**Problem**: "Authentication failed"
- **Solution**: Verify API token is valid
- **Solution**: Check email address is correct
- **Solution**: Verify Jira URL format

---

## 📝 Next Steps

After MCP setup:

1. ✅ Test both GitHub and Jira integrations
2. ✅ Create initial epics in Jira
3. ✅ Generate stories from PRDs using AI
4. ✅ Start development with MCP-assisted workflow
5. ✅ Document time savings for consulting portfolio

---

## 📚 Resources

- **GitHub MCP**: https://github.com/modelcontextprotocol/servers
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Cursor AI Docs**: https://docs.cursor.com/
- **Jira API**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **GitHub API**: https://docs.github.com/en/rest

---

**Last Updated**: October 4, 2025
**Status**: Setup In Progress
**Repository**: https://github.com/tensargh/complianceflow/


