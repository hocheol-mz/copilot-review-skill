# copilot-review-skill

Claude Code에서 GitHub Copilot CLI를 사용한 read-only 코드리뷰 스킬.

## 요구사항

- [Claude Code](https://claude.ai/code)
- [GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli) (`npm install -g @github/copilot-cli`)

## 설치

프로젝트 루트에 `.claude/skills/review/` 디렉토리를 복사합니다:

```bash
# 프로젝트 루트에서
mkdir -p .claude/skills
cp -r path/to/copilot-review-skill/.claude/skills/review .claude/skills/
```

## 사용법

Claude Code에서:

```
/review                  # 자동 감지 (변경사항 있으면 워킹 트리, 없으면 마지막 커밋)
/review last-commit      # 마지막 커밋 리뷰
/review HEAD~3..HEAD     # 최근 3개 커밋 리뷰
/review main...HEAD      # 브랜치 전체 리뷰
```

## 리뷰 기준

| 카테고리 | 점검 항목 |
|---------|----------|
| 버그 | 논리 오류, 잘못된 조건문, null/undefined 처리 누락, 경계값 오류 |
| 보안 | 인젝션, 인증/인가 누락, 민감 정보 노출, OWASP Top 10 |
| 코드 품질 | 네이밍, 중복 코드, 복잡도, 일관성, 에러 처리 |
| 표준/스타일 | 프로젝트 컨벤션 위반, 불필요한 import, 미사용 변수 |

## 구조

```
.claude/skills/review/
├── SKILL.md              # 스킬 정의 (진입점, read-only 강제)
└── scripts/
    └── review.sh         # Copilot CLI 실행 (scope 자동 감지)
```

## 동작 방식

1. git 워킹 트리 상태 확인 (staged, unstaged, untracked)
2. scope에 따라 diff 수집
3. Copilot CLI (`gpt-5.3-codex`)에 diff를 전달하여 한국어 코드리뷰 수행
4. 결과를 그대로 출력 (자동 수정 없음)

## 라이선스

MIT
