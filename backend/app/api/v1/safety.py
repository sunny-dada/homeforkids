"""API 엔드포인트 - /api/v1"""

from fastapi import APIRouter, Query

from app.models.schemas import (
    SafetyRequest,
    SafetyResponse,
    SearchResponse,
    NearbySchoolsResponse,
    NearbyAcademiesResponse,
)

from app.services.safety_service import evaluate_safety
from app.services.search_service import search_suggestions
from app.services.school_service import find_nearby_schools
from app.services.academy_service import find_nearby_academies

router = APIRouter(prefix="/api/v1", tags=["safety"])


@router.get("/safety/score", response_model=SafetyResponse)
def get_safety_score(
    lat: float = Query(description="위도"),
    lng: float = Query(description="경도"),
    radius: int = Query(default=500, ge=100, le=3000, description="반경(m)"),
    name: str | None = Query(default=None, description="장소명"),
):
    """아이 안전 점수 조회"""
    req = SafetyRequest(lat=lat, lng=lng, radius=radius, name=name)
    return evaluate_safety(req)


@router.get("/search", response_model=SearchResponse)
async def search_api(
    q: str = Query(description="검색어"),
    x: float | None = Query(default=None, description="경도 (위치 기반 정렬)"),
    y: float | None = Query(default=None, description="위도 (위치 기반 정렬)"),
):
    """통합 검색 (호갱노노 suggestions API 프록시)"""
    return await search_suggestions(q, x=x, y=y)


@router.get("/schools/nearby", response_model=NearbySchoolsResponse)
async def get_nearby_schools(
    lat: float = Query(description="위도"),
    lng: float = Query(description="경도"),
    radius: int = Query(default=500, ge=100, le=3000, description="반경(m)"),
    name: str | None = Query(default=None, description="장소명"),
    address: str | None = Query(default=None, description="주소 (구/동 추출용)"),
):
    """반경 내 학교 조회 (유치원, 초등, 중, 고)"""
    return await find_nearby_schools(
        lat, lng, radius,
        location_name=name or "",
        address=address or "",
    )


@router.get("/academies/nearby", response_model=NearbyAcademiesResponse)
async def get_nearby_academies(
    lat: float = Query(description="위도"),
    lng: float = Query(description="경도"),
    radius: int = Query(default=500, ge=100, le=3000, description="반경(m)"),
    name: str | None = Query(default=None, description="장소명"),
    address: str | None = Query(default=None, description="주소 (구/동 추출용)"),
):
    """반경 내 학원 조회 (종류별 그룹)"""
    return await find_nearby_academies(
        lat, lng, radius,
        location_name=name or "",
        address=address or "",
    )
