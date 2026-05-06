"""Mock 데이터 - 서울 주요 지역 위험/안전 데이터 (가상)

실제 서비스에서는 다음 공공 API로 대체:
[위험요인]
- 생활안전지도 (safemap.go.kr): 범죄 hotspot
- 도로교통공단 TAAS: 어린이 교통사고 다발지역
- 행정안전부: 침수 이력, 지반침하 데이터

[안전요인]
- 전국CCTV표준데이터: CCTV 설치 현황
- 경찰청: 경찰서/파출소/지구대 위치
- 아동안전지킴이집 정보 서비스: 지킴이집 위치
- 전국보안등정보표준데이터: 가로등/보안등
- 전국어린이보호구역표준데이터: 스쿨존
"""

from app.models.schemas import RiskPoint, RiskCategory, SafetyPoint, SafetyCategory


# ─── 범죄 위험 데이터 (성범죄 hotspot, 어린이 대상 범죄) ───
CRIME_RISKS: list[RiskPoint] = [
    # 강남/서초 지역
    RiskPoint(id="c-001", category=RiskCategory.CRIME, lat=37.5050, lng=127.0150,
              severity=4, label="성범죄 hotspot", description="반포동 일대 성범죄 발생 밀집지역 (최근 1년 3건)"),
    RiskPoint(id="c-002", category=RiskCategory.CRIME, lat=37.5120, lng=127.0200,
              severity=2, label="어린이 대상 범죄", description="반포초 인근 아동 대상 범죄 신고 이력"),
    RiskPoint(id="c-003", category=RiskCategory.CRIME, lat=37.5000, lng=127.0600,
              severity=3, label="성범죄 hotspot", description="대치동 학원가 인근 성범죄 발생지역"),
    RiskPoint(id="c-004", category=RiskCategory.CRIME, lat=37.4990, lng=127.1100,
              severity=2, label="어린이 대상 범죄", description="가락시장 인근 아동 대상 범죄 신고"),
    # 송파
    RiskPoint(id="c-005", category=RiskCategory.CRIME, lat=37.5140, lng=127.0900,
              severity=3, label="성범죄 hotspot", description="잠실역 일대 성범죄 밀집지역"),
    RiskPoint(id="c-006", category=RiskCategory.CRIME, lat=37.5200, lng=127.0850,
              severity=1, label="어린이 대상 범죄", description="잠실 초등학교 인근 신고 이력 (경미)"),
    # 강동
    RiskPoint(id="c-007", category=RiskCategory.CRIME, lat=37.5300, lng=127.1400,
              severity=4, label="성범죄 hotspot", description="둔촌역 인근 성범죄 다발지역"),
    RiskPoint(id="c-008", category=RiskCategory.CRIME, lat=37.5250, lng=127.1300,
              severity=3, label="어린이 대상 범죄", description="둔촌동 어린이공원 인근 범죄 신고"),
    # 마포
    RiskPoint(id="c-009", category=RiskCategory.CRIME, lat=37.5530, lng=126.9580,
              severity=2, label="어린이 대상 범죄", description="아현역 인근 아동 대상 범죄 신고"),
    # 금천
    RiskPoint(id="c-010", category=RiskCategory.CRIME, lat=37.4700, lng=126.9000,
              severity=4, label="성범죄 hotspot", description="독산동 성범죄 다발지역"),
    RiskPoint(id="c-011", category=RiskCategory.CRIME, lat=37.4650, lng=126.8950,
              severity=3, label="어린이 대상 범죄", description="독산초 인근 아동 범죄 다발"),
    # 은평
    RiskPoint(id="c-012", category=RiskCategory.CRIME, lat=37.5810, lng=126.8980,
              severity=2, label="성범죄 hotspot", description="수색역 인근 범죄 신고 이력"),
]


