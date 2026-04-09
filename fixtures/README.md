# Test Fixtures

rubric 검증용 모의고사 세트. 답을 미리 알고 있는 가짜 plan 산출물.

## 케이스별 기대 결과

### case-01-clean
결함 없음. 모든 검사가 정상이어야 한다.
- R-1~R-5: 전부 PASS
- Layer 1-C: PASS (해당 없음)
- Layer 2: PASS
- 스크립트: WARN만 (manifest 파일 미존재는 fixture 한계)

### case-02-criteria-weakened
validation-v1에 있던 "커버리지 80% 이상"이 validation-v2에서 삭제됨.
- **R-4: FAIL** — 기준 삭제 감지
- R-1: PASS (clarify 성공기준 3개가 validation-v2에 3개 매핑)
- 나머지: PASS

### case-03-gap-dishonesty
execution-review에서 기준3 FAIL → gap-plan-r1 작성 → execution-review-r1에서 PASS. 그런데 파일 변경 없이 "다시 보니 충분함"으로 해석만 바꿈.
- **Layer 1-C: FAIL** — 파일 변경 없이 해석만 바꿔서 pass 처리
- R-5: PASS (gap-plan이 gap에 대응함)
- 나머지: PASS

### case-04-criteria-missing
clarify 성공기준 3개인데 validation-v2에 2개만 있음. "토큰 갱신" 기준이 누락.
- **R-1: FAIL** — 성공기준 누락
- R-4: FAIL — v1 기준 3개에서 v2 기준 2개로 삭제
- 나머지: PASS

### case-05-review-ignored
plan-v1-review에 수정 포인트 2개(에러 핸들링, 감사 로깅)가 있는데 plan-v2 Changelog에 반영 안 됨.
- **R-3: FAIL** — 리뷰 수정 포인트 미반영
- 나머지: PASS

### case-06-no-issues
모든 것이 깨끗함. meta-evaluation 전체 PASS, 리뷰 수정 포인트 없음, gap 없음.
- R-1~R-5: 전부 PASS (R-2, R-3, R-5는 "해당 없음" PASS)
- Layer 1-C: PASS (해당 없음)
- Layer 2: PASS

## 참고

- fixture에서 manifest가 참조하는 소스 파일(src/auth/*.ts)은 실제로 존재하지 않음
- 스크립트 실행 시 해당 파일 미존재 WARN은 fixture 한계이므로 무시
