#!/usr/bin/env python3
"""Copilot CLI를 사용한 read-only 코드리뷰 스크립트."""

import subprocess
import sys


REVIEW_PROMPT = """아래 코드 diff를 코드리뷰해주세요.

## 리뷰 기준
1. 버그: 논리 오류, 잘못된 조건문, null/undefined 처리 누락, 경계값 오류
2. 보안: 인젝션, 인증/인가 누락, 민감 정보 노출, OWASP Top 10
3. 코드 품질: 네이밍, 중복 코드, 복잡도, 일관성, 에러 처리
4. 표준/스타일: 프로젝트 컨벤션 위반, 불필요한 import, 미사용 변수

## 출력 규칙
- 첫 줄에 반드시 "[Copilot gpt-5.3-codex Review]"를 출력
- 서론/인사말/부연설명 없이 바로 리뷰 결과만 출력
- 각 카테고리별로 이슈를 정리하고, 이슈가 없는 카테고리는 생략
- 이슈 없으면 "[Copilot gpt-5.3-codex Review]\n이슈 없음"이라고만 답변
- 한국어로 답변"""

MODEL = "gpt-5.3-codex"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def get_working_tree_state() -> dict:
    staged = git("diff", "--cached", "--name-only", "--", ".").splitlines()
    unstaged = git("diff", "--name-only", "--", ".").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard", "--", ".").splitlines()
    return {
        "staged": len(staged),
        "unstaged": len(unstaged),
        "untracked": len(untracked),
        "has_changes": bool(staged or unstaged or untracked),
    }


def collect_working_tree_diff() -> str:
    parts = []
    cached = git("diff", "--cached", "--", ".")
    if cached:
        parts.append(cached)
    unstaged = git("diff", "--", ".")
    if unstaged:
        parts.append(unstaged)

    untracked = git("ls-files", "--others", "--exclude-standard", "--", ".").splitlines()
    for path in untracked:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            parts.append(f"=== NEW FILE: {path} ===\n{content}")
        except OSError:
            continue

    return "\n".join(parts)


def collect_commit_diff(revision_range: str) -> str:
    return git("diff", revision_range, "--", ".")


def resolve_scope(arg: str, state: dict) -> str:
    if arg and arg != "auto":
        return arg
    return "working-tree" if state["has_changes"] else "last-commit"


def run_review(diff: str) -> None:
    proc = subprocess.run(
        ["copilot", "-p", REVIEW_PROMPT, "-s", "--model", MODEL],
        input=diff,
        text=True,
    )
    sys.exit(proc.returncode)


def main() -> None:
    scope_arg = sys.argv[1].strip() if len(sys.argv) > 1 else "auto"
    state = get_working_tree_state()
    scope = resolve_scope(scope_arg, state)

    if scope == "working-tree":
        label = f"워킹 트리 (staged: {state['staged']}, unstaged: {state['unstaged']}, untracked: {state['untracked']})"
        diff = collect_working_tree_diff()
    elif scope == "last-commit":
        commit_msg = git("log", "-1", "--pretty=format:%h %s", "--", ".")
        label = f"마지막 커밋: {commit_msg}"
        diff = collect_commit_diff("HEAD~1..HEAD")
    else:
        label = f"범위: {scope}"
        diff = collect_commit_diff(scope)

    if not diff:
        print("리뷰할 변경사항이 없습니다.")
        return

    print(f"리뷰 대상: {label}")
    print("---")
    run_review(diff)


if __name__ == "__main__":
    main()
