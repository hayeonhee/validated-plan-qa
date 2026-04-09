# Validation v2: test-auth-api

## 검증 기준
1. JWT 토큰 발급 API가 정상 동작하는가
2. 토큰 검증 미들웨어가 유효/무효 토큰을 구분하는가
3. 만료 토큰 갱신 API가 정상 동작하는가
4. 토큰 발급 시 rate limiting이 적용되는가 (강화)

## v1→v2 변경점
- 기준 4 추가 (rate limiting, 강화)
