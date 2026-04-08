# Validated Plan QA Checklist

## Layer 1: Chain Audit

### A. 구조 검사 (스크립트)

- [ ] `clarify-result.md`부터 최신 review까지 필수 파일이 존재한다
- [ ] 파일 헤더의 slug와 디렉토리 slug가 일치한다
- [ ] gap 루프 파일 쌍이 맞는다 (gap-plan-r{N} ↔ execution-review-r{N})
- [ ] `execution-manifest.md`에 변경 파일 목록과 Step 매핑이 있다
- [ ] 매핑된 파일이 실제로 존재한다
- [ ] worktree 변경 파일 중 manifest에 없는 항목이 없다
- [ ] clarify-result에 목표/이유/성공 기준/제약 섹션이 있다
- [ ] plan-v2에 [Core] 태그와 수락 기준이 있다

### B. 의미 참조 검증 (에이전트)

- [ ] R-1: clarify 성공 기준 → validation-v2 결과 기준 매핑 확인
- [ ] R-2: meta-evaluation fail 항목 → validation-v2 개선 확인
- [ ] R-3: plan-v1-review 수정 포인트 → plan-v2 Changelog 반영 확인
- [ ] R-4: validation-v1 → v2 기준 약화 없음 확인
- [ ] R-5: execution-review Gap → gap-plan 대응 확인

### C. Gap 루프 정직성 (해당 시)

- [ ] fail → pass 전환 항목에서 실제 파일 변경이 있었는가
- [ ] 파일 변경 없이 해석만 바뀐 항목이 없는가

## Layer 2: Independent Verdict

- [ ] critic에게 clarify-result + 최종 산출물만 전달 (중간 체인 제외)
- [ ] 명시적 성공 기준 각각에 대해 PASS/FAIL 판정
- [ ] 명시된 제약 위반 여부 확인
- [ ] 암묵적 기대 식별 및 충족 여부
- [ ] 과잉/이탈 산출물 식별
- [ ] 종합 독립 판정: PASS / PARTIAL / FAIL

## Layer 3: Divergence Analysis

- [ ] 체인 판정 (최신 execution-review 점수) 추출
- [ ] 독립 판정 (independent-verdict.md) 추출
- [ ] 교차 매트릭스로 최종 verdict 결정
- [ ] 불일치 시 구체적 분석 (체인이 놓친 것 / 체인이 과잉인 것)
- [ ] Layer 1 오버라이드 해당 여부 확인

## Final Report

- [ ] 3 Layer 결과 모두 포함
- [ ] findings 심각도 순 정렬
- [ ] Final Verdict: PASS / CONDITIONAL PASS / FAIL
- [ ] CONDITIONAL이면 missing evidence 명시
- [ ] FAIL이면 blocking finding 목록
