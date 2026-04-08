---
name: validated-plan-qa
description: >
  validated-plan 실행 결과 사후 감사. 3-layer 검증:
  Layer 1 (Chain Audit) 구조+의미 정합성,
  Layer 2 (Independent Verdict) 체인 우회 독립 판정,
  Layer 3 (Divergence Analysis) 체인 판정 vs 독립 판정 교차 검증.
  "validated-plan QA", "실행 끝난 거 QA" 요청에 사용.
---

# Validated Plan QA

validated-plan의 내장 검증(critic, meta-validation, gap 루프)이 **구조적으로 놓치는 것**을 잡는다.
내장 검증의 맹점: 프레이밍 오염, 점진적 앵커링, 기준 약화, 매니페스트 ≠ 실제.

## 3-Layer 아키텍처

```
              validated-plan 실행 완료
                      |
            +---------+---------+
            v         v         v
        Layer 1    Layer 2    Layer 3
      Chain Audit  Independent  Divergence
      (정합성)     Verdict      Analysis
                   (독립 판정)   (교차 검증)
            |         |         |
            +---------+---------+
                      v
                Final Report
```

## 사전 조건

- `.omc/plans/{task-slug}/` 디렉토리가 존재한다
- 최소한 `clarify-result.md`와 `execution-review.md`(또는 `execution-review-r{N}.md`)가 있다
- 프로젝트 루트를 식별할 수 있다

---

## Layer 1: Chain Audit (구조 + 의미 정합성)

orchestration-silent-failure-inspector의 구조 검사를 흡수하고, 의미 검사를 추가한다.

### 1-A. 스크립트 실행 (구조 검사)

```bash
python3 ~/.claude/skills/validated-plan-qa/scripts/audit_validated_plan_run.py .omc/plans/{task-slug} --repo-root .
```

스크립트가 검사하는 것:
- 필수 산출물 존재 + 비어있지 않음
- slug 일관성 (디렉토리 ↔ 파일 헤더)
- gap 루프 파일 쌍 정합성
- execution-manifest 변경파일/매핑/worktree 교차검증
- clarify-result 필수 섹션 존재
- plan-v2 Core 태그 + 수락 기준 존재

### 1-B. 의미 참조 검증 (에이전트가 직접 수행)

스크립트 결과를 확인한 뒤, 아래 5개 참조 연결을 **파일 내용을 읽어서** 검증한다.

| # | 생산자 | 소비자 | 확인 내용 |
|---|--------|--------|----------|
| R-1 | `clarify-result.md` 성공 기준 | `validation-v2.md` 결과 기준 | clarify 성공 기준 각각이 validation 기준에 매핑되는가 |
| R-2 | `meta-evaluation.md` fail 항목 | `validation-v2.md` v1→v2 변경점 | meta에서 fail된 것이 v2에서 실제로 개선됐는가 |
| R-3 | `plan-v1-review.md` 수정 포인트 | `plan-v2.md` Changelog | 리뷰 수정 포인트가 plan-v2에 반영됐는가 |
| R-4 | `validation-v1.md` 기준 | `validation-v2.md` 기준 | 기준이 **강화만** 됐는가, 약화된 건 없는가 |
| R-5 | `execution-review.md` Gap 목록 | `gap-plan-r1.md` | Gap이 있으면 보완 계획이 있는가, Gap 내용이 일치하는가 |

**R-4 (기준 약화 감지)가 핵심이다.** validation-v1에서 v2로 넘어갈 때, 또는 gap 루프에서 재검증할 때 기준을 느슨하게 재해석하면 false pass가 된다.

기준 약화 판정법:
- v1의 임계값이 v2에서 낮아졌는가 (예: "3개 이상" → "1개 이상")
- v1에 있던 기준이 v2에서 삭제됐는가
- v2 테스트셋의 fail 케이스가 v1보다 관대해졌는가

### 1-C. Gap 루프 정직성 검증

gap 루프가 있었다면 (execution-review-r1.md 등 존재):

1. `execution-review.md`에서 fail이던 항목을 추출
2. `execution-review-r1.md`에서 해당 항목의 판정을 확인
3. fail → pass로 바뀐 항목에 대해:
   - **output이 바뀌었는가** (실제 파일 변경이 있는가)
   - **해석이 바뀌었는가** (같은 output에 대해 판정만 바뀌었는가)
4. 해석만 바뀐 경우 → finding: "gap loop resolved by reinterpretation, not by improvement"

---

## Layer 2: Independent Verdict (독립 판정)

**이 Layer가 이 스킬의 존재 이유다.**

validated-plan의 모든 내장 검증은 같은 실행 컨텍스트를 공유하므로 프레이밍 오염에 취약하다.
Independent Verdict는 체인을 **완전히 우회**하고 원점에서 재판정한다.

### 실행 방법

```
Agent(subagent_type="oh-my-claudecode:critic", model="opus")
```

**이 agent에게 주는 것:**
- `clarify-result.md` (원래 의도)
- 최종 산출물 (execution-manifest.md에 나열된 실제 코드/파일)

**이 agent에게 주지 않는 것:**
- plan-v1.md, plan-v2.md
- validation-v1.md, validation-v2.md
- meta-evaluation.md
- execution-review.md, execution-review-r{N}.md
- plan-v1-review.md
- gap-plan-r{N}.md

