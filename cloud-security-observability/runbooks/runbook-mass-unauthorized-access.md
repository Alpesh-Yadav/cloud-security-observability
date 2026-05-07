# Runbook: Mass Unauthorized Access

## Triage
- Inspect spikes in `failed_auth_rate` and `unauthorized_api_calls_total`
- Check CloudWatch logs and SQS queue depth
- Identify suspicious sources or credentials

## MITRE ATT&CK Mapping
- T1078 Valid Accounts
- T1110 Brute Force

## Containment
- Revoke compromised creds
- Block suspicious IPs
- Disable affected roles
- Increase monitoring and alerting
