# Tasks: 20260627-193714-planning-quality-gates

## Task T001: Convert The First Plan Slice Into An Atomic Change

- Task: Implement one independently verifiable XS/S change from the approved plan.
- Outcome: One success criterion from `spec.md` is moved closer to verified completion without unrelated edits.
- Exact Scope: One cohesive code, test, documentation, or harness-artifact change selected from the approved plan.
- Non-Scope: Unrelated refactors, dependency additions, release work, and broad cleanup outside the selected slice.
- Size: XS
- Acceptance:
  - The selected change is complete for its narrow scope.
  - The implementation remains compatible with the approved plan and spec boundaries.
- Scenario:
  - Given the approved intake, spec, and plan
  - When this atomic task is implemented and verified
  - Then the matching acceptance criterion has concrete evidence
- Verify: Run the closest targeted command or manual evidence check and record the result.
- Dependencies: Approved plan gate.
- Files: `.harness/requests/20260627-193714-planning-quality-gates/tasks.md`, plus the concrete implementation file path selected before editing.
- Risk Notes: The main risk is choosing a task that is too broad; split again if it touches independent subsystems.
- Rollback/Repair: Revert only the selected task's changes or repair the smallest failing check attribution.
- Parallelization: Sequential until concrete files and dependencies are known.

## Checkpoint

- [ ] State and history are updated.
- [ ] Required verification evidence is recorded.
- [ ] No task is larger than S; split M/L/XL work before implementation.
