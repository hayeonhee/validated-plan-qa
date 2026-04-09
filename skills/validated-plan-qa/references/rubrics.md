# Rubrics

Layer 1-B(의미 참조 검증), Layer 1-C(gap 루프 정직성), Layer 2(독립 판정) 각각의 PASS/FAIL/WARN 판정 기준.

## 운영 규칙

- 같은 항목에서 같은 교훈이 3회 반복되면 해당 항목의 규칙에 반영한다
- 반영 후 해당 사례는 삭제한다
- 사례 기록은 Layer 3 Divergence Analysis에서 불일치 발견 시 수행한다

---

## R-1: clarify 성공 기준 → validation-v2 결과 기준

### 규칙

- **PASS (해당 없음)**: clarify-result에 성공 기준 섹션이 없거나 항목이 없다
- **PASS**: 모든 성공 기준이 validation-v2에 동일하거나 더 구체적인 기준으로 1:1 대응된다
- **FAIL**: 성공 기준 중 하나라도 validation-v2에 대응 항목 없이 누락됐다
- **WARN**: 대응은 있으나 추상화 수준이 달라 매핑 충분성이 애매하다 (예: "사용성 개선" → "버튼 색 변경")

### R-1b: execution-review 통합 경로 검증 (R-1 PASS 시에만)

R-1이 "기준이 존재하는가"를 확인한다면, R-1b는 "그 기준으로 pass된 판정이 통합 경로를 검증했는가"를 확인한다.

- **PASS**: execution-review의 각 pass 항목이 통합 경로(API→DB→UI 또는 해당 기능의 전체 데이터 흐름)를 근거로 판정했다
- **FAIL**: pass 항목 중 하나라도 단위 수준(함수 존재, 타입 일치 등)만으로 판정되고, 실제 연결(import, 호출, 렌더링)이 미검증이다
- **WARN**: 통합 경로 검증이 명시적이지 않으나, 산출물 코드에서 연결이 자명하게 추론된다

검증 방법: execution-review에서 pass된 각 항목의 "근거" 컬럼을 읽고, 그 근거가 (1) 실제 파일 간 import/호출 관계를 포함하는지, (2) API 응답이 UI까지 전달되는 경로를 포함하는지, (3) 프론트엔드가 호출하는 API 엔드포인트의 라우트 파일이 실제로 존재하는지, (4) 여러 API가 같은 데이터를 다루는 경우 키/스키마가 일치하는지 확인한다.

**API 간 정합성 검증 (R-1b-cross)**:
- 프론트에서 `fetch('/api/...')` 호출이 있으면, 해당 라우트 파일 존재를 확인한다
- 같은 도메인 데이터를 읽는 API(GET)와 쓰는 API(POST/PUT)가 있으면, 키/필드 목록이 일치하는지 교차 확인한다
- 불일치 시 FAIL (예: GET이 2개 키, POST가 4개 키 → 저장 항상 실패)

> **승격 근거**: MISSED-2026-04-09-001. coach-view-notification-ux에서 CompanyAlias DB 조회가 notifications route에서 누락(null 하드코딩), CompanyAliasManager가 mypage에 미연결(import 0건)이었으나, execution-review는 "함수 존재"만으로 pass 처리. coach-schedule-metrics에서도 추이 차트, weeklyTrend가 plan에 설계됐으나 미구현, 채널 키 불일치 버그를 체인이 놓침.

### 사례

(Layer 3 불일치 시 추가)

---

## R-2: meta-evaluation fail 항목 → validation-v2 개선

### 규칙

- **PASS (해당 없음)**: meta-evaluation에 fail 항목이 없다
- **PASS**: 모든 fail 항목이 validation-v2에서 개선된 기준이나 보완 조치로 반영됐다
- **FAIL**: fail 항목 중 하나라도 validation-v2에서 개선 없이 무시됐다
- **WARN**: 반영은 됐으나 개선 정도가 충분한지 판단이 애매하다

### 사례

(Layer 3 불일치 시 추가)

---

## R-3: plan-v1-review 수정 포인트 → plan-v2 반영

### 규칙

- **PASS (해당 없음)**: plan-v1-review에 수정 포인트가 없다
- **PASS**: 모든 수정 포인트가 plan-v2 Changelog 또는 본문에 반영됐다
- **FAIL**: 수정 포인트 중 하나라도 plan-v2에 반영 없이 누락됐다
- **WARN**: 반영은 됐으나 수정 포인트의 의도와 다르게 반영된 것 같다

### 사례

(Layer 3 불일치 시 추가)

---

## R-4: validation-v1 기준 → validation-v2 기준 약화 감지

### 규칙

- **PASS**: 모든 기준이 v1과 동일하거나 더 엄격해졌다
- **FAIL**: v1에 있던 기준이 v2에서 삭제됐다
- **FAIL**: v1의 임계값이 v2에서 낮아졌다 (예: "3개 이상" → "1개 이상", "80%" → "60%")
- **WARN**: 기준 표현이 바뀌어서 강화/약화 판단이 애매하다 (예: "빠른 응답" → "적절한 응답")

### 사례

(Layer 3 불일치 시 추가)

---

## R-5: execution-review Gap 목록 → gap-plan 대응

### 규칙

- **PASS (해당 없음)**: execution-review에 Gap이 없거나 "전체 pass"다
- **PASS**: 모든 Gap 항목이 gap-plan에 보완 계획으로 대응됐다
- **FAIL**: Gap 항목 중 하나라도 gap-plan에 대응 계획 없이 누락됐다
- **FAIL**: gap-plan의 보완 내용이 Gap과 무관한 다른 것을 수정한다
- **WARN**: 대응은 있으나 보완 범위가 Gap을 충분히 해소하는지 애매하다

### 사례

(Layer 3 불일치 시 추가)

---

## Layer 1-C: gap 루프 정직성

### 규칙

- **PASS (해당 없음)**: gap 루프가 돌지 않았다 (execution-review-r{N} 파일 없음)
- **PASS (해당 없음)**: gap 루프에서 fail → pass 전환 항목이 없다
- **PASS**: fail → pass 전환된 모든 항목에서 실제 파일 변경이 확인된다
- **FAIL**: fail → pass 전환됐는데 관련 파일 변경이 없다 (해석만 바꿔서 pass 처리)
- **WARN**: 파일 변경은 있으나 해당 기준과의 관련성이 애매하다

### 사례

(Layer 3 불일치 시 추가)

---

## Layer 2: 독립 판정

### 규칙

- **PASS**: clarify-result의 명시적 성공 기준 전부 충족 + 근거 있음 + 제약 위반 없음
- **PARTIAL**: 일부 성공 기준 미충족이지만 핵심 기능에 영향 없음, 또는 경미한 제약 이슈
- **FAIL**: 핵심 성공 기준 1개 이상 미충족, 또는 중대한 제약 위반
- **WARN 해당 없음**: Layer 2는 PASS/PARTIAL/FAIL 3단계만 사용한다

### 사례

(Layer 3 불일치 시 추가)
