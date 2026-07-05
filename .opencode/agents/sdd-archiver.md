---
description: Archive all SDD artifacts into a single completed record in memory.
mode: subagent
model: opencode-go/deepseek-v4-pro
hidden: true
permission:
  edit: deny
---
Load the `sdd-archive` skill and execute it for the given change_id.

1. Load all phase artifacts from memory (context, proposal, spec, design, tasks, impl, verify)
2. Write consolidated archive entry
Save to memory: title=`SDD Complete: <change_id>`, topic_key=`sdd-<change_id>-done`, type=`summary`