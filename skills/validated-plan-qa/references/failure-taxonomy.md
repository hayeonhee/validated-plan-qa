# Validated Plan QA Failure Taxonomy

## Layer 1 Failures

### 1. Chain Break
- 필수 산출물 누락
- slug 불일치 (디렉토리 ↔ 파일 헤더)
- gap 루프 파일 쌍 불일치

### 2. Manifest Staleness
- gap 보완 후 manifest 미갱신
- manifest에 적힌 파일이 이후 다시 수정됨
- worktree 변경이 manifest에 누락

### 3. Reference Disconnect
- clarify 성공 기준이 validation-v2에 매핑되지 않음
- meta-evaluation fail이 validation-v2에서 개선되지 않음
- plan-v1-review 수정 포인트가 plan-v2에 미반영

### 4. Criteria Weakening
- validation-v1 → v2에서 임계값 하향
- v1에 있던 기준이 v2에서 삭제
- v2 테스트셋의 fail 케이스가 v1보다 관대

### 5. Gap Loop Dishonesty
- fail → pass 전환인데 실제 파일 변경 없음
- 같은 output에 대해 해석만 변경하여 pass 처리
- gap-plan이 원래 Gap과 다른 내용을 수정

## Layer 2 Failures

### 6. Framing Contamination
- clarify 성공 기준을 달성했다고 체인이 판정했지만 독립 판정은 미달
- 체인의 프레이밍이 실제 의도를 왜곡
- 성공 기준 자체가 원래 의도를 제대로 포착하지 못함

### 7. Implicit Expectation Miss
- 명시적 기준은 충족했지만 당연히 기대되는 것이 빠짐
- 사용자 관점에서 "이것도 당연히 포함이지" 싶은 것이 없음

### 8. Scope Drift
- 최종 산출물에 의도와 무관한 것이 포함
- 요청하지 않은 기능/코드/문서가 추가
- 핵심 의도 대비 부수적인 것에 비중이 치우침

## Layer 3 Failures

### 9. Silent Failure (체인 PASS + 독립 FAIL)
- 가장 위험한 유형
- 체인의 내장 검증이 모두 통과했지만 실제 목표 미달
- 원인: 프레이밍 오염, 기준 약화, 앵커링

### 10. Overly Strict Chain (체인 FAIL + 독립 PASS)
- 실제로는 목표를 달성했지만 validation 기준이 과잉
- 기준 자체의 설계 문제
- gap 루프가 불필요하게 돌았을 수 있음
