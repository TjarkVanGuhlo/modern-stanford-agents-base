# Tjark GitHub CLI Setup

This document outlines the correct steps to configure GitHub CLI (`gh`) with the TjarkVanGuhlo account for this repository.

## Problem Context

This repository is owned by the `TjarkVanGuhlo` GitHub account, but the local machine may have multiple GitHub accounts configured with `gh CLI`. The default active account might be different (e.g., `Pattkopp`), which causes authentication issues when trying to create releases or perform other GitHub operations.

## Solution: Multi-Account GitHub CLI Setup

### Prerequisites
- SSH key for TjarkVanGuhlo account must already be configured in GitHub
- SSH config should already be set up for the `github-tjark` host alias

**Example SSH Config (`~/.ssh/config`):**
```
Host github-tjark
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_tjark
```

### Steps to Configure TjarkVanGuhlo Account

1. **Add TjarkVanGuhlo Account to GitHub CLI**
   ```bash
   gh auth login --hostname github.com --git-protocol ssh --web
   ```
   - When prompted about SSH key upload, select **"Skip"** (key already exists)
   - Complete the web authentication for the TjarkVanGuhlo account

2. **Verify Authentication Status**
   ```bash
   gh auth status
   ```
   - Should show TjarkVanGuhlo as the active account
   - Should show both Pattkopp and TjarkVanGuhlo accounts if multiple exist

3. **Add Workflow Scope (Required for Releases)**
   ```bash
   gh auth refresh -h github.com -s workflow
   ```
   - Complete the web authentication to add workflow permissions
   - This scope is required for creating GitHub releases

4. **Verify Final Setup**
   ```bash
   gh auth status
   ```
   - Should show TjarkVanGuhlo as active account
   - Token scopes should include: `gist`, `read:org`, `repo`, `workflow`

### Testing the Setup

Create a test release to verify everything works:
```bash
gh release create v0.1.1 --title "Test Release" --notes "Test release notes"
```

### Account Switching (If Needed)

If you need to switch between accounts for different repositories:
```bash
gh auth switch --hostname github.com
```

### Troubleshooting

**Error: "workflow scope may be required"**
- Run: `gh auth refresh -h github.com -s workflow`
- Complete web authentication

**Error: Wrong account credentials**
- Check active account: `gh auth status`
- Switch account if needed: `gh auth switch --hostname github.com`

**Error: Authentication failed**
- Ensure SSH key is properly configured in GitHub
- Verify SSH connection: `ssh -T git@github-tjark`

## Important Notes

- SSH keys should never be uploaded if they already exist in GitHub
- Always use the web authentication flow for security
- The workflow scope is specifically required for release operations
- Each repository can have different GitHub accounts associated with it

## Security Considerations

- Never skip SSH key configuration unless the key already exists
- Always verify the active account before performing sensitive operations
- Use proper SSH host aliases to separate different GitHub accounts