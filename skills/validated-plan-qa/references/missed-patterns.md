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

### MISSED-2026-04-09-001

- **발견일**: 2026-04-09
- **원래 task-slug**: coach-view-notification-ux
- **QA verdict**: FAIL (이번 QA에서 발견됨 — 체인은 PASS였으나 독립 판정이 잡음)
- **놓친 내용**: 체인 검증(execution-review)은 "Plan v2 대비 구현 일치"만 확인함. Plan v2가 clarify 원래 의도에서 이탈했거나, Plan에 명시된 기능이 연결 없이 dead code로 구현된 경우를 잡지 못함. 구체적으로: CompanyAlias DB 조회가 notifications route에서 누락(companyAlias: null 하드코딩), CompanyAliasManager가 mypage에 미연결(import 0건).
- **잡았어야 할 Layer**: Layer 1 (체인 자체의 구조적 한계) + Layer 2 (독립 판정이 잡음)
- **기존 규칙 중 관련된 것**: R-1 (clarify → validation 매핑)은 "기준이 존재하는지"만 확인하고, "기준이 실제로 통합 경로를 검증하는지"는 확인하지 않음
- **왜 못 잡았는지**: 규칙 자체가 없었음 (coverage gap) — execution-review가 단위 함수 테스트 pass를 통합 경로 pass로 잘못 판정하는 것을 감지하는 규칙이 없음. R-1은 기준 존재 여부만 확인하고, 기준의 검증 범위(단위 vs 통합)는 검사하지 않음.
- **심각도**: Critical
- **승격 후보 여부**: Yes — "execution-review에서 pass된 항목이 단위 테스트만으로 판정된 것인지, 통합 경로(API→DB→UI)를 포함하는지 확인" 규칙 추가 후보
- **반복 사례**:
  - 2026-04-09 coach-schedule-metrics (CONDITIONAL PASS): execution-review 15/15 pass였으나, 독립 판정에서 (1) plan-v2에 설계된 추이 차트(4개 지표 중첩 라인 차트)와 weeklyTrend가 미구현, (2) summary API channelKeys 2개 vs POST API CHANNEL_KEYS 4개 불일치로 저장 항상 실패하는 버그, (3) 과잉 산출물(삼전 현황, 일정 제공 비율) 발견. 체인은 "Plan v2 대비 구현 일치"만 확인하고, "Clarify 성공 기준 대비 구현"과 "API 간 정합성"을 검증하지 않음.
  - **2026-04-09 추가 발견**: 실제로는 channelKeys 불일치보다 심각 — `POST /api/admin/metrics/external-hire` 라우트 파일 자체가 존재하지 않았음. execution-manifest.md에 "src/app/api/admin/metrics/external-hire/route.ts (신규) — 완료"로 기록되어 있었으나 파일이 없음. audit 스크립트가 WARN만 냈고 FAIL로 잡지 못함.
  - **후속 조치 방치**: CONDITIONAL PASS + Blocking Bug 판정이 나왔으나 수정 프로세스 없이 방치됨. 2026-04-09에 API 신규 생성으로 해소.
  - **규칙 승격 완료 (2026-04-09)**:
    1. audit 스크립트: 신규 파일 미존재 시 WARN → FAIL 승격
    2. rubrics R-1b: API 간 정합성 교차 검증(R-1b-cross) 규칙 추가
    3. QA SKILL.md: CONDITIONAL PASS 해소 루프 추가

### MISSED-2026-04-09-002

- **발견일**: 2026-04-09
- **원래 task-slug**: mypage-scouting-review (CONDITIONAL PASS) ← course-centric-scouting에 의해 회귀
- **QA verdict**: CONDITIONAL PASS (체인 PASS, 독립 PARTIAL)
- **놓친 내용**: 같은 파일을 수정하는 복수 plan 간 교차 회귀를 추적하는 메커니즘이 없음. plan A가 파일 X를 수정하고, 이후 plan B가 같은 파일 X를 수정하면, plan A의 구현이 회귀될 수 있으나, 각 plan의 QA는 자기 plan 범위만 검증함.
- **잡았어야 할 Layer**: Layer 1 (구조 검사 스크립트가 cross-plan 파일 충돌을 감지해야 함)
- **기존 규칙 중 관련된 것**: 해당 규칙 없음 — 현재 QA는 단일 plan 범위 내에서만 동작
- **왜 못 잡았는지**: 규칙 자체가 없었음 (coverage gap) — 단일 plan 격리 검증 설계. cross-plan regression 추적 메커니즘 부재.
- **심각도**: Major
- **승격 후보 여부**: Yes — execution-manifest의 변경 파일 목록을 다른 plan의 manifest와 교차 비교하는 스크립트 확장 후보
- **구체적 사례**:
  - mypage-scouting-review가 `mypage/page.tsx`에 (1) ConfirmModal 연결 (확정→수정 UI), (2) '일련의 과정' placeholder 영역을 추가. 이후 course-centric-scouting이 같은 파일을 전면 리팩터(ScoutingTab + CourseTab 분리)하면서 두 가지 모두 누락. 결과: ConfirmModal 데드 코드화(확정→수정 불가, scheduleText 미기록), placeholder 소실.
  - 두 plan 모두 execution-review PASS였으나, 각각 자기 plan 범위만 검증했으므로 교차 회귀를 감지하지 못함.
