---
allowed-tools: Read, Glob, Grep, Bash
argument-hint: [route|validate|seams]
description: Route and validate the FreeUp Space plus MAC_App_Audit file-based federation without creating an umbrella runtime.
---

# Mac Tools Federation Command

Use the `mac-tools-federation` skill instructions.

Parse `$ARGUMENTS`:

- `route`: classify a user request as FreeUp Space, mac-app-audit, or both.
- `validate`: run the federation validator and smoke test.
- `seams`: inspect `MAC_App_Audit/example_ledger.json` for cross-producer
  `related_entries`.
- no argument: read `FEDERATION.md` and summarize the ownership boundary.

Never build or invoke an umbrella CLI/runtime. The federation is files,
schemas, ledgers, safety rules, and agent routing.
