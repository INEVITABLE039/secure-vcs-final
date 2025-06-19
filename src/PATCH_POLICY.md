# Patch Management Policy

This document outlines the simulated patch management strategy for the Secure Virtual Collaboration Software project.

## ⏱️ Patch Response Time

- Critical security patches must be applied within **24–48 hours** of discovery.
- High-severity vulnerabilities should be patched within **72 hours**.
- Medium/low vulnerabilities may be scheduled for next sprint or monthly patch cycle.

## 🔍 Regular Vulnerability Review

- Trivy scans are performed after every image build (Docker).
- Checkov scans are run on Infrastructure-as-Code (IaC) for misconfigurations.
- Reports from Bandit (static code analysis) are reviewed weekly.

## 🛠️ Automation & CI/CD Integration

- GitHub Actions pipeline blocks merge if:
  - Bandit detects critical Python vulnerabilities
  - Trivy/Checkov finds high-severity issues
- Pipeline requires a successful security test before deployment

## 📋 Patch Log (Example Entry)

| Date       | Tool    | Severity | Component     | Action Taken             |
|------------|---------|----------|---------------|--------------------------|
| 2025-06-15 | Trivy   | High     | openssl       | Image updated & pushed   |
| 2025-06-16 | Bandit  | Medium   | app.py        | Rewrote unsafe function  |

## 🔁 Review Cycle

- All patch activities are reviewed monthly.
- A patch status summary is submitted with each release report.

