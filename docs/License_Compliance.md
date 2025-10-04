# License Compliance Tracking

**Project**: ComplianceFlow (Proprietary Software)  
**Last Updated**: October 4, 2025

---

## 🔒 License Policy

ComplianceFlow is **proprietary software**. All third-party dependencies must use licenses compatible with proprietary/commercial software.

### ✅ Acceptable Licenses
- MIT License
- Apache License 2.0
- BSD Licenses (2-Clause, 3-Clause)
- ISC License
- Python Software Foundation License
- Unlicense / Public Domain

### ❌ Prohibited Licenses
- GNU General Public License (GPL) v2 or v3
- GNU Lesser General Public License (LGPL)
- GNU Affero General Public License (AGPL)
- Any copyleft licenses requiring derivative works to be open-sourced

---

## 📦 Third-Party Dependencies

### MCP (Model Context Protocol) Servers

#### 1. GitHub MCP Server
- **Package**: `@modelcontextprotocol/server-github`
- **License**: MIT ✅
- **Repository**: https://github.com/modelcontextprotocol/servers
- **Purpose**: Create/manage GitHub issues, PRs, comments
- **Verified**: October 4, 2025
- **Status**: ✅ Compliant

#### 2. Filesystem MCP Server
- **Package**: `@modelcontextprotocol/server-filesystem`
- **License**: MIT ✅
- **Repository**: https://github.com/modelcontextprotocol/servers
- **Purpose**: File system operations for AI context
- **Verified**: October 4, 2025
- **Status**: ✅ Compliant

#### 3. PostgreSQL MCP Server
- **Package**: `@modelcontextprotocol/server-postgres`
- **License**: MIT ✅
- **Repository**: https://github.com/modelcontextprotocol/servers
- **Purpose**: Database query capabilities for AI
- **Verified**: October 4, 2025
- **Status**: ✅ Compliant

#### 4. Atlassian Remote MCP Server
- **Provider**: Atlassian (Official)
- **Type**: Remote SaaS Server (not a package)
- **License**: Official Atlassian Product ✅
- **Server URL**: https://mcp.atlassian.com/v1/sse
- **Repository**: https://github.com/atlassian/atlassian-mcp-server
- **Documentation**: https://www.atlassian.com/platform/remote-mcp-server
- **Dependencies**: None (remote server)
- **Purpose**: Integrate Jira and Confluence with AI tools
- **Verified**: October 4, 2025
- **Status**: ✅ Compliant (Official Atlassian product, no licensing concerns)

---

## 🔍 Verification Process

For each third-party dependency:

1. **Check License**: Look up the library's license explicitly
2. **Verify Compatibility**: Ensure it's compatible with proprietary software
3. **Document**: Record license type and verification date
4. **Track**: Maintain this document with all dependencies

### Verification Commands

```bash
# For npm packages
npm view <package-name> license

# For Python packages
pip show <package-name> | grep License

# For GitHub repositories
curl https://api.github.com/repos/<owner>/<repo>/license
```

---

## 📊 License Summary

| Package | License | Status | Verified |
|---------|---------|--------|----------|
| `@modelcontextprotocol/server-github` | MIT | ✅ Compliant | 2025-10-04 |
| `@modelcontextprotocol/server-filesystem` | MIT | ✅ Compliant | 2025-10-04 |
| `@modelcontextprotocol/server-postgres` | MIT | ✅ Compliant | 2025-10-04 |
| Atlassian Remote MCP Server | Official Product | ✅ Compliant | 2025-10-04 |

**Total Packages**: 4  
**Compliant**: 4 (100%)  
**Non-Compliant**: 0

---

## 🔄 Ongoing Compliance

### Regular Reviews
- Review licenses quarterly
- Check for dependency updates that might change licenses
- Document any new dependencies before use

### Adding New Dependencies
Before adding any new third-party library:

1. Research the license
2. Verify it's not GPL/LGPL/AGPL
3. Add to this document
4. Get approval if uncertain

### Contact
For license questions or concerns, consult with legal counsel or project maintainer.

---

## 📚 Resources

- [Choose a License](https://choosealicense.com/)
- [SPDX License List](https://spdx.org/licenses/)
- [TLDRLegal - Software Licenses Explained](https://www.tldrlegal.com/)
- [GitHub License API](https://docs.github.com/en/rest/licenses)

---

**Note**: This document must be kept up-to-date as dependencies are added or changed. License compliance is mandatory for protecting intellectual property rights.

