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
        raise ValueError(f"--unit {unit!r} is invalid; use an existing Work Item, Step or consecutive range, e.g. W-001, W-001/step-2 or W-001/steps-1-3 (lowercase step/steps)")
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
    statuses = ("pass, changes_requested, blocked, needs_user_decision, context_handoff"
                if role == "reviewer" else "completed, blocked, needs_user_decision, context_handoff")
    return [
        "Return a concise normal message with an explicit status: " + statuses + ". No version marker, fixed field syntax, JSON or change flags are required.",
        "State completed effects, relevant changed paths, decisive checks and unverified behavior. For context_handoff, add unfinished work, needed constraints and the next action. Keep only facts needed to assess or continue correctly.",
        "Findings name the actual unresolved defect, location, effect and smallest correction. A reviewer pass has no unresolved findings. Do not count characters or include a work log.",
    ]


def build_prompt(role: str, workspace: Path, coordinator: str, reference: str,
                 context: dict, role_input: dict) -> str:
    allowed = {"context_handoff", "supplemental_context", "predecessor_thread_id"}
    if role == "reviewer":
        allowed.add("executor_result")
        result = role_input.get("executor_result")
        if not isinstance(result, str) or not result.strip():
            raise ValueError("review requires the original worker result; supply it with --executor-result")
    if role == "executor":
        allowed.update({"reviewer_result"})
    if set(role_input) - allowed:
        raise ValueError("unknown role input")
    if role_input.get("context_handoff") and not role_input.get("predecessor_thread_id", "").strip():
        raise ValueError("continuation requires --predecessor-thread-id so the successor can confirm receipt directly")
    item = context.get("work_item", {})
    if not isinstance(item.get("source_text"), str) or not item["source_text"].strip():
        raise ValueError("selected unit must contain source_text")
    if not isinstance(item.get("context_text"), str) or not item["context_text"].strip():
        raise ValueError("selected unit must include its complete Work Item as context_text")
    checkpoint = Path(__file__).with_name("check_context_checkpoint.py")
    lines = [f"scoville_role={role}", "dispatch_contract=SCOVILLE_DISPATCH_V1",
             f"workspace_root={workspace}", f"return_to_thread_id={coordinator}",

             "Work only in the named workspace on this assigned unit. The coordinator owns Plan, Decision and index edits, staging and commits. Do not create tasks, change Workflow or model settings, or dispatch other work. Product and test configuration may change only within the assigned scope and project constraints; reviewers remain read-only.",
             "The complete Work Item is context. Perform only the assigned unit: the named Step, consecutive Step range, or whole Work Item. Follow the authored Step order. Use Outcome, Acceptance and supplied constraints for that scope. Reviewers assess the same assigned scope, not unfinished work outside it. Do not load Plan, Workflow or Handoff Skills, selectors, other Plan points, Decision records or predecessor chats. Use supplied supplemental_context only for a necessary constraint or missing fact; Workers request material missing facts instead of expanding scope; reviewers include missing facts and their effect on the verdict in their one complete result. Follow applicable repository instructions and implementation Skills.",
             "Work autonomously. Omit routine progress narration and tool announcements. If the host requires an update, use one short sentence about a material change or blocker. Keep every result and handoff as short as possible and only as long as necessary. Necessary facts let the receiver assess or continue the assigned work correctly without hidden context. Preserve current state, binding constraints, evidence limits and the next action; omit repetition and history that no longer affects the work.",
             ("Stay read-only. Review the unreviewed diff and affected Acceptance identified in supplemental_context, including relevant interactions. Reuse supplied earlier assessments for unchanged parts; do not review those parts again. Report a missing review boundary instead of assuming a whole-tree review." if role == "reviewer" else
              "Implement only the assigned work and its proportionate checks. Preserve unrelated changes. Follow repository instructions, including required backups. Fixing product code that was complete or checked before this assignment completes your assignment after focused checks: return the checked fix without another checkpoint or further tests. Name remaining Step work for the coordinator; this does not complete the whole Step. Correct intermediate errors in code you are implementing in this assignment and continue the assignment normally."),
             "When reviewer_result is supplied, correct the assigned source findings and verify them. For inherited context_handoff, continue unfinished work and preserve completed effects. After your result, do no more project work; workers may answer necessary questions; reviewers give one complete assessment without a question round. Self-archive when instructed.",
             "While assigned work remains, run the bundled context checkpoint below after each bounded implementation-and-check, review, or UI-check batch, before starting another correction or check batch. Failed checks also end a batch. Finish any running operation first. Checkpoint before commands expected to add substantial context unless just checked with no material context growth since. Save large output to a file with the exit status; read failures and a summary first, then relevant details as needed. When your work and checks are complete, return the normal result for your role without another checkpoint: completed for executor, pass or changes_requested for reviewer. The coordinator's later review and acceptance are not your unfinished work.",
             f'"{sys.executable}" "{checkpoint}" --role {role} --project-root "{workspace}"',
             "On context_handoff, state finished Steps or parts, changed files, actual checks, unverified behavior, remaining work and the next concrete action. The successor uses this to continue rather than repeat work. Put the needed handoff directly in your result message. Then end this task. The coordinator creates the successor after retaining your handoff. Do not continue project work.",
             "On unavailable telemetry, continue without inventing occupancy or claiming rollover. Invalid configuration or a failed helper stops the affected operation and returns blocked with the diagnostic.",
             "After compaction, recover this assignment and compare the actual files and retained checks with completed effects before continuing. Do not repeat completed work or treat compaction as a task handoff.",
             "Treat a user stop as immediate: make no further change, return the exact retained state and stop. A missing material choice returns needs_user_decision.",
             "After all work and checks stop, send the exact role result once to return_to_thread_id with send_message_to_thread, using real line breaks. Use the user's existing authorization for internal Workflow coordination; retain its scope and follow the host's permission rules. Then return the same result as your final answer and perform no more project work. If you cannot send, explicitly state RESULT NOT DELIVERED, the reason and the coordinator ID in your final answer beside the unchanged role result. Never silently treat a final answer as delivery to the coordinator.",
             "After sending your result, an archival request from the coordinator or the assigned rollover successor finishes this task: make no project changes, call set_thread_archived once on your own exact task/host ID as your last action. No confirmation message or archival check follows. ",
             *(["Before continuing this inherited handoff, call send_message_to_thread with predecessor_thread_id as threadId and 'I have the information. You can archive yourself now.' as prompt. A reply in your own chat does not deliver this message. Then continue the remaining work; send your result to the coordinator."] if role_input.get("context_handoff") else []),
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
    parser.add_argument("--role", choices=("executor", "reviewer"), required=True)
    parser.add_argument("--project-root", "--workspace-root", dest="workspace_root", type=Path, required=True)
    parser.add_argument("--return-to-thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--predecessor-thread-id")
    for name in ("executor-result", "reviewer-result", "context-handoff", "supplemental-context"):
        parser.add_argument("--" + name, type=Path, help="UTF-8 plain-text file")
    args = parser.parse_args()
    try:
        if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
            raise ValueError(f"--project-root/--workspace-root {str(args.workspace_root)!r} must be an existing absolute project directory; supply the actual checkout path")
        if not args.return_to_thread_id or any(c in args.return_to_thread_id for c in "\r\n") or not args.return_to_thread_id.strip():
            raise ValueError("No valid coordinator ID: supply --return-to-thread-id <actual-chat-id> or use the host's CODEX_THREAD_ID; the ID must be nonempty and contain no line breaks")
        role_input = {}
        if args.predecessor_thread_id:
            role_input["predecessor_thread_id"] = args.predecessor_thread_id
        for key in ("executor_result", "reviewer_result", "context_handoff", "supplemental_context"):
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
