# K-Democracy — 고팡 AI 민주주의

> **democracy.hondi.net** | [hondi.net](https://hondi.net) | [K-Law](https://klaw.hondi.net)

고팡(Gopang) AI 평행 세계의 입법 시스템입니다.  
누구나 안건을 제안하고, 공헌도에 비례한 의결권으로 결정하며, 결과는 OpenHash에 영구 기록됩니다.

---

## 파일 구조

| 파일 | 설명 |
|------|------|
| `index.html` | 진입점 |
| `desktop.html` | K-Democracy 메인 UI |
| `webapp.html` | 모바일 UI |
| `pdv.js` | PDV(Private Data Vault) 연동 스크립트 |
| `gopang_laws.html` | 고팡 평행 법전 — 원칙·민사규칙·형사규칙 |
| `ai_democracy_sp.html` | AI 민주주의 System Prompt 전집 (HTML) |
| `ai_democracy_system_prompts.md` | AI 민주주의 System Prompt 전집 (Markdown) |

---

## AI 민주주의 파이프라인

```
시민 제안 → 1,000표 동의
    ↓
SP-01 사용자 DB 구성 (PDV 공개 데이터)
    ↓
SP-02 안건 분류 · SP-03 심사위원단 선발
    ↓
SP-04 찬성발의단 ‖ SP-05 반대심사단  ← 상호 차단
    ↓
SP-06 심의위원회 (DeepSeek V4 Pro)
    ↓
SP-07 교차 검증 (Claude Opus)
    ↓
SP-08 인간 심사위원단 최종 결정
    ↓
OpenHash 앵커링 → 즉시 시행
```

---

## 고팡 평행 법전

| 법전 | 현실 대응 | 조문 수 |
|------|-----------|---------|
| 원칙 | 헌법 | 17조 |
| 민사규칙 | 민법 | 18조 |
| 형사규칙 | 형법 | 30조 |

> 고팡의 원칙과 규칙은 현실 세계의 헌법 및 법률에 종속됩니다.

---

## 기술 스택

- **OpenHash** — SHA-256 기반 5계층 분산원장 (L1 읍면동 ~ L5 글로벌)
- **PDV** — 사용자 기기 암호화 저장, 서버 무저장
- **GDC** — Gopang Digital Currency (₮), 수수료 0%
- **K-Law** — 법적 감시 AI, 30초 쿨다운 백그라운드 모니터
- **DAWN** — Democracy is All We Need

---

## 라이선스

**GPL v3.0** · © 2026 AI City Inc. (비영리)  
모든 소스코드와 System Prompt는 공개됩니다.

```
tensor.city@gmail.com · github.com/Openhash-Gopang
```
