"""검색 서비스 - 호갱노노 suggestions API 프록시

호갱노노 검색 구조:
- API: GET /api/v2/searches/suggestions/new?query=...&x=...&y=...
- 카테고리: apt(아파트), region(지역), subway(지하철), poi(학교/병원 등)
- 각 카테고리에 order(우선순위), list(결과 목록) 포함
"""

import logging
from urllib.parse import quote

import httpx

from app.models.schemas import SearchResultItem, SearchResponse

logger = logging.getLogger(__name__)

HOGANGNONO_SUGGEST_URL = "https://hogangnono.com/api/v2/searches/suggestions/new"


async def search_suggestions(
    query: str,
    x: float | None = None,
    y: float | None = None,
) -> SearchResponse:
    """호갱노노 자동완성 API를 호출하여 통합 검색 결과 반환"""
    if not query.strip():
        return SearchResponse(query=query, results=[])

    params: dict[str, str] = {"query": query}
    if x is not None:
        params["x"] = str(x)
    if y is not None:
        params["y"] = str(y)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                HOGANGNONO_SUGGEST_URL,
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "HomeForKid/0.1",
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"호갱노노 API 호출 실패: {e}")
        return SearchResponse(query=query, results=[])

    return _parse_suggestions(query, data)


def _parse_suggestions(query: str, raw: dict) -> SearchResponse:
    """호갱노노 응답 → SearchResponse 변환

    카테고리별 order 값으로 정렬하여 호갱노노와 동일한 우선순위로 결과 제공
    """
    matched = raw.get("data", {}).get("matched", {})
    items: list[tuple[int, SearchResultItem]] = []

    # 아파트
    apt_info = matched.get("apt", {})
    apt_order = apt_info.get("order", 99)
    for apt in apt_info.get("list", []):
        loc = apt.get("location", {})
        items.append((apt_order, SearchResultItem(
            id=apt.get("id", ""),
            name=apt.get("name", ""),
            address=apt.get("address", ""),
            road_address=apt.get("road_address"),
            lat=apt.get("lat") or loc.get("lat", 0),
            lng=apt.get("lng") or loc.get("lon", 0),
            type="apt",
            type_label=apt.get("type_name", "아파트"),
            household=apt.get("household"),
        )))

    # 지역
    region_info = matched.get("region", {})
    region_order = region_info.get("order", 99)
    for region in region_info.get("list", []):
        loc = region.get("location", {})
        items.append((region_order, SearchResultItem(
            id=str(region.get("id", "")),
            name=region.get("name", ""),
            address=_build_region_address(region),
            road_address=None,
            lat=region.get("lat") or loc.get("lat", 0),
            lng=region.get("lng") or loc.get("lon", 0),
            type="region",
            type_label="지역",
        )))

    # 지하철
    subway_info = matched.get("subway", {})
    subway_order = subway_info.get("order", 99)
    for sub in subway_info.get("list", []):
        loc = sub.get("location", {})
        items.append((subway_order, SearchResultItem(
            id=str(sub.get("id", "")),
            name=sub.get("name", ""),
            address=sub.get("line", ""),
            road_address=None,
            lat=sub.get("lat") or loc.get("lat", 0),
            lng=sub.get("lng") or loc.get("lon", 0),
            type="subway",
            type_label="지하철",
        )))

    # POI (학교, 병원, 마트 등)
    poi_info = matched.get("poi", {})
    poi_order = poi_info.get("order", 99)
    for poi in poi_info.get("list", []):
        loc = poi.get("location", {})
        items.append((poi_order, SearchResultItem(
            id=str(poi.get("id", "")),
            name=poi.get("name", ""),
            address=poi.get("address", ""),
            road_address=None,
            lat=poi.get("lat") or loc.get("lat", 0),
            lng=poi.get("lng") or loc.get("lon", 0),
            type="poi",
            type_label=poi.get("description", "관심지점"),
        )))

    # order로 그룹 정렬 (호갱노노 우선순위 유지)
    items.sort(key=lambda x: x[0])
    results = [item for _, item in items]

    return SearchResponse(query=query, results=results)


def _build_region_address(region: dict) -> str:
    """지역 정보로 주소 문자열 생성"""
    parts = []
    for level in ["local1_name", "local2_name", "local3_name", "local4_name"]:
        val = region.get(level)
        if val:
            parts.append(val)
    return " ".join(parts) if parts else region.get("name", "")
