# copilot-review-skill

Claude Code(Anthropic Claude Opus/Sonnet)로 작성한 코드를 GitHub Copilot CLI(OpenAI GPT-5.3-Codex)로 크로스 리뷰하기 위한 Claude Code 커스텀 스킬.

## 왜 만들었나

Claude Code는 코드를 매우 잘 짜지만, 자기가 짠 코드를 자기가 리뷰하면 같은 사고 패턴에서 같은 맹점을 놓치기 쉽습니다. 마치 자기가 쓴 글을 자기가 교정하면 오타를 못 찾는 것과 같습니다.

이 스킬은 Claude Code 작업 흐름 안에서 `/review` 한 줄로 완전히 다른 모델 계열(OpenAI GPT-5.3-Codex)에게 코드리뷰를 위임합니다. 서로 다른 학습 데이터, 다른 아키텍처, 다른 편향을 가진 모델이 교차 검증하면 단일 모델 리뷰보다 사각지대가 줄어듭니다.

### 설계 원칙

- **Read-only**: 리뷰 결과를 보고 수정할지 말지는 사람이 판단합니다. 자동 수정 없음.
- **출처 명시**: 출력 첫 줄에 `[Copilot gpt-5.3-codex Review]`를 표시하여 Claude의 응답과 Copilot의 리뷰를 명확히 구분합니다.
- **최소 구조**: 셸 스크립트 대신 Python 단일 파일로 구현. 외부 의존성 없이 git + copilot CLI만 있으면 동작합니다.
- **비파괴적**: 프로젝트 코드를 건드리지 않습니다. `.claude/skills/` 안에서만 동작하고, git diff를 읽기만 합니다.

### 전형적인 워크플로우

```
1. Claude Code로 기능 개발 또는 버그 수정
2. /review 실행 → GPT-5.3-Codex가 diff를 리뷰
3. 리뷰 결과 확인 → 필요하면 Claude Code에게 수정 지시
4. 다시 /review → 이슈 없음 확인 후 커밋
```

Claude가 코드를 쓰고, Copilot이 검증하고, 사람이 최종 판단하는 3단계 구조입니다.

## 요구사항

- [Claude Code](https://claude.ai/code) (CLI, Desktop App, 또는 IDE Extension)
- [GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli) (`npm install -g @github/copilot-cli`)
- Python 3.8+
- Git

## 설치

프로젝트 루트에 `.claude/skills/review/` 디렉토리를 복사합니다:

```bash
# 프로젝트 루트에서
mkdir -p .claude/skills
cp -r path/to/copilot-review-skill/.claude/skills/review .claude/skills/
```

Copilot CLI 인증이 안 되어 있다면:

```bash
copilot login
```

## 사용법

Claude Code에서:

```
/review                  # 자동 감지 (변경사항 있으면 워킹 트리, 없으면 마지막 커밋)
/review last-commit      # 마지막 커밋 리뷰
/review HEAD~3..HEAD     # 최근 3개 커밋 리뷰
/review main...HEAD      # 브랜치 전체 리뷰
```

### 출력 예시

```
리뷰 대상: 마지막 커밋: 2574e1b refactor(prompt): 시스템 인스트럭션 간소화
---
[Copilot gpt-5.3-codex Review]

**버그**
1. `agent/agent.py:42` — 조건문에서 빈 리스트와 None을 구분하지 않아 ...

**보안**
이슈 없음

**코드 품질**
1. `agent/prompts/system.py:15` — 중복된 필터링 로직이 ...
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
    └── review.py         # Copilot CLI 실행 (scope 자동 감지)
```

## 동작 방식

1. git 워킹 트리 상태 확인 (staged, unstaged, untracked)
2. scope에 따라 diff 수집
3. Copilot CLI(`gpt-5.3-codex`)에 diff를 stdin으로 전달하여 한국어 코드리뷰 수행
4. 출력 첫 줄에 `[Copilot gpt-5.3-codex Review]` 표시
5. 결과를 그대로 출력 (자동 수정 없음)

## 커스터마이징

`review.py` 상단의 상수를 수정하면 됩니다:

| 상수 | 설명 | 기본값 |
|-----|------|-------|
| `MODEL` | Copilot CLI 모델 | `gpt-5.3-codex` |
| `REVIEW_PROMPT` | 리뷰 프롬프트 | 한국어, 4개 카테고리 |

다른 모델을 쓰고 싶다면:

```python
MODEL = "gpt-5.4"          # 최신 모델
MODEL = "gemini-3.1-pro"   # Gemini 사용
```

리뷰 언어를 영어로 바꾸고 싶다면 `REVIEW_PROMPT`의 마지막 줄을 `- Answer in English`로 변경하면 됩니다.

## 라이선스

MIT