# ─── 교통 위험 데이터 (어린이 교통사고, 스쿨존 사고) ───
TRAFFIC_RISKS: list[RiskPoint] = [
    RiskPoint(id="t-001", category=RiskCategory.TRAFFIC, lat=37.5095, lng=127.0120,
              severity=3, label="스쿨존 사고", description="반포초등학교 스쿨존 교통사고 다발지점 (최근 2년 4건)"),
    RiskPoint(id="t-002", category=RiskCategory.TRAFFIC, lat=37.5060, lng=127.0180,
              severity=2, label="어린이 교통사고", description="반포대로 어린이 교통사고 발생 이력"),
    RiskPoint(id="t-003", category=RiskCategory.TRAFFIC, lat=37.4970, lng=127.1050,
              severity=4, label="어린이 교통사고", description="가락로 어린이 교통사고 다발지역 (최근 2년 7건)"),
    RiskPoint(id="t-004", category=RiskCategory.TRAFFIC, lat=37.5130, lng=127.0870,
              severity=3, label="스쿨존 사고", description="잠실초등학교 스쿨존 사고 발생"),
    RiskPoint(id="t-005", category=RiskCategory.TRAFFIC, lat=37.5020, lng=127.0560,
              severity=2, label="스쿨존 사고", description="대치초 스쿨존 교통사고 이력"),
    RiskPoint(id="t-006", category=RiskCategory.TRAFFIC, lat=37.5280, lng=127.1370,
              severity=3, label="어린이 교통사고", description="둔촌로 어린이 교통사고 다발"),
    RiskPoint(id="t-007", category=RiskCategory.TRAFFIC, lat=37.5520, lng=126.9540,
              severity=4, label="어린이 교통사고", description="아현역 교차로 어린이 사고 다발지점 (5건)"),
    RiskPoint(id="t-008", category=RiskCategory.TRAFFIC, lat=37.4690, lng=126.8960,
              severity=3, label="스쿨존 사고", description="독산초 스쿨존 사고 다발지점"),
    RiskPoint(id="t-009", category=RiskCategory.TRAFFIC, lat=37.5800, lng=126.8940,
              severity=2, label="어린이 교통사고", description="수색로 어린이 교통사고 이력"),
    RiskPoint(id="t-010", category=RiskCategory.TRAFFIC, lat=37.4830, lng=127.0520,
              severity=2, label="스쿨존 사고", description="개포초 스쿨존 교통사고 이력"),
]


# ─── 재난 위험 데이터 (침수, 지반침하) ───
DISASTER_RISKS: list[RiskPoint] = [
    RiskPoint(id="d-001", category=RiskCategory.DISASTER, lat=37.5090, lng=127.0140,
              severity=2, label="침수 이력", description="반포천 인근 2022년 집중호우 침수 피해 이력"),
    RiskPoint(id="d-002", category=RiskCategory.DISASTER, lat=37.4950, lng=127.1080,
              severity=4, label="침수 이력", description="석촌호수 인근 2022.08 집중호우 대규모 침수 (피해 심각)"),
    RiskPoint(id="d-003", category=RiskCategory.DISASTER, lat=37.4980, lng=127.1060,
              severity=3, label="지반침하", description="송파대로 지반침하(싱크홀) 발생 이력 (2023)"),
    RiskPoint(id="d-004", category=RiskCategory.DISASTER, lat=37.5100, lng=127.0880,
              severity=2, label="침수 이력", description="잠실 일대 2022년 침수 피해 이력"),
    RiskPoint(id="d-005", category=RiskCategory.DISASTER, lat=37.5540, lng=126.9550,
              severity=3, label="침수 이력", description="아현동 급경사지 집중호우 침수 이력 (2023)"),
    RiskPoint(id="d-006", category=RiskCategory.DISASTER, lat=37.5480, lng=126.9600,
              severity=2, label="지반침하", description="아현로 도로 지반침하 발생 이력"),
    RiskPoint(id="d-007", category=RiskCategory.DISASTER, lat=37.4670, lng=126.9010,
              severity=3, label="침수 이력", description="독산동 저지대 침수 이력 (2022, 2023)"),
    RiskPoint(id="d-008", category=RiskCategory.DISASTER, lat=37.5780, lng=126.8950,
              severity=4, label="침수 이력", description="수색동 홍제천 인근 침수 피해 이력 (2022.08 심각)"),
    RiskPoint(id="d-009", category=RiskCategory.DISASTER, lat=37.5260, lng=127.1320,
              severity=2, label="침수 이력", description="둔촌동 하수관 역류 침수 이력"),
    RiskPoint(id="d-010", category=RiskCategory.DISASTER, lat=37.4840, lng=127.0480,
              severity=1, label="지반침하", description="개포동 경미한 지반침하 이력"),
]


# ─── 안전 요인 데이터 ───

# CCTV 설치 현황
CCTV_SAFETIES: list[SafetyPoint] = [
    # 강남/서초 지역
    SafetyPoint(id="s-cctv-001", category=SafetyCategory.CCTV, lat=37.5060, lng=127.0170,
               effectiveness=4, label="범죄예방 CCTV", description="반포동 일대 CCTV 15대 설치 (범죄예방용)"),
    SafetyPoint(id="s-cctv-002", category=SafetyCategory.CCTV, lat=37.5010, lng=127.0620,
               effectiveness=5, label="스쿨존 CCTV", description="대치초 스쿨존 CCTV 8대 (어린이보호)"),
    SafetyPoint(id="s-cctv-003", category=SafetyCategory.CCTV, lat=37.4995, lng=127.1090,
               effectiveness=3, label="범죄예방 CCTV", description="가락시장 인근 CCTV 12대"),
    # 송파
    SafetyPoint(id="s-cctv-004", category=SafetyCategory.CCTV, lat=37.5150, lng=127.0890,
               effectiveness=4, label="범죄예방 CCTV", description="잠실역 일대 CCTV 20대"),
    # 구로
    SafetyPoint(id="s-cctv-005", category=SafetyCategory.CCTV, lat=37.4680, lng=126.8980,
               effectiveness=5, label="스쿨존 CCTV", description="독산초 스쿨존 CCTV 10대"),
]

