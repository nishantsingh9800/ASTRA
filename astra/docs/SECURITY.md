# ASTRA 2.0 Security & Safety

ASTRA integrates strict safety and security protocols at the orchestration level.

## Upgrade Supervisor & Safe Rollbacks
ASTRA's self-improvement pipeline cannot silently rewrite the production system.
1. Improvements are proposed based on strict telemetry thresholds.
2. Candidate code is built in an **Isolated Workspace**.
3. The **Upgrade Supervisor** gates deployment behind automated unit tests, integration tests, and security scans.
4. Post-deployment, the **Release Manager** runs a live health check. If core systems (Voice, Vision, Safety) fail, the system is immediately rolled back to the last known-good configuration.

## DemoSafeMode & Presentation
During demonstrations (activated via "Astra, presentation mode"), **DemoSafeMode** strictly intercepts and rejects all destructive actions (e.g., file deletions, sending emails) while maintaining the illusion of a standard run for the audience. The presentation engine guarantees truthful responses by pulling live runtime state (e.g., connected hardware, offline status) rather than hallucinating capabilities.

## Permissions & Least Privilege
ASTRA agents run with least privilege. The underlying OS control tools require explicit authorization for medium/high-risk actions (modifying files, sharing private information, triggering emergency workflows).

## Emergency SOS
The **SafetyEngine** uses sensor fusion to detect falls or accidents. It utilizes a verification countdown before firing SOS payloads. ASTRA will never falsely claim an SOS was sent unless the external test/production channel explicitly confirms successful delivery.
