# Rule Promotion Rules

missed-patterns.md에 축적된 사례를 규칙으로 승격할 때의 기준과 절차.

## 승격 기준 (5개 모두 충족)

1. **재현 가능**: 동일 유형의 누락이 2회 이상 기록됨
2. **범용 적용**: 특정 태스크/도메인이 아닌 다른 유형의 작업에도 적용 가능
3. **규칙화 가능**: 체크리스트 항목, taxonomy 카테고리, 또는 스크립트 검사로 표현 가능
4. **False positive 낮음**: 정상 사례를 오탐하는 비율이 수용 가능 수준
5. **실제 누락 사례 존재**: missed-patterns.md에 구체적 MISSED- 엔트리가 있음

## 핵심 원칙

- **발견자 != 규칙 확정자**: 문제를 놓친 에이전트/세션이 직접 규칙을 확정하지 않음
- **references/ & scripts/ 먼저**: SKILL.md 본문 수정은 최후 수단
- **데이터 선행**: 충분한 missed-patterns 엔트리가 쌓인 뒤에만 승격 검토
- **1회성 사례 금지**: 단 1번 발생한 문제를 바로 규칙화하지 않음

## 에이전트 자동화 활성화 임계값

| 조건 | 값 | 의미 |
|------|---|------|
| pattern-analyst 최초 실행 | missed-patterns.md 엔트리 >= 5개 | 분석할 데이터가 충분함 |
| pattern-analyst 정기 실행 | 마지막 분석 이후 신규 엔트리 >= 3개 | 새 패턴이 축적됨 |
| regression-verifier 실행 | rule-update-proposal.md 작성됨 + qa-archive에 과거 사례 >= 2개 | 검증할 규칙과 데이터가 모두 있음 |

임계값 미달 시 에이전트를 실행하지 않는다. 데이터 없이 분석하면 과적합된 규칙이 나온다.

## 승격 대상 결정

| 패턴 유형 | 승격 위치 | 판단 기준 |
|-----------|----------|----------|
| 파일 존재/형식/정합성으로 잡을 수 있는 것 | `scripts/audit_validated_plan_run.py` | 자동화 가능한 구조 검사 |
| 에이전트가 확인할 의미 검증 항목 | `references/checklist.md` | Layer 1-B 또는 Layer 2 체크항목 |
| 새로운 실패 카테고리 | `references/failure-taxonomy.md` | 기존 10개 유형에 안 맞는 실패 |
| 판정 매트릭스 수정 | `references/verdict-rules.md` | verdict 로직 자체의 결함 |
| 위 어디에도 안 맞을 때만 | `SKILL.md` 본문 | 최후 수단 |

## 승격 절차

### 현재 (수동, 데이터 축적 단계)

1. missed-patterns.md에서 유사 엔트리 3개 이상인 패턴을 식별
2. "왜 못 잡았는지" 필드의 공통점을 분석
3. 규칙 추가안을 작성하여 해당 reference/script에 반영
4. qa-archive의 과거 사례로 새 규칙이 해당 문제를 잡는지 수동 확인
5. false positive가 없는지 정상 사례에도 적용하여 확인

### 향후 (에이전트 자동화, 임계값 충족 후)

1. pattern-analyst가 missed-patterns.md 분석 -> rule-update-proposal.md 작성
2. regression-verifier가 qa-archive로 검증 -> regression-check.md 작성
3. 검증 통과 시 해당 reference/script에 반영

## 반려 사유

- 사례가 1건뿐 (재현 미확인)
- 특정 프로젝트/도메인에만 해당 (범용성 부족)
- 자연어 판단에 의존하여 규칙으로 표현 불가
- 기존 규칙과 충돌하거나 중복
- false positive가 높을 것으로 예상
- qa-archive 과거 사례에서 검증 실패
