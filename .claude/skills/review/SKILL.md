---
name: review
description: Copilot CLI로 코드리뷰 (read-only, 수정 금지)
allowed-tools:
  - Bash
  - Read
---

Copilot CLI를 사용한 read-only 코드리뷰를 실행합니다.

## 실행

아래 명령어를 실행하고 출력 결과를 그대로 보여주세요:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/review.sh" "$ARGUMENTS"
```

- 인자 없으면: 워킹 트리 변경사항이 있으면 워킹 트리, 없으면 마지막 커밋 리뷰
- `last-commit`: 마지막 커밋 리뷰
- `HEAD~3..HEAD`: 특정 범위 리뷰
- `main...HEAD`: 브랜치 전체 리뷰

## 규칙

1. 출력 결과를 그대로 보여줄 것. 요약/편집 금지.
2. 리뷰 결과를 기반으로 코드를 수정하지 말 것. read-only.
3. 사용자가 명시적으로 수정을 요청하기 전까지 Edit/Write 도구 사용 금지.
