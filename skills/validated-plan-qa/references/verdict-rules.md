# Verdict Rules

## Layer 1 오버라이드 (최우선)

아래 중 하나라도 해당하면, Layer 2/3 결과와 무관하게 **FAIL**:

- 필수 산출물 누락 (clarify-result, plan-v2, execution-manifest, execution-review 중 하나라도)
- gap 루프 파일 정합성 깨짐 (쌍 불일치)
- 기준 약화 감지 (R-4 fail)
- gap 루프 정직성 위반 (해석만 변경하여 pass 처리)

## 판정 매트릭스

Layer 1이 통과한 후, Layer 2와 3으로 최종 verdict를 결정한다.

### PASS

- Layer 1: 구조+의미 검사 모두 통과
- 체인 판정: PASS (15/15 또는 동등)
- 독립 판정: PASS
- 불일치: 없음

### CONDITIONAL PASS

아래 중 하나:

- 체인 PASS + 독립 PARTIAL → 독립 판정의 FAIL 항목 상세 기술
- 체인 PARTIAL + 독립 PASS → validation 기준 재검토 권고
- 체인 PARTIAL + 독립 PARTIAL → 합집합 Gap 기술
- 체인 FAIL + 독립 PASS → 기준 과잉 가능성, 재검토 권고
- Layer 1 WARN만 있고 FAIL 없음 + Layer 2/3 PASS

CONDITIONAL PASS 시 반드시 `Missing evidence` 또는 `권고사항`을 명시한다.

### FAIL

아래 중 하나:

- Layer 1 오버라이드 해당
- 체인 PASS + 독립 FAIL (silent failure)
- 체인 PARTIAL + 독립 FAIL
- 체인 FAIL + 독립 FAIL
- 체인 FAIL + 독립 PARTIAL

## 체인 판정 해석

execution-review 점수로 체인 판정을 매핑한다:

| 점수 | 체인 판정 |
|------|----------|
| 15/15 pass | PASS |
| 11-14/15 pass | PARTIAL |
| 0-10/15 pass | FAIL |

점수가 없는 경우 (예: 텍스트 기반 판정만 있는 경우):
- "전체 pass", "모든 항목 pass" → PASS
- Gap이 있지만 경미 → PARTIAL
- 명시적 fail 또는 blocking gap → FAIL

## 독립 판정 해석

independent-verdict.md의 종합 판정을 그대로 사용:

| 독립 판정 | 의미 |
|-----------|------|
| PASS | 성공 기준 전체 충족 + 제약 위반 없음 |
| PARTIAL | 일부 기준 미충족 또는 경미한 제약 이슈 |
| FAIL | 핵심 기준 미충족 또는 중대한 제약 위반 |
