# Gap Plan Round 1: test-auth-api

## 보완 대상
- 토큰 갱신 시 기존 토큰 무효화 로직 추가

## 보완 방법
- src/auth/refresh.ts에 기존 토큰 블랙리스트 로직 추가