# 경찰서/파출소
POLICE_SAFETIES: list[SafetyPoint] = [
    SafetyPoint(id="s-police-001", category=SafetyCategory.POLICE, lat=37.5070, lng=127.0160,
               effectiveness=5, label="파출소", description="반포파출소 - 24시간 운영"),
    SafetyPoint(id="s-police-002", category=SafetyCategory.POLICE, lat=37.5005, lng=127.0600,
               effectiveness=5, label="지구대", description="대치지구대"),
    SafetyPoint(id="s-police-003", category=SafetyCategory.POLICE, lat=37.5140, lng=127.0880,
               effectiveness=5, label="파출소", description="잠실파출소"),
    SafetyPoint(id="s-police-004", category=SafetyCategory.POLICE, lat=37.4690, lng=126.8970,
               effectiveness=5, label="지구대", description="독산지구대"),
]

# 아동안전지킴이집
SAFE_HOUSE_SAFETIES: list[SafetyPoint] = [
    SafetyPoint(id="s-house-001", category=SafetyCategory.SAFE_HOUSE, lat=37.5065, lng=127.0165,
               effectiveness=4, label="아동안전지킴이집", description="반포동 GS25 편의점"),
    SafetyPoint(id="s-house-002", category=SafetyCategory.SAFE_HOUSE, lat=37.5015, lng=127.0610,
               effectiveness=4, label="아동안전지킴이집", description="대치동 CU 편의점"),
    SafetyPoint(id="s-house-003", category=SafetyCategory.SAFE_HOUSE, lat=37.5145, lng=127.0885,
               effectiveness=4, label="아동안전지킴이집", description="잠실 세븐일레븐"),
    SafetyPoint(id="s-house-004", category=SafetyCategory.SAFE_HOUSE, lat=37.4685, lng=126.8975,
               effectiveness=4, label="아동안전지킴이집", description="독산동 미니스톱"),
]

# 가로등/보안등
STREET_LIGHT_SAFETIES: list[SafetyPoint] = [
    SafetyPoint(id="s-light-001", category=SafetyCategory.STREET_LIGHT, lat=37.5055, lng=127.0175,
               effectiveness=3, label="보안등", description="반포동 골목길 보안등 밀집구역 (30개)"),
    SafetyPoint(id="s-light-002", category=SafetyCategory.STREET_LIGHT, lat=37.5000, lng=127.0615,
               effectiveness=4, label="LED 가로등", description="대치동 학원가 LED 가로등 (50개)"),
    SafetyPoint(id="s-light-003", category=SafetyCategory.STREET_LIGHT, lat=37.5135, lng=127.0895,
               effectiveness=3, label="보안등", description="잠실 주택가 보안등 (25개)"),
    SafetyPoint(id="s-light-004", category=SafetyCategory.STREET_LIGHT, lat=37.4695, lng=126.8965,
               effectiveness=3, label="보안등", description="독산동 보안등 (20개)"),
]

# 어린이 보호구역 (스쿨존)
SCHOOL_ZONE_SAFETIES: list[SafetyPoint] = [
    SafetyPoint(id="s-zone-001", category=SafetyCategory.SCHOOL_ZONE, lat=37.5095, lng=127.0120,
               effectiveness=5, label="어린이보호구역", description="반포초등학교 스쿨존 - CCTV 8대, 신호등 3개"),
    SafetyPoint(id="s-zone-002", category=SafetyCategory.SCHOOL_ZONE, lat=37.5020, lng=127.0560,
               effectiveness=5, label="어린이보호구역", description="대치초등학교 스쿨존 - CCTV 10대"),
    SafetyPoint(id="s-zone-003", category=SafetyCategory.SCHOOL_ZONE, lat=37.5130, lng=127.0870,
               effectiveness=5, label="어린이보호구역", description="잠실초등학교 스쿨존 - CCTV 12대"),
    SafetyPoint(id="s-zone-004", category=SafetyCategory.SCHOOL_ZONE, lat=37.4690, lng=126.8960,
               effectiveness=5, label="어린이보호구역", description="독산초등학교 스쿨존 - CCTV 9대"),
]


def get_all_risks() -> list[RiskPoint]:
    """전체 위험 데이터 반환"""
    return CRIME_RISKS + TRAFFIC_RISKS + DISASTER_RISKS


def get_all_safeties() -> list[SafetyPoint]:
    """전체 안전 데이터 반환"""
    return (CCTV_SAFETIES + POLICE_SAFETIES + SAFE_HOUSE_SAFETIES +
            STREET_LIGHT_SAFETIES + SCHOOL_ZONE_SAFETIES)
