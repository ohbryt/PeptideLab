# Peptide-as-a-Service (PaaS) MVP

## Vision
**亚太地区AI Biotech를 위한 합성 peptide 서비스**

- AI가 설계한 Peptide → 합성 → Assay → 데이터 반환
- 30-50% 저렴한 가격
- 2-4주 내 배송

---

## 서비스 구성

```
사용자 (AI Agent / 연구자)
         ↓
   API Gateway (주문)
         ↓
   Partner Lab (합성 + Assay)
         ↓
   데이터 반환 (S3/email)
```

---

## 서비스 종류 & 가격

### Peptide Synthesis
| 항목 | 단위 | 가격 | 시간 |
|------|------|------|------|
| Standard peptide | mg | ₩80,000 | 2-3주 |
| Modified (Ahx, pSer) | mg | ₩150,000 | 3-4주 |
| High purity (>95%) | mg | ₩200,000 | 3-4주 |
| Scale up (g) | g | ₩500,000+ | 4-6주 |

### Assays
| 항목 | 가격 | 시간 |
|------|------|------|
| HPLC purity | ₩50,000 | 3일 |
| Mass spec | ₩80,000 | 5일 |
| Binding (SPR) | ₩300,000 | 2주 |
| Cell-based | ₩500,000 | 3주 |
| ADMET panel | ₩800,000 | 4주 |

### Packages
| Package | 내용 | 가격 |
|---------|------|------|
| Basic | 합성 + HPLC | ₩250,000 |
| Standard | 합성 + HPLC + MS | ₩400,000 |
| Premium | 합성 + Full assay | ₩1,200,000 |

---

## 파트너 Lab (국내)

### 합성 파트너 (Anygen)
| 항목 | 내용 |
|------|------|
| **회사** | Anygen (에니젠) |
| **위치** | 한국 |
| **납기** | 2-3주 |
| **가격대** | ₩~100K/mg |
| **특징** | 한국 대표 Peptide 합성 회사 |

### Wet Validation 파트너 (BrownBiotech)
| 항목 | 내용 |
|------|------|
| **회사** | BrownBiotech |
| **위치** | Brown University / Korea |
| **서비스** | Cell-based assay, Binding, ADMET |
| **역할** | Peptide 효능/독성 검증 |

---

## API Design

### Endpoints

```bash
# 주문 생성
POST /api/v1/orders
{
  "sequence": "YGRKKRRQRRR-Ahx-DEEVSPSLLQ",
  "modifications": ["Ahx", "TFA"],
  "quantity": "50mg",
  "purity": ">95%",
  "assays": ["hplc", "ms"],
  "email": "user@research.kr"
}

# 주문 현황
GET /api/v1/orders/{order_id}

# 결과 다운로드
GET /api/v1/orders/{order_id}/results
```

### Response
```json
{
  "order_id": "PS-20260403-001",
  "status": "synthesizing",
  "estimated_delivery": "2026-04-17",
  "price": "₩400,000",
  "tracking_url": "https://..."
}
```

---

## 마케팅

### 타겟 고객
1. **AI Biotech** (韩, 日, 台, 新)
2. **Academia** (生命科学、化学)
3. **Pharma** (CRO, biotech)

### 차별화
- AI Agent 통합 (API-first)
- 한국산 품질, 중국 가격
- 영어/한국어/日本語 지원

---

## 로드맵

```
Q2 2026: MVP Launch
├── 파트너 Lab 계약 완료
├── API 개발 완료
└── 10개 테스트 주문

Q3 2026: Public Beta
├── 웹사이트 공개
├── 결제 시스템 연동
└── 50개 주문 목표

Q4 2026: Regional Expansion
├── Japan 사무소
├── Taiwan 파트너
└── $100K ARR
```

---

## 필요 자원

### 비용
| 항목 | 예상 비용 |
|------|----------|
| API 개발 | ₩5,000,000 |
| 마케팅 | ₩3,000,000 |
| 파트너 계약 | ₩2,000,000 |
| 운영 (6개월) | ₩10,000,000 |
| **Total** | ₩20,000,000 |

### 인건비
| 역할 | 인원 |
|------|------|
| Backend (FastAPI) | 1 |
| Operations (Lab coordination) | 1 |
| Sales/Marketing | 0.5 (兼業) |

---

## 다음 단계

- [ ] 파트너 Lab 견적 받기
- [ ] API 프로토타입 개발
- [ ] 웹사이트 ( Landing page)
- [ ] 계약서 준비 (MTA, NDA)

---

*Peptide-as-a-Service MVP Plan*
*Created: 2026-04-03*
