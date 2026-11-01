# Security Policy

The Trappy Language Project takes security seriously. We welcome security researchers, contributors, and users to report any security vulnerabilities responsibly.

---

## Supported Versions

Only the latest active release branch receives active security patches.

| Version | Supported          |
| ------- | ------------------ |
| 1.5.x   | Yes                |
| 1.15.x  | Yes                |
| < 1.5   | No                 |

---

## Reporting a Vulnerability

If you discover a security vulnerability or security bug in Trappy, please do **NOT** open a public GitHub issue.

Please report vulnerabilities through **GitHub Private Vulnerability Reporting**:
1. Navigate to the repository at https://github.com/ashoccompany/Trappy
2. Click the **Security** tab.
3. Click **Report a vulnerability** to submit a private advisory.

Alternatively, contact the core team via private message on the official Discord:
- Official Discord: https://discord.gg/3chDfAPE9H

### What to Include in Your Report
- A description of the vulnerability and its potential impact.
- Steps to reproduce or a minimal proof of concept code (`.trappy` script or Python traceback).
- The operating system and Trappy version tested.

---

## Vulnerability Handling Process

1. **Acknowledgment:** We will acknowledge receipt of your vulnerability report within 48 hours.
2. **Investigation & Triage:** The issue will be triaged and investigated in a private branch.
3. **Patch & Advisory:** Once verified, a fix will be implemented, regression-tested against the automated test suite, and published in the next patch release along with credit to the reporter (unless anonymity is requested).

---

## Security Best Practices for Trappy Users

- **Restricting Untrusted Code:** When running untrusted scripts or community packages, use `--safe` mode (`python trappy.py --safe script.trappy` or set `TRAPPY_SAFE_MODE=1`). Safe mode disables arbitrary shell execution (`sys_exec`) and direct low-level memory writes (`mem_write`).
- **Network Boundaries:** Trappy servers (`srv_listen`) bind to loopback (`127.0.0.1`) by default. To expose services on external interfaces, explicitly set the `TRAPPY_HOST` environment variable.
- **File Sandbox:** File operations (`file_write`, `file_read`, etc.) are confined to the working directory using path traversal guards. Do not run untrusted scripts in sensitive system root directories.