**프롬프트:**

```
너는 이 프로젝트의 실행 과정을 전혀 모른다.
사용자의 원래 의도와 최종 결과물만 본다.

[clarify-result.md 경로]를 읽어라. 이것이 원래 의도다.
[execution-manifest.md에 나열된 실제 변경 파일 경로들]을 읽어라. 이것이 최종 결과물이다.

아래 3가지를 판정하라:

1. 명시적 성공 기준 충족
   clarify-result의 "성공 기준" 섹션의 각 항목에 대해:
   최종 결과물이 이 기준을 충족하는가? (PASS/FAIL + 근거)

2. 암묵적 기대 충족
   이 의도를 가진 사람이 당연히 기대하지만 명시하지 않은 것:
   충족되는가? (PASS/FAIL + 근거)
   항목이 없으면 "식별된 암묵적 기대 없음"

3. 과잉/이탈 산출물
   최종 결과물에서 의도와 무관하거나 과잉인 것:
   있는가? (목록 + 왜 과잉인지)
   없으면 "과잉 산출물 없음"

최종 독립 판정: PASS / PARTIAL / FAIL
```

**critic은 read-only이므로, 결과를 받은 후 오케스트레이터가** `.omc/plans/{task-slug}/independent-verdict.md`**에 저장한다.**

---

## Layer 3: Divergence Analysis (교차 검증)

Layer 1과 Layer 2 결과를 비교하여 최종 판정을 내린다.

### 입력

- 체인 판정: 최신 execution-review (execution-review.md 또는 execution-review-r{N}.md)
- 독립 판정: independent-verdict.md

### 판정 매트릭스

| 체인 판정 | 독립 판정 | 의미 | 최종 verdict |
|-----------|----------|------|-------------|
| PASS | PASS | 높은 신뢰도 | **PASS** |
| PASS | PARTIAL | 체인이 일부 놓침 | **CONDITIONAL PASS** — 독립 판정의 FAIL 항목 상세 기술 |
| PASS | FAIL | **Silent failure 확정** | **FAIL** — 체인이 놓친 것을 구체적으로 기술 |
| PARTIAL | PASS | 체인이 과잉 엄격 | **CONDITIONAL PASS** — 기준 재검토 권고 |
| PARTIAL | PARTIAL | 양쪽 모두 부족 인식 | **CONDITIONAL PASS** — 합집합 Gap 기술 |
| PARTIAL | FAIL | 실행 미완 | **FAIL** |
| FAIL | PASS | 체인 기준 오류 가능 | **CONDITIONAL PASS** — 기준 재검토 권고 |
| FAIL | FAIL | 실행 자체 실패 | **FAIL** |

### Layer 1 오버라이드

Layer 1에서 아래 중 하나라도 해당하면, Layer 2/3 결과와 무관하게 **FAIL**:
- 필수 산출물 누락
- gap 루프 파일 정합성 깨짐
- 기준 약화 감지
- gap 루프에서 해석만 변경하여 pass 처리

---

## 실행 순서

1. `task-slug`와 repo root를 식별한다
2. **Layer 1-A**: 스크립트 실행 → 구조 finding 수집
3. **Layer 1-B**: 5개 참조 연결을 파일 읽기로 검증 → 의미 finding 수집
4. **Layer 1-C**: gap 루프 정직성 검증 → finding 수집
5. Layer 1에 FAIL-grade finding이 있으면 → Layer 1 FAIL 보고 후 Layer 2로 계속 진행
6. **Layer 2**: Independent Verdict agent 스폰 → 독립 판정 수집
7. **Layer 3**: 체인 판정 vs 독립 판정 비교 → 최종 verdict 결정
8. Final Report 작성

Layer 1 FAIL이어도 Layer 2는 실행한다. 독립 판정은 체인 상태와 무관하게 가치가 있다.

---

## 보고 형식

```markdown
# Validated Plan QA: {task-slug}

## Layer 1: Chain Audit
### 구조 검사 (스크립트)
[스크립트 출력 요약]

### 의미 참조 검증
| # | 생산자 → 소비자 | 판정 | 근거 |
|---|----------------|------|------|

### Gap 루프 정직성
[해당 시 결과]

### Layer 1 종합: PASS / FAIL
[FAIL이면 finding 목록]

## Layer 2: Independent Verdict
### 명시적 성공 기준
| 기준 | 판정 | 근거 |

### 암묵적 기대
[결과]

### 과잉/이탈 산출물
[결과]

### 독립 판정: PASS / PARTIAL / FAIL

## Layer 3: Divergence Analysis
- 체인 판정: [PASS/PARTIAL/FAIL]
- 독립 판정: [PASS/PARTIAL/FAIL]
- 일치 여부: [일치 / 불일치]
- 불일치 시 분석: [체인이 놓친 것 / 체인이 과잉인 것]

## Final Verdict: PASS / CONDITIONAL PASS / FAIL
- [verdict 근거 1-2문장]
- [CONDITIONAL이면 missing evidence / 권고사항]
- [FAIL이면 blocking finding 목록]
```

---

## 참조 문서

- 체크리스트: [references/checklist.md](references/checklist.md)
- 실패 taxonomy: [references/failure-taxonomy.md](references/failure-taxonomy.md)
- verdict 규칙: [references/verdict-rules.md](references/verdict-rules.md)
