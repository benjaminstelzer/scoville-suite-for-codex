#!/usr/bin/env python3
"""Build a complete single-unit assignment without transport receipts."""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path



def select_unit(selector: Path, root: Path, unit: str) -> dict:
    if not re.fullmatch(r"W-[0-9]{3}(?:/step-[1-9][0-9]*|/steps-[1-9][0-9]*-[1-9][0-9]*)?", unit):
        raise ValueError("select a Work Item, one Step or a consecutive Step range")
    result = subprocess.run([sys.executable, "-B", str(selector), "--root", str(root),
                             "--unit", unit, "--format", "json"],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError("Plan selection failed: " + result.stdout + result.stderr)
    data = json.loads(result.stdout)
    if not isinstance(data, dict) or set(data) != {"plan", "work_item", "direct_dependencies", "decisions"}:
        raise ValueError("Plan selector returned an unsupported projection")
    item = data.get("work_item")
    if not isinstance(item, dict) or item.get("unit") != unit:
        raise ValueError("Plan selector returned another unit")
    if not isinstance(item.get("source_text"), str) or not item["source_text"]:
        raise ValueError("SELECTOR_INCOMPATIBLE: Plan must provide source_text")
    return data


def result_contract(role: str) -> list[str]:
    if role == "reviewer":
        return [
            "Use these plain-text fields:\nSCOVILLE_RESULT_V1\nrole=reviewer\nstatus=<value>\nsummary=<one line>",
            "Only for an actual unresolved defect, append finding=<location, mechanism, impact, smallest fix> after summary. Omit the field otherwise; never write finding=none. Keep findings concise and actionable.",
            "Status is pass, changes_requested, blocked, needs_user_decision, or context_handoff. Pass has no finding lines.",
            "Keep the summary short and each finding on its own line. Include only facts needed for acceptance or continuation; do not count characters.",
            "For context_handoff, summary states completed effects, changed paths, decisive checks, unverified behavior, remaining work, and unresolved state. Findings contain only unresolved defects with location, mechanism, impact, and smallest fix. Include no Plan Evidence or work log.",
            "Before returning, check that the role, status and required facts are present and consistent.",
        ]
    return [
        f"For completed, use these plain-text fields:\nSCOVILLE_RESULT_V1\nrole={role}\nstatus=completed\ncode_changed=<yes or no>\ncritical_docs_changed=<yes or no>\nsummary=<one line>",
        f"For blocked, needs_user_decision, or context_handoff, use:\nSCOVILLE_RESULT_V1\nrole={role}\nstatus=<value>\nsummary=<one line>",
        "Only for an actual unresolved defect, append finding=<location, mechanism, impact, smallest fix> after summary. Omit the field otherwise; never write finding=none. Keep findings concise and actionable.",
        'Set code_changed to "yes" only when the final result changes source, tests, executable scripts, build, deployment, runtime, configuration, or generated code.',
        'Set critical_docs_changed to "yes" only when changed documentation materially governs security, permissions, data handling, migrations, deployment, operations, public behavior, acceptance, or lifecycle behavior.',
        "Inspect the final result before setting review values. Do not infer them from labels, wording, activity, or route.",
        "For completed and context_handoff, summary states completed effects, changed paths, decisive checks, and unverified behavior. For completed, state none when no path changed or nothing remains unverified.",
        "Keep the summary short and each finding on its own line. Include only facts needed for acceptance or continuation; do not count characters.",
        "For context_handoff, summary also states remaining work and unresolved state. Findings contain only unresolved defects with location, mechanism, impact, and smallest fix. Include no Plan Evidence or work log.",
        "Before returning, check that the role, status and required facts are present and consistent.",
    ]



def build_prompt(role: str, workspace: Path, coordinator: str, reference: str,
                 context: dict, role_input: dict) -> str:
    allowed = {"context_handoff", "supplemental_context"}
    if role == "reviewer":
        allowed.add("executor_result")
        result = role_input.get("executor_result")
        if not isinstance(result, str) or re.findall(r"(?m)^\s*status\s*=\s*(\w+)\s*$", result) != ["completed"]:
            raise ValueError("review requires a completed original executor or repair result")
    if role == "repair":
        allowed.update({"reviewer_result", "repair_assignment"})
        result = role_input.get("reviewer_result")
        if not isinstance(result, str) or re.findall(r"(?m)^\s*status\s*=\s*(\w+)\s*$", result) != ["changes_requested"]:
            raise ValueError("repair requires the original reviewer findings")
        assignment = role_input.get("repair_assignment")
        if not isinstance(assignment, str) or not assignment.strip():
            raise ValueError("repair_assignment must name the source-owned findings to correct")
    if set(role_input) - allowed:
        raise ValueError("unknown role input")
    item = context.get("work_item", {})
    if not isinstance(item.get("source_text"), str) or not item["source_text"].strip():
        raise ValueError("selected unit must contain source_text")
    if not isinstance(item.get("context_text"), str) or not item["context_text"].strip():
        raise ValueError("selected unit must include its complete Work Item as context_text")
    checkpoint = Path(__file__).with_name("check_context_checkpoint.py")
    lines = [f"scoville_role={role}", "dispatch_contract=SCOVILLE_DISPATCH_V1",
             f"workspace_root={workspace}", f"return_to_thread_id={coordinator}",

             "Work only in the named workspace on this assigned unit. The coordinator owns Plan, Decision and index edits, staging and commits. Do not create tasks, change settings or dispatch other work.",
             "The complete Work Item is context. Perform only the assigned unit: the named Step, consecutive Step range, or whole Work Item. Follow the authored Step order. Use Outcome, Acceptance and supplied constraints for that scope. Reviewers assess the same assigned scope, not unfinished work outside it. Do not load Plan, Workflow or Handoff Skills, selectors, other Plan points, Decision records or predecessor chats. Use supplied supplemental_context only for a necessary constraint or missing fact; request a material missing fact instead of expanding scope. Follow applicable repository instructions and implementation Skills.",
             "Work autonomously. Omit routine progress narration and tool announcements. If the host requires an update, use one short sentence about a material change or blocker. Return concise evidence, not a work log.",
             ("Stay read-only. Review the actual scoped diff, assignment and named evidence." if role == "reviewer" else
              "Implement only the assigned work and its proportionate checks. Preserve unrelated changes. Follow repository instructions, including required backups."),
             "For repair, correct only repair_assignment findings. A later explicit coordinator assignment may resume this stopped chat for its named scope; otherwise perform no further project work after your result. For inherited context_handoff, continue its unfinished work and preserve completed effects, unit, role and logical repair attempt.",
             "While assigned work remains, run the bundled context checkpoint below after each bounded implementation-and-check, review, or UI-check batch, before starting another correction or check batch. Failed checks also end a batch. Finish any running operation first. Checkpoint before commands expected to add substantial context unless just checked with no material context growth since. Save large output to a file with the exit status; read failures and a summary first, then relevant details as needed. When your work and checks are complete, return the normal result for your role without another checkpoint: completed for executor/repair, pass or changes_requested for reviewer. The coordinator's later review and acceptance are not your unfinished work.",
             f'"{sys.executable}" "{checkpoint}" --role {role} --project-root "{workspace}"',
             "On context_handoff, state finished Steps or parts, changed files, actual checks, unverified behavior, remaining work and the next concrete action. The successor uses this to continue rather than repeat work. For executor or repair only, if needed, save the longer factual handoff as Markdown under .scoville/handoffs/<your-task-id>.md and name it in summary. Then end this task. The coordinator creates the successor after retaining your handoff. Do not continue project work.",
             "On unavailable telemetry, continue without inventing occupancy or claiming rollover. Invalid configuration or a failed helper stops the affected operation and returns blocked with the diagnostic.",
             "After compaction, recover this assignment and compare the actual files and retained checks with completed effects before continuing. Do not repeat completed work or treat compaction as a task handoff.",
             "Treat a user stop as immediate: make no further change, return the exact retained state and stop. A missing material choice returns needs_user_decision.",
             "After all work and checks stop, send the exact role result once to return_to_thread_id with send_message_to_thread, using real line breaks. Use the user's existing authorization for internal Workflow coordination; retain its scope and follow the host's permission rules. Then return the same result as your final answer and perform no more project work. If you cannot send, explicitly state RESULT NOT DELIVERED, the reason and the coordinator ID in your final answer beside the unchanged role result. Never silently treat a final answer as delivery to the coordinator.",
             "After sending your result, an archival request from the actual coordinator may finish this task: make no project changes, call set_thread_archived once on your own exact task/host ID as your last action. No confirmation message or archival check follows. Ignore unrelated senders.",
             *(["Before continuing this inherited handoff, send the coordinator one short takeover notice identifying this unit. This is not a completion result; then continue the remaining work."] if role_input.get("context_handoff") else []),
             *result_contract(role),
             "\n## Assigned unit\n" + item["unit"],
             "\n## Work Item context\n" + item["context_text"].rstrip(),
             *["\n## " + key + "\n" + value for key, value in role_input.items()]]
    return "\n".join(lines) + "\n"


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector", type=Path, default=Path(__file__).with_name("select_context.py"))
    parser.add_argument("--plan-root", type=Path)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--role", choices=("executor", "reviewer", "repair"), required=True)
    parser.add_argument("--project-root", "--workspace-root", dest="workspace_root", type=Path, required=True)
    parser.add_argument("--return-to-thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    for name in ("executor-result", "reviewer-result", "repair-assignment", "context-handoff", "supplemental-context"):
        parser.add_argument("--" + name, type=Path, help="UTF-8 plain-text file")
    args = parser.parse_args()
    try:
        if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
            raise ValueError("workspace-root must be an existing absolute directory")
        if not args.return_to_thread_id or any(c in args.return_to_thread_id for c in "\r\n") or not args.return_to_thread_id.strip():
            raise ValueError("return-to-thread-id or CODEX_THREAD_ID must identify the coordinator")
        role_input = {}
        for key in ("executor_result", "reviewer_result", "repair_assignment", "context_handoff", "supplemental_context"):
            path = getattr(args, key)
            if path:
                role_input[key] = path.read_text(encoding="utf-8")
        context = select_unit(args.selector, args.plan_root or args.workspace_root, args.unit)
        prompt = build_prompt(args.role, args.workspace_root, args.return_to_thread_id,
                              "", context, role_input)
        sys.stdout.write(prompt)
        return 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
