#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


BASE_FILES = [
    ("clarify-result.md", r"^# Clarify Result: (?P<slug>.+)$"),
    ("plan-v1.md", None),
    ("validation-v1.md", r"^# Validation v1: (?P<slug>.+)$"),
    ("meta-evaluation.md", None),
    ("validation-v2.md", r"^# Validation v2: (?P<slug>.+)$"),
    ("plan-v1-review.md", r"^# Plan v1 Review: (?P<slug>.+)$"),
    ("plan-v2.md", None),
    ("execution-manifest.md", r"^# Execution Manifest: (?P<slug>.+)$"),
    ("execution-review.md", r"^# Execution Review: (?P<slug>.+)$"),
]

ROUND_FILES = [
    ("gap-plan-r1.md", None),
    ("execution-review-r1.md", r"^# Execution Review Round 1: (?P<slug>.+)$"),
    ("gap-plan-r2.md", None),
    ("execution-review-r2.md", r"^# Execution Review Round 2: (?P<slug>.+)$"),
]

FILE_TOKEN = re.compile(r"(?P<path>[\w./-]+\.[A-Za-z0-9]+)")


@dataclass
class Finding:
    level: str
    area: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_first_heading(path: Path) -> str | None:
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def extract_section(lines: list[str], heading: str) -> list[str]:
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == heading:
            start = idx + 1
            break
    if start is None:
        return []
    section: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if stripped:
            section.append(stripped)
    return section


def normalize_list_entry(raw: str) -> str:
    text = raw.strip()
    if text.startswith("- "):
        text = text[2:].strip()
    text = re.sub(r"\s+\([^)]*\)$", "", text)
    if " — " in text:
        text = text.split(" — ", 1)[0].strip()
    return text


def extract_mapped_path(raw: str) -> str | None:
    text = raw.strip()
    if text.startswith("- "):
        text = text[2:].strip()
    matches = FILE_TOKEN.findall(text)
    return matches[0] if matches else None


def git_status_paths(repo_root: Path) -> set[str]:
    try:
        output = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return set()

    paths = set()
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def latest_review_path(plan_dir: Path) -> Path:
    for name in ["execution-review-r2.md", "execution-review-r1.md", "execution-review.md"]:
        path = plan_dir / name
        if path.exists():
            return path
    return plan_dir / "execution-review.md"


def add_finding(findings: list[Finding], level: str, area: str, message: str) -> None:
    findings.append(Finding(level, area, message))


def check_required_files(plan_dir: Path, slug: str, findings: list[Finding]) -> None:
    for name, heading_pattern in BASE_FILES + ROUND_FILES:
        path = plan_dir / name
        if name.startswith("gap-plan-r") or name.startswith("execution-review-r"):
            continue
        if not path.exists():
            add_finding(findings, "FAIL", "run-integrity", f"missing required artifact: {name}")
            continue
        if path.stat().st_size == 0:
            add_finding(findings, "FAIL", "run-integrity", f"empty artifact: {name}")
        if heading_pattern:
            heading = read_first_heading(path)
            if not heading:
                add_finding(findings, "FAIL", "run-integrity", f"missing heading in: {name}")
                continue
            match = re.match(heading_pattern, heading)
            if not match:
                add_finding(findings, "FAIL", "run-integrity", f"invalid heading format in: {name}")
                continue
            embedded_slug = match.group("slug").strip()
            if embedded_slug != slug:
                add_finding(
                    findings,
                    "FAIL",
                    "run-integrity",
                    f"slug mismatch in {name}: directory={slug}, file={embedded_slug}",
                )


def check_base_order(plan_dir: Path, findings: list[Finding]) -> None:
    existing = [plan_dir / name for name, _ in BASE_FILES if (plan_dir / name).exists()]
    for earlier, later in zip(existing, existing[1:]):
        if earlier.stat().st_mtime > later.stat().st_mtime + 1:
            add_finding(
                findings,
                "WARN",
                "run-integrity",
                f"upstream artifact newer than downstream artifact: {earlier.name} > {later.name}",
            )


def check_loop_consistency(plan_dir: Path, findings: list[Finding]) -> None:
    initial_review = plan_dir / "execution-review.md"
    r1_plan = plan_dir / "gap-plan-r1.md"
    r1_review = plan_dir / "execution-review-r1.md"
    r2_plan = plan_dir / "gap-plan-r2.md"
    r2_review = plan_dir / "execution-review-r2.md"

    if initial_review.exists():
        text = read_text(initial_review)
        if ("전체 pass" in text or "Gap 보완 불필요" in text) and any(
            path.exists() for path in [r1_plan, r1_review, r2_plan, r2_review]
        ):
            add_finding(
                findings,
                "WARN",
                "run-integrity",
                "initial execution-review says all pass, but gap-loop artifacts also exist",
            )

    if r1_plan.exists() and not r1_review.exists():
        add_finding(findings, "WARN", "run-integrity", "gap-plan-r1.md exists without execution-review-r1.md")
    if r1_review.exists() and not r1_plan.exists():
        add_finding(findings, "WARN", "run-integrity", "execution-review-r1.md exists without gap-plan-r1.md")
    if r2_plan.exists() and not r1_review.exists():
        add_finding(findings, "FAIL", "run-integrity", "gap-plan-r2.md exists before round-1 review is present")
    if r2_review.exists() and not r2_plan.exists():
        add_finding(findings, "WARN", "run-integrity", "execution-review-r2.md exists without gap-plan-r2.md")

    for name, heading_pattern in ROUND_FILES:
        path = plan_dir / name
        if not path.exists() or not heading_pattern:
            continue
        heading = read_first_heading(path)
        if not heading or not re.match(heading_pattern, heading):
            add_finding(findings, "FAIL", "run-integrity", f"invalid round review heading: {name}")


