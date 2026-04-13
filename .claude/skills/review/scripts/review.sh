#!/usr/bin/env bash
set -euo pipefail

SCOPE="${1:-auto}"

# Check working tree state
STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
UNSTAGED=$(git diff --name-only | wc -l | tr -d ' ')
UNTRACKED=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')
HAS_CHANGES=$(( STAGED + UNSTAGED + UNTRACKED ))

# Resolve scope
if [[ "$SCOPE" == "auto" ]]; then
  if [[ "$HAS_CHANGES" -gt 0 ]]; then
    SCOPE="working-tree"
  else
    SCOPE="last-commit"
  fi
fi

# Collect diff
case "$SCOPE" in
  working-tree)
    LABEL="워킹 트리 (staged: ${STAGED}, unstaged: ${UNSTAGED}, untracked: ${UNTRACKED})"
    DIFF=$( { git diff --cached; git diff; git ls-files -z --others --exclude-standard | while IFS= read -r -d '' f; do echo "=== NEW FILE: $f ==="; cat -- "$f" 2>/dev/null; done; } )
    ;;
  last-commit)
    COMMIT_MSG=$(git log -1 --pretty=format:"%h %s")
    LABEL="마지막 커밋: ${COMMIT_MSG}"
    DIFF=$(git diff HEAD~1..HEAD)
    ;;
  *)
    LABEL="범위: ${SCOPE}"
    DIFF=$(git diff "${SCOPE}")
    ;;
esac

if [[ -z "$DIFF" ]]; then
  echo "리뷰할 변경사항이 없습니다."
  exit 0
fi

echo "리뷰 대상: ${LABEL}"
echo "---"

PROMPT='아래 코드 diff를 코드리뷰해주세요.

## 리뷰 기준
1. 버그: 논리 오류, 잘못된 조건문, null/undefined 처리 누락, 경계값 오류
2. 보안: 인젝션, 인증/인가 누락, 민감 정보 노출, OWASP Top 10
3. 코드 품질: 네이밍, 중복 코드, 복잡도, 일관성, 에러 처리
4. 표준/스타일: 프로젝트 컨벤션 위반, 불필요한 import, 미사용 변수

## 출력 규칙
- 각 카테고리별로 이슈를 정리하고, 이슈가 없는 카테고리는 생략
- 이슈 없으면 "이슈 없음"이라고만 답변
- 한국어로 답변'

echo "$DIFF" | copilot -p "$PROMPT" -s --model "gpt-5.3-codex"
