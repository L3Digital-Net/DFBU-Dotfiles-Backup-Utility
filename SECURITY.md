# Security Policy

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | :white_check_mark: |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

**Recommendation**: Use the latest stable release for optimal security and feature
support.

## Security Considerations

### Data Handling

DFBU processes and stores configuration files that may contain sensitive information:

- Configuration paths and system structure
- Application settings and preferences
- File metadata and timestamps
- Backup history and statistics

**User Responsibilities**:

- Do not backup files containing credentials, API keys, or passwords
- Use `.dfbuignore` to exclude sensitive directories (e.g., `.ssh/`, `.gnupg/`)
- Secure backup destinations with appropriate filesystem permissions
- Encrypt backup storage when using cloud or network destinations

### Backup Security

**Best Practices**:

- Set restrictive permissions on backup directories (`chmod 700`)
- Store pre-restore safety backups in user-writable locations only
- Verify backup integrity using hash verification feature
- Maintain backup copies in multiple secure locations

### Configuration Security

Configuration files are stored in:

- **AppImage**: `~/.config/dfbu/` (user-readable only by default)
- **Source**: `DFBU/data/` or `~/.config/dfbu/`

**Recommendations**:

- Protect configuration directory permissions (`chmod 700 ~/.config/dfbu/`)
- Review `dotfiles.yaml` before sharing to remove sensitive paths
- Validate configuration files after manual edits
- Export configurations to secure locations only

## Reporting a Vulnerability

**If you discover a security vulnerability in DFBU, please report it responsibly.**

### Reporting Process

1. **Do Not** create a public GitHub issue for security vulnerabilities
2. **Email** security concerns to: dev@l3digital.net
3. **Include** in your report:
   - Detailed description of the vulnerability
   - Steps to reproduce the issue
   - Affected versions (if known)
   - Potential impact assessment
   - Proof of concept (if applicable)

### Response Timeline

| Stage                        | Timeline                                  |
| ---------------------------- | ----------------------------------------- |
| **Initial Response**         | Within 48 hours                           |
| **Vulnerability Assessment** | Within 7 days                             |
| **Patch Development**        | Depends on severity (critical: 7-14 days) |
| **Public Disclosure**        | After patch release + 14 days             |

### Severity Classification

**Critical**: Remote code execution, privilege escalation, data corruption

- Response: Immediate patch, security advisory

**High**: Local file access vulnerabilities, data exposure

- Response: Priority patch within 2 weeks

**Medium**: Information disclosure, denial of service

- Response: Patch in next minor release

**Low**: Configuration issues, edge case vulnerabilities

- Response: Addressed in routine updates

## Security Updates

### Notification Channels

Security updates are announced via:

- [GitHub Security Advisories](https://github.com/L3DigitalNet/DFBU-Dotfiles-Backup-Utility/security/advisories)
- [GitHub Releases](https://github.com/L3DigitalNet/DFBU-Dotfiles-Backup-Utility/releases)
  (security release notes)
- Repository CHANGELOG.md (security section)

### Update Recommendations

**Critical/High Severity**: Update immediately **Medium Severity**: Update within 30
days **Low Severity**: Update at next convenient maintenance window

### Applying Updates

**AppImage**:

```bash
# Download latest release
wget https://github.com/L3DigitalNet/DFBU-Dotfiles-Backup-Utility/releases/latest/download/DFBU-x86_64.AppImage
chmod +x DFBU-x86_64.AppImage
```

**Source Installation**:

```bash
git pull origin main
uv sync --all-extras --dev
```

## Known Security Limitations

### File System Access

DFBU requires read access to source files and write access to backup destinations:

- **By Design**: File operations use standard Python filesystem APIs
- **Limitation**: Cannot backup files without read permissions
- **Mitigation**: Run with appropriate user permissions, avoid sudo unless necessary

### Backup Integrity

Archive backups use gzip compression without built-in encryption:

- **By Design**: Focus on compression, not encryption
- **Limitation**: Backups stored in plaintext (compressed)
- **Mitigation**: Use filesystem-level encryption (LUKS, eCryptfs) or encrypt backup
  destinations

### Configuration Storage

Configuration files stored in YAML format without encryption:

- **By Design**: Human-readable configuration
- **Limitation**: Paths and settings visible in plaintext
- **Mitigation**: Secure configuration directory permissions

## Security Contact

**Security Issues**: dev@l3digital.net **General Issues**:
[GitHub Issues](https://github.com/L3DigitalNet/DFBU-Dotfiles-Backup-Utility/issues)
**Discussions**:
[GitHub Discussions](https://github.com/L3DigitalNet/DFBU-Dotfiles-Backup-Utility/discussions)

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who
report valid vulnerabilities:

- Recognition in CHANGELOG.md security section
- Credit in GitHub Security Advisory (if desired)
- Mention in release notes for security updates

Thank you for helping keep DFBU secure.
