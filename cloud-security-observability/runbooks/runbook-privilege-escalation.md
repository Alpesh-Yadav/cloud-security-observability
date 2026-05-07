# Runbook: Privilege Escalation

## Detection
- PromQL: `sum(rate(security_exporter_iam_policy_changes_total[5m])) > 0`
- Look for anomalous IAM policy change activity

## Investigation
1. Identify the principal and activity source.
2. Review CloudWatch and IAM logs.
3. Validate whether changes were authorized.

## Remediation
- Revert unauthorized IAM changes.
- Enforce least privilege and MFA.
- Rotate impacted credentials.
