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

## 1Password SSH Agent Configuration

### Problem Context

When using 1Password SSH agent for managing SSH key passphrases, the SSH keys must be properly configured in both 1Password and the SSH agent config file. If the vault names don't match exactly, SSH will fall back to requesting passphrases in the terminal instead of using 1Password.

### Prerequisites

- 1Password SSH agent must be enabled in 1Password app (Settings → Developer → Use the SSH agent)
- SSH_AUTH_SOCK environment variable must point to 1Password SSH agent
- SSH keys must be stored in 1Password vaults

### SSH Agent Configuration Steps

1. **Verify 1Password SSH Agent is Active**
   ```bash
   echo $SSH_AUTH_SOCK
   # Should output: /Users/username/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock
   ```

2. **Check Current SSH Keys Loaded**
   ```bash
   ssh-add -l
   # Look for the Tjark SSH key with fingerprint: SHA256:VpE7YgCEiFMNh0+vcrD7RvcMlxM47TCtRSFT+BkcW18
   # If missing, proceed to step 3
   ```

3. **Add Tjark Vault to 1Password SSH Agent Config**

   Edit `~/.config/1Password/ssh/agent.toml` and add the following entry:
   ```toml
   [[ssh-keys]]
   vault = "Tjark van Guhlo"  # Note: exact vault name with spaces is critical
   ```

   **Full example config:**
   ```toml
   [[ssh-keys]]
   vault = "Private"

   [[ssh-keys]]
   vault = "Tjark van Guhlo"
   ```

4. **Verify the Tjark SSH Key is Now Loaded**
   ```bash
   ssh-add -l | grep -i tjark
   # Should show: 256 SHA256:VpE7YgCEiFMNh0+vcrD7RvcMlxM47TCtRSFT+BkcW18 tjark SSH (ED25519)
   ```

5. **Test SSH Connection to GitHub**
   ```bash
   ssh -T git@github-tjark
   # Expected output: "Hi TjarkVanGuhlo! You've successfully authenticated..."
   # Should NOT prompt for passphrase - 1Password handles it automatically
   ```

### Common Issues

**SSH asks for passphrase in terminal instead of using 1Password:**
- Check that vault name in `agent.toml` matches exactly (including spaces)
- Verify the SSH key exists and is active in the specified 1Password vault
- Ensure SSH_AUTH_SOCK points to 1Password agent socket
- Kill any competing system SSH agents: `ps aux | grep ssh-agent`

**SSH key not showing in `ssh-add -l`:**
- Vault name mismatch in `agent.toml` (most common issue)
- SSH key may be archived or deleted in 1Password
- 1Password may need to be restarted after config changes

### Testing 1Password SSH Integration

```bash
# Test SSH connection - should authenticate via 1Password, not terminal
ssh -T git@github-tjark
# Expected output: "Hi TjarkVanGuhlo! You've successfully authenticated..."
```

## Security Considerations

- Never skip SSH key configuration unless the key already exists
- Always verify the active account before performing sensitive operations
- Use proper SSH host aliases to separate different GitHub accounts
- Ensure 1Password SSH agent config file uses exact vault names (case-sensitive, including spaces)
