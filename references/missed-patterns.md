# Missed Patterns Registry

validated-plan-qa 3-Layer 감사가 놓친 문제를 사후에 기록하는 cross-session 저장소.

## 목적

- QA가 PASS/CONDITIONAL PASS를 줬는데, 나중에 실제 문제가 발견된 경우를 기록
- 패턴이 축적되면 pattern-analyst가 분석하여 규칙 승격 후보를 식별
- 1회성 사례는 기록만 하고 즉시 규칙화하지 않음

## Intake 트리거

아래 상황에서 이 파일에 엔트리를 추가한다:

1. **사용자 보고**: "이전 QA에서 놓친 게 있었다", "이거 QA 통과했는데 문제 있다"
2. **후속 작업 중 발견**: 이전 validated-plan의 산출물을 사용하다가 결함 발견
3. **프로덕션 이슈**: QA PASS된 코드에서 실제 버그/장애 발생
4. **다른 리뷰어 지적**: code review, PR review 등에서 QA가 놓친 문제 식별

기록 주체: 문제를 발견한 세션의 오케스트레이터가 즉시 기록한다.
기록 시점: 발견 즉시. 나중에 정리하려 하면 맥락을 잃는다.

## 엔트리 형식

```markdown
### MISSED-{YYYY-MM-DD}-{순번}

- **발견일**: YYYY-MM-DD
- **원래 task-slug**: QA를 수행했던 태스크
- **QA verdict**: 당시 최종 판정 (PASS / CONDITIONAL PASS)
- **놓친 내용**: 무엇이 누락/오판됐는지 (구체적으로)
- **잡았어야 할 Layer**: Layer 1 / Layer 2 / Layer 3
- **기존 규칙 중 관련된 것**: checklist/taxonomy 중 어떤 항목이 관련되는지 (없으면 "해당 규칙 없음")
- **왜 못 잡았는지**: [아래 3가지 중 택1]
  - 규칙 자체가 없었음 (coverage gap)
  - 규칙은 있었으나 적용되지 않음 (execution gap)
  - 규칙이 적용됐으나 판정이 틀림 (judgment gap)
- **심각도**: Critical / Major / Minor
- **승격 후보 여부**: Yes / No / 판단 보류
```

## 기록 원칙

1. "왜 못 잡았는지"가 가장 중요한 필드다 — 패턴 분석의 핵심 입력
2. 1회성 사례도 기록은 한다 — 승격 여부는 나중에 판단
3. 발견자가 승격 여부를 확정하지 않는다 — 별도 분석 단계에서 결정
4. 기존 엔트리와 유사하면 별도 엔트리로 기록하되 관련 엔트리 ID를 참조한다

---

## 로그

(엔트리가 아래에 시간순으로 추가됨)