def check_manifest(plan_dir: Path, repo_root: Path, findings: list[Finding]) -> None:
    manifest = plan_dir / "execution-manifest.md"
    if not manifest.exists():
        return

    lines = read_text(manifest).splitlines()
    changed = {normalize_list_entry(line) for line in extract_section(lines, "## 변경된 파일 목록")}
    created = {normalize_list_entry(line) for line in extract_section(lines, "## 새로 생성된 파일")}
    mapped = {
        path
        for path in (extract_mapped_path(line) for line in extract_section(lines, "## Plan v2 Step별 산출물 매핑"))
        if path
    }

    if not changed:
        add_finding(findings, "FAIL", "evidence-integrity", "execution-manifest.md has no changed-file entries")
    if not mapped:
        add_finding(findings, "FAIL", "evidence-integrity", "execution-manifest.md has no mapped output files")

    manifest_mtime = manifest.stat().st_mtime

    for path in sorted(created):
        if path not in changed:
            add_finding(findings, "WARN", "evidence-integrity", f"new file not present in changed list: {path}")

    for path in sorted(mapped | changed | created):
        abs_path = (repo_root / path).resolve()
        if not abs_path.exists():
            add_finding(findings, "WARN", "evidence-integrity", f"referenced file does not exist: {path}")
            continue
        if abs_path.stat().st_mtime > manifest_mtime + 1:
            add_finding(
                findings,
                "WARN",
                "evidence-integrity",
                f"file changed after manifest generation, manifest may be stale: {path}",
            )

    for path in sorted(mapped):
        if path not in changed and path not in created:
            add_finding(findings, "WARN", "evidence-integrity", f"mapped output missing from changed/new lists: {path}")

    for path in sorted(git_status_paths(repo_root)):
        if path not in changed and path not in created:
            add_finding(findings, "WARN", "evidence-integrity", f"worktree change not represented in manifest: {path}")

    if any((plan_dir / name).exists() for name in ["gap-plan-r1.md", "execution-review-r1.md", "gap-plan-r2.md", "execution-review-r2.md"]):
        add_finding(
            findings,
            "WARN",
            "evidence-integrity",
            "gap loop artifacts exist; verify execution-manifest was refreshed after gap execution, or revalidation may rely on stale evidence",
        )


def check_structural_traceability(plan_dir: Path, findings: list[Finding]) -> None:
    clarify = plan_dir / "clarify-result.md"
    plan = plan_dir / "plan-v2.md"
    review = latest_review_path(plan_dir)

    clarify_text = read_text(clarify)
    for heading in ["## 목표", "## 이유", "## 성공 기준", "## 제약"]:
        if heading not in clarify_text:
            add_finding(findings, "FAIL", "spec-fidelity", f"clarify-result.md missing section: {heading}")

    plan_text = read_text(plan)
    if "[Core]" not in plan_text:
        add_finding(findings, "FAIL", "spec-fidelity", "plan-v2.md has no [Core] step tag")
    if "수락 기준" not in plan_text:
        add_finding(findings, "FAIL", "spec-fidelity", "plan-v2.md has no acceptance criteria section")

    if review.exists():
        review_text = read_text(review)
        if "## 평가 요약" not in review_text:
            add_finding(findings, "WARN", "spec-fidelity", f"{review.name} has no evaluation summary section")
        if "Gap" not in review_text and "전체 pass" not in review_text:
            add_finding(findings, "WARN", "spec-fidelity", f"{review.name} does not clearly state gap status")


def print_report(findings: list[Finding], plan_dir: Path) -> int:
    if not findings:
        print(f"PASS validated-plan final QA baseline checks passed for: {plan_dir}")
        return 0

    order = {"FAIL": 0, "WARN": 1}
    findings.sort(key=lambda item: (order[item.level], item.area, item.message))
    print(f"Validated-plan final QA findings for: {plan_dir}")
    for finding in findings:
        print(f"{finding.level} [{finding.area}] {finding.message}")

    return 1 if any(item.level == "FAIL" for item in findings) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a validated-plan run directory for final QA signals.")
    parser.add_argument("plan_dir", help="Path to .omc/plans/{task-slug}")
    parser.add_argument("--repo-root", default=".", help="Repository root used for manifest file checks")
    args = parser.parse_args()

    plan_dir = Path(args.plan_dir).resolve()
    repo_root = Path(args.repo_root).resolve()

    if not plan_dir.exists() or not plan_dir.is_dir():
        print(f"FAIL plan directory not found: {plan_dir}")
        return 1

    findings: list[Finding] = []
    slug = plan_dir.name

    check_required_files(plan_dir, slug, findings)
    check_base_order(plan_dir, findings)
    check_loop_consistency(plan_dir, findings)
    check_manifest(plan_dir, repo_root, findings)
    check_structural_traceability(plan_dir, findings)

    return print_report(findings, plan_dir)


if __name__ == "__main__":
    sys.exit(main())
