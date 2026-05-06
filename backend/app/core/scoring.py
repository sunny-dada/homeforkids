"""점수 계산 엔진 - 우리아이살집

## 알고리즘 설명

아이 안전 점수 = 100 - (범죄위험 × 0.4 + 교통위험 × 0.3 + 재난위험 × 0.3)

각 카테고리 위험 점수(0~100) 계산:
  1. 반경 내 위험 지점 필터링
  2. 밀도 점수: min(hotspot_count / 기준값, 1.0) × 50
  3. 심각도 점수: (평균 severity / 5) × 50
  4. 위험 점수 = 밀도 점수 + 심각도 점수

설계 원칙:
- Explainable: 각 카테고리별 점수를 분리하여 "왜 이 점수인지" 설명 가능
- 단순: 선형 가중합으로 구성하여 이해하기 쉬움
"""

import math

from urllib.parse import quote

from app.models.schemas import (
    RiskPoint,
    RiskCategory,
    CategoryScore,
    SubcategoryDetail,
    RiskFactor,
    SafetyPoint,
    SafetyCategory,
    SafetyCategoryScore,
    SafetyFactor,
    SourceLink,
    SafetyGrade,
)


# ─── 가중치 ───
WEIGHTS: dict[RiskCategory, float] = {
    RiskCategory.CRIME: 0.4,
    RiskCategory.TRAFFIC: 0.3,
    RiskCategory.DISASTER: 0.3,
}

# 밀도 기준값: 이 개수 이상이면 밀도 점수 최대
DENSITY_THRESHOLD: dict[RiskCategory, int] = {
    RiskCategory.CRIME: 3,
    RiskCategory.TRAFFIC: 4,
    RiskCategory.DISASTER: 3,
}

CATEGORY_LABELS: dict[RiskCategory, str] = {
    RiskCategory.CRIME: "범죄 위험",
    RiskCategory.TRAFFIC: "교통 위험",
    RiskCategory.DISASTER: "재난 위험",
}

CATEGORY_ICONS: dict[RiskCategory, str] = {
    RiskCategory.CRIME: "shield-alert",
    RiskCategory.TRAFFIC: "car",
    RiskCategory.DISASTER: "cloud-rain",
}

# ─── 안전요인 가중치 & 라벨 ───
SAFETY_WEIGHTS: dict[SafetyCategory, float] = {
    SafetyCategory.CCTV: 0.25,
    SafetyCategory.POLICE: 0.25,
    SafetyCategory.SAFE_HOUSE: 0.2,
    SafetyCategory.STREET_LIGHT: 0.15,
    SafetyCategory.SCHOOL_ZONE: 0.15,
}

# 밀도 기준값: 이 개수 이상이면 밀도 점수 최대
SAFETY_DENSITY_THRESHOLD: dict[SafetyCategory, int] = {
    SafetyCategory.CCTV: 5,
    SafetyCategory.POLICE: 2,
    SafetyCategory.SAFE_HOUSE: 3,
    SafetyCategory.STREET_LIGHT: 4,
    SafetyCategory.SCHOOL_ZONE: 2,
}

SAFETY_CATEGORY_LABELS: dict[SafetyCategory, str] = {
    SafetyCategory.CCTV: "CCTV 설치",
    SafetyCategory.POLICE: "치안 시설",
    SafetyCategory.SAFE_HOUSE: "안전지킴이집",
    SafetyCategory.STREET_LIGHT: "가로등/보안등",
    SafetyCategory.SCHOOL_ZONE: "어린이보호구역",
}

