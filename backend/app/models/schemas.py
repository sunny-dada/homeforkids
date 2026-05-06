"""데이터 스키마 정의 - 우리아이살집 (HomeForKid)"""

from enum import Enum
from pydantic import BaseModel, Field


# ─── 등급 Enum ───
class SafetyGrade(str, Enum):
    SAFE = "안전"      # 80~100
    NORMAL = "보통"    # 50~79
    CAUTION = "주의"   # 0~49


class RiskCategory(str, Enum):
    CRIME = "crime"
    TRAFFIC = "traffic"
    DISASTER = "disaster"


class SafetyCategory(str, Enum):
    CCTV = "cctv"
    POLICE = "police"
    SAFE_HOUSE = "safe_house"
    STREET_LIGHT = "street_light"
    SCHOOL_ZONE = "school_zone"


# ─── 위험 데이터 모델 ───
class RiskPoint(BaseModel):
    """개별 위험 지점"""
    id: str
    category: RiskCategory
    lat: float
    lng: float
    severity: int = Field(ge=1, le=5, description="위험 등급 1(낮음)~5(높음)")
    label: str
    description: str


class SafetyPoint(BaseModel):
    """개별 안전 요인"""
    id: str
    category: SafetyCategory
    lat: float
    lng: float
    effectiveness: int = Field(ge=1, le=5, description="안전 효과 1(낮음)~5(높음)")
    label: str
    description: str


class SubcategoryDetail(BaseModel):
    """세부 유형별 상세 정보"""
    label: str  # 예: "성범죄 hotspot", "스쿨존 사고"
    count: int
    avg_severity: float


class CategoryScore(BaseModel):
    """카테고리별 위험 점수"""
    category: RiskCategory
    raw_score: float = Field(ge=0, le=100, description="0~100 위험도")
    weight: float
    weighted_score: float
    hotspot_count: int
    avg_severity: float
    detail: str
    subcategories: list[SubcategoryDetail] = Field(default_factory=list, description="세부 유형별 집계")


# ─── API 요청/응답 ───
class SafetyRequest(BaseModel):
    """안전 점수 조회 요청"""
    lat: float = Field(description="위도")
    lng: float = Field(description="경도")
    radius: int = Field(default=500, ge=100, le=3000, description="반경(m)")
    name: str | None = Field(default=None, description="아파트/장소명")


class SourceLink(BaseModel):
    """출처 링크"""
    label: str
    url: str
    type: str = "data"  # "data" (공공데이터) | "news" (뉴스 기사)


class RiskFactor(BaseModel):
    """주요 위험 요인"""
    rank: int
    icon: str
    title: str
    description: str
    category: RiskCategory
    sources: list[SourceLink] = Field(default_factory=list)


class SafetyCategoryScore(BaseModel):
    """카테고리별 안전 점수"""
    category: SafetyCategory
    raw_score: float = Field(ge=0, le=100, description="0~100 안전도")
    weight: float
    weighted_score: float
    facility_count: int
    avg_effectiveness: float
    detail: str


class SafetyFactor(BaseModel):
    """주요 안전 요인"""
    rank: int
    icon: str
    title: str
    description: str
    category: SafetyCategory
    sources: list[SourceLink] = Field(default_factory=list)


class SafetyResponse(BaseModel):
    """안전 점수 응답"""
    score: int = Field(ge=0, le=100, description="아이 안전 점수 (통합)")
    risk_score: int = Field(ge=0, le=100, description="위험 점수")
    safety_score: int = Field(ge=0, le=100, description="안전 점수")
    grade: SafetyGrade
    grade_label: str
    location_name: str
    radius: int
    category_scores: list[CategoryScore]
    risk_factors: list[RiskFactor]
    nearby_risks: list[RiskPoint]
    safety_category_scores: list[SafetyCategoryScore] = Field(default_factory=list)
    safety_factors: list[SafetyFactor] = Field(default_factory=list)
    nearby_safeties: list[SafetyPoint] = Field(default_factory=list)


# ─── 검색 결과 (호갱노노 API 매핑) ───
class SearchResultItem(BaseModel):
    """통합 검색 결과 항목"""
    id: str
    name: str
    address: str
    road_address: str | None = None
    lat: float
    lng: float
    type: str  # "apt" | "region" | "subway" | "poi"
    type_label: str  # "아파트" | "오피스텔" | "지역" | "지하철" | "학교" 등
    household: int | None = None  # 세대수 (아파트만)


class SearchResponse(BaseModel):
    """검색 응답"""
    query: str
    results: list[SearchResultItem]


# ─── 주변 학교 ───
class SchoolType(str, Enum):
    KINDERGARTEN = "kindergarten"   # 유치원
    ELEMENTARY = "elementary"       # 초등학교
    MIDDLE = "middle"               # 중학교
    HIGH = "high"                   # 고등학교


class NearbySchool(BaseModel):
    """반경 내 학교"""
    id: str
    name: str
    school_type: SchoolType
    school_type_label: str
    description: str | None = None  # 공립/사립 등
    address: str
    lat: float
    lng: float
    distance_m: int                 # 직선 거리 (m)
    walking_min: int                # 도보 시간 (분)
    detail_url: str                 # 상세 링크 (Kakao Map / 호갱노노)
    is_assigned: bool = False       # 배정 추정 초등학교 여부


class NearbySchoolsResponse(BaseModel):
    """주변 학교 응답"""
    location_name: str
    radius: int
    total_count: int
    groups: list["SchoolGroup"]


class SchoolGroup(BaseModel):
    """학교 타입별 그룹"""
    school_type: SchoolType
    label: str
    count: int
    schools: list[NearbySchool]


# ─── 주변 학원 (NEIS 공공데이터) ───
class AcademyCategory(BaseModel):
    """학원 분야별 통계"""
    realm: str       # NEIS REALM_SC_NM (분야명)
    count: int


class NearbyAcademiesResponse(BaseModel):
    """주변 학원 응답"""
    location_name: str
    district: str            # 행정구역명 (e.g., "송파구")
    total_count: int
    categories: list[AcademyCategory]
    source: str = "나이스 교육정보 개방 포털"