SAFETY_CATEGORY_ICONS: dict[SafetyCategory, str] = {
    SafetyCategory.CCTV: "camera",
    SafetyCategory.POLICE: "shield",
    SafetyCategory.SAFE_HOUSE: "home",
    SafetyCategory.STREET_LIGHT: "lightbulb",
    SafetyCategory.SCHOOL_ZONE: "flag",
}


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 간 거리(m) 계산 - Haversine 공식"""
    R = 6371000  # 지구 반지름 (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def filter_nearby_risks(
    risks: list[RiskPoint],
    lat: float,
    lng: float,
    radius: int,
) -> list[RiskPoint]:
    """반경 내 위험 지점만 필터링"""
    nearby = []
    for risk in risks:
        dist = haversine_distance(lat, lng, risk.lat, risk.lng)
        if dist <= radius:
            nearby.append(risk)
    return nearby


def filter_nearby_safeties(
    safeties: list[SafetyPoint],
    lat: float,
    lng: float,
    radius: int,
) -> list[SafetyPoint]:
    """반경 내 안전 지점만 필터링"""
    nearby = []
    for safety in safeties:
        dist = haversine_distance(lat, lng, safety.lat, safety.lng)
        if dist <= radius:
            nearby.append(safety)
    return nearby


def calculate_category_score(
    risks: list[RiskPoint],
    category: RiskCategory,
) -> CategoryScore:
    """카테고리별 위험 점수 계산 (0~100)

    공식:
      밀도 점수 = min(hotspot_count / threshold, 1.0) × 50
      심각도 점수 = (avg_severity / 5) × 50
      위험 점수 = 밀도 점수 + 심각도 점수
    """
    category_risks = [r for r in risks if r.category == category]
    count = len(category_risks)
    threshold = DENSITY_THRESHOLD[category]
    weight = WEIGHTS[category]

    if count == 0:
        return CategoryScore(
            category=category,
            raw_score=0,
            weight=weight,
            weighted_score=0,
            hotspot_count=0,
            avg_severity=0,
            detail=f"반경 내 {CATEGORY_LABELS[category]} 요인 없음",
            subcategories=[],
        )

    # 세부 유형별 집계
    subcategory_map: dict[str, list[RiskPoint]] = {}
    for risk in category_risks:
        if risk.label not in subcategory_map:
            subcategory_map[risk.label] = []
        subcategory_map[risk.label].append(risk)

    subcategories = [
        SubcategoryDetail(
            label=label,
            count=len(sub_risks),
            avg_severity=round(sum(r.severity for r in sub_risks) / len(sub_risks), 1),
        )
        for label, sub_risks in subcategory_map.items()
    ]
    # 개수 내림차순 정렬
    subcategories.sort(key=lambda x: x.count, reverse=True)

    avg_severity = sum(r.severity for r in category_risks) / count
    density_score = min(count / threshold, 1.0) * 50
    severity_score = (avg_severity / 5) * 50
    raw_score = round(density_score + severity_score, 1)
    raw_score = min(raw_score, 100)

    detail = f"{CATEGORY_LABELS[category]}: {count}건 탐지, 평균 위험도 {avg_severity:.1f}/5"

    return CategoryScore(
        category=category,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 1),
        hotspot_count=count,
        avg_severity=round(avg_severity, 1),
        detail=detail,
        subcategories=subcategories,
    )


def calculate_safety_category_score(
    safeties: list[SafetyPoint],
    category: SafetyCategory,
) -> SafetyCategoryScore:
    """카테고리별 안전 점수 계산 (0~100)

    공식:
      밀도 점수 = min(facility_count / threshold, 1.0) × 50
      효과성 점수 = (avg_effectiveness / 5) × 50
      안전 점수 = 밀도 점수 + 효과성 점수
    """
    category_safeties = [s for s in safeties if s.category == category]
    count = len(category_safeties)
    threshold = SAFETY_DENSITY_THRESHOLD[category]
    weight = SAFETY_WEIGHTS[category]

    if count == 0:
        return SafetyCategoryScore(
            category=category,
            raw_score=0,
            weight=weight,
            weighted_score=0,
            facility_count=0,
            avg_effectiveness=0,
            detail=f"반경 내 {SAFETY_CATEGORY_LABELS[category]} 없음",
        )

    avg_effectiveness = sum(s.effectiveness for s in category_safeties) / count
    density_score = min(count / threshold, 1.0) * 50
    effectiveness_score = (avg_effectiveness / 5) * 50
    raw_score = round(density_score + effectiveness_score, 1)
    raw_score = min(raw_score, 100)

    detail = f"{SAFETY_CATEGORY_LABELS[category]}: {count}개 설치, 평균 효과 {avg_effectiveness:.1f}/5"

    return SafetyCategoryScore(
        category=category,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 1),
        facility_count=count,
        avg_effectiveness=round(avg_effectiveness, 1),
        detail=detail,
    )


def calculate_overall_safety_score(
    nearby_safeties: list[SafetyPoint],
) -> tuple[int, list[SafetyCategoryScore]]:
    """전체 안전 점수 계산

    안전 점수 = Σ(카테고리 안전점수 × 가중치)
    """
    safety_category_scores = [
        calculate_safety_category_score(nearby_safeties, cat)
        for cat in SafetyCategory
    ]

    total_safety = sum(scs.weighted_score for scs in safety_category_scores)
    safety_score = max(0, min(100, round(total_safety)))

    return safety_score, safety_category_scores


def calculate_safety_score(
    nearby_risks: list[RiskPoint],
) -> tuple[int, list[CategoryScore]]:
    """최종 위험 점수 계산

    위험 점수 = Σ(카테고리 위험점수 × 가중치)
    """
    category_scores = [
        calculate_category_score(nearby_risks, cat)
        for cat in RiskCategory
    ]

    total_risk = sum(cs.weighted_score for cs in category_scores)
    risk_score = max(0, min(100, round(total_risk)))

    return risk_score, category_scores


def determine_grade(overall_score: int) -> tuple[SafetyGrade, str]:
    """통합 점수 → 등급 변환

    통합 점수 = 100 - 위험점수 + (안전점수 × 0.3)
    """
    if overall_score >= 80:
        return SafetyGrade.SAFE, "아이가 안전하게 생활할 수 있는 환경입니다"
    elif overall_score >= 50:
        return SafetyGrade.NORMAL, "일부 주의가 필요한 요소가 있습니다"
    else:
        return SafetyGrade.CAUTION, "아이 안전에 주의가 필요한 지역입니다"


# ─── 안전요인 카테고리별 공공데이터 출처 ───
SAFETY_CATEGORY_DATA_SOURCES: dict[SafetyCategory, list[SourceLink]] = {
    SafetyCategory.CCTV: [
        SourceLink(
            label="전국CCTV표준데이터",
            url="https://www.data.go.kr/data/15013094/standard.do",
            type="data",
        ),
    ],
    SafetyCategory.POLICE: [
        SourceLink(
            label="경찰관서 위치 현황",
            url="https://www.data.go.kr/data/15077036/fileData.do",
            type="data",
        ),
    ],
    SafetyCategory.SAFE_HOUSE: [
        SourceLink(
            label="아동안전지킴이집",
            url="https://www.data.go.kr/data/3052084/openapi.do",
            type="data",
        ),
    ],
    SafetyCategory.STREET_LIGHT: [
        SourceLink(
            label="전국보안등정보표준데이터",
            url="https://www.data.go.kr/data/15017320/standard.do",
            type="data",
        ),
    ],
    SafetyCategory.SCHOOL_ZONE: [
        SourceLink(
            label="전국어린이보호구역표준데이터",
            url="https://www.data.go.kr/data/15012891/standard.do",
            type="data",
        ),
    ],
}

# ─── 위험요인 카테고리별 공공데이터 출처 ───
CATEGORY_DATA_SOURCES: dict[RiskCategory, list[SourceLink]] = {
    RiskCategory.CRIME: [
        SourceLink(
            label="생활안전지도",
            url="https://www.safemap.go.kr/main/smap.do",
            type="data",
        ),
        SourceLink(
            label="성범죄자 알림e",
            url="https://www.sexoffender.go.kr",
            type="data",
        ),
    ],
    RiskCategory.TRAFFIC: [
        SourceLink(
            label="도로교통공단 TAAS",
            url="https://taas.koroad.or.kr/gis/mcm/mcl/initMap.do?menuId=GIS_GMP_STS_RSN",
            type="data",
        ),
        SourceLink(
            label="어린이보호구역 정보",
            url="https://www.schoolzone.go.kr",
            type="data",
        ),
    ],
    RiskCategory.DISASTER: [
        SourceLink(
            label="재난안전포털",
            url="https://www.safekorea.go.kr",
            type="data",
        ),
        SourceLink(
            label="국토정보플랫폼 침수흔적도",
            url="https://www.data.go.kr/data/15048634/fileData.do",
            type="data",
        ),
    ],
}

# 위험 라벨별 뉴스 검색 키워드 매핑
NEWS_SEARCH_KEYWORDS: dict[str, str] = {
    "성범죄 hotspot": "성범죄 발생",
    "어린이 대상 범죄": "어린이 대상 범죄",
    "스쿨존 사고": "스쿨존 교통사고",
    "어린이 교통사고": "어린이 교통사고",
    "침수 이력": "침수 피해",
    "지반침하": "싱크홀 지반침하",
}


def _build_news_search_url(risk: RiskPoint) -> str:
    """위험 지점 기반 네이버 뉴스 검색 URL 생성"""
    # description에서 지역명 추출 (첫 단어)
    location = risk.description.split(" ")[0] if risk.description else ""
    keyword = NEWS_SEARCH_KEYWORDS.get(risk.label, risk.label)
    query = f"{location} {keyword}"
    return f"https://search.naver.com/search.naver?where=news&query={quote(query)}"


def extract_risk_factors(
    nearby_risks: list[RiskPoint],
    category_scores: list[CategoryScore],
) -> list[RiskFactor]:
    """주요 위험 요인 상위 3개 추출 (설명 가능성 + 출처 링크)"""
    factors: list[RiskFactor] = []

    # 가중 점수 높은 카테고리 순으로 정렬
    sorted_scores = sorted(category_scores, key=lambda x: x.weighted_score, reverse=True)

    rank = 1
    for cs in sorted_scores:
        if cs.hotspot_count == 0:
            continue
        if rank > 3:
            break

        # 해당 카테고리에서 가장 심각한 위험 지점 찾기
        cat_risks = [r for r in nearby_risks if r.category == cs.category]
        worst = max(cat_risks, key=lambda r: r.severity)

        # 출처 링크 조합: 뉴스 검색(상위) + 공공데이터 출처(텍스트)
        sources = [
            SourceLink(
                label="관련 뉴스 검색",
                url=_build_news_search_url(worst),
                type="news",
            ),
            *CATEGORY_DATA_SOURCES.get(cs.category, []),
        ]

        factors.append(RiskFactor(
            rank=rank,
            icon=CATEGORY_ICONS[cs.category],
            title=f"{CATEGORY_LABELS[cs.category]} ({cs.hotspot_count}건)",
            description=worst.description,
            category=cs.category,
            sources=sources,
        ))
        rank += 1

    # 위험 요인이 없으면 안전 메시지
    if not factors:
        factors.append(RiskFactor(
            rank=1,
            icon="check-circle",
            title="안전 지역",
            description="반경 내 주요 위험 요인이 발견되지 않았습니다",
            category=RiskCategory.CRIME,
            sources=[],
        ))

    return factors


def extract_safety_factors(
    nearby_safeties: list[SafetyPoint],
    safety_category_scores: list[SafetyCategoryScore],
) -> list[SafetyFactor]:
    """주요 안전 요인 상위 3개 추출"""
    factors: list[SafetyFactor] = []

    # 가중 점수 높은 카테고리 순으로 정렬
    sorted_scores = sorted(safety_category_scores, key=lambda x: x.weighted_score, reverse=True)

    rank = 1
    for scs in sorted_scores:
        if scs.facility_count == 0:
            continue
        if rank > 3:
            break

        # 해당 카테고리에서 가장 효과적인 안전 시설 찾기
        cat_safeties = [s for s in nearby_safeties if s.category == scs.category]
        best = max(cat_safeties, key=lambda s: s.effectiveness)

        # 출처 링크
        sources = SAFETY_CATEGORY_DATA_SOURCES.get(scs.category, [])

        factors.append(SafetyFactor(
            rank=rank,
            icon=SAFETY_CATEGORY_ICONS[scs.category],
            title=f"{SAFETY_CATEGORY_LABELS[scs.category]} ({scs.facility_count}개)",
            description=best.description,
            category=scs.category,
            sources=sources,
        ))
        rank += 1

    return factors
