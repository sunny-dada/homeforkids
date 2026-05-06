"""주변 학교 서비스

검색 전략 (우선순위):
  1. OpenStreetMap Overpass API (API 키 불필요, 기본값)
     - 좌표 기반 반경 검색으로 누락 없이 모든 학교 검색
     - amenity=school (초/중/고), amenity=kindergarten (유치원)

  2. Kakao Local API (KAKAO_REST_API_KEY 설정 시)
     - SC4(학교), PS3(유치원) 카테고리 기반 반경 검색

  3. 호갱노노 suggestions API (최후 fallback)
     - 텍스트 매칭 기반이므로 일부 학교 누락 가능

배정 초등학교:
  가장 가까운 초등학교를 '배정 추정'으로 표시
  정확한 확인은 학구도 알리미(https://schoolzone.emac.kr/) 참고
"""

import asyncio
import logging
import os
import re

import httpx

from app.core.scoring import haversine_distance
from app.models.schemas import (
    NearbySchool,
    NearbySchoolsResponse,
    SchoolGroup,
    SchoolType,
)
from app.services.assigned_school_service import find_assigned_elementary_schools

logger = logging.getLogger(__name__)

# ─── 공통 상수 ───
TYPE_LABELS: dict[SchoolType, str] = {
    SchoolType.KINDERGARTEN: "유치원",
    SchoolType.ELEMENTARY: "초등학교",
    SchoolType.MIDDLE: "중학교",
    SchoolType.HIGH: "고등학교",
}

WALKING_SPEED_M_PER_MIN = 67  # 약 4km/h (직선거리 fallback용)

# 카카오 모빌리티 API
KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


# ============================================================
# 메인 함수
# ============================================================

async def find_nearby_schools(
    lat: float,
    lng: float,
    radius: int,
    location_name: str = "",
    address: str = "",
) -> NearbySchoolsResponse:
    """반경 내 학교 검색 (유치원, 초등, 중, 고)"""

    # 1순위: Overpass API (무료, 키 불필요, 좌표 기반 완전 검색)
    groups = await _find_schools_overpass(lat, lng, radius)

    # Overpass 실패 시 fallback
    if not groups:
        kakao_key = os.environ.get("KAKAO_REST_API_KEY", "")
        if kakao_key:
            groups = await _find_schools_kakao(lat, lng, radius, kakao_key)
        else:
            logger.info("Overpass 실패, KAKAO_REST_API_KEY 미설정 → 호갱노노 fallback")
            groups = await _find_schools_hogangnono(lat, lng, radius, address)

    # 실제 도보 경로 기반 거리 및 시간 업데이트 (카카오 모빌리티 API)
    kakao_key = os.environ.get("KAKAO_REST_API_KEY", "")
    if kakao_key and groups:
        await _update_walking_routes(lat, lng, groups, kakao_key)

    # 실제 배정 초등학교 조회 및 표시
    assigned_schools = await find_assigned_elementary_schools(lat, lng)
    if assigned_schools:
        _mark_assigned_schools(groups, assigned_schools)

    total = sum(g.count for g in groups)

    return NearbySchoolsResponse(
        location_name=location_name,
        radius=radius,
        total_count=total,
        groups=groups,
    )


def _build_groups(
    type_map: dict[SchoolType, list[NearbySchool]],
) -> list[SchoolGroup]:
    """유형별 학교 리스트를 정렬된 SchoolGroup 리스트로 변환"""
    groups: list[SchoolGroup] = []
    for school_type in SchoolType:
        schools = type_map.get(school_type, [])
        if not schools:
            continue
        schools.sort(key=lambda s: s.distance_m)

        groups.append(SchoolGroup(
            school_type=school_type,
            label=TYPE_LABELS[school_type],
            count=len(schools),
            schools=schools,
        ))
    return groups


def _mark_assigned_schools(
    groups: list[SchoolGroup], assigned_school_names: list[str]
) -> None:
    """배정 초등학교 표시 (is_assigned = True)"""
    if not assigned_school_names:
        return

    for group in groups:
        if group.school_type != SchoolType.ELEMENTARY:
            continue

        for school in group.schools:
            # 학교 이름 매칭 (공백 제거하여 비교)
            school_name_clean = school.name.replace(" ", "")
            for assigned_name in assigned_school_names:
                assigned_clean = assigned_name.replace(" ", "")
                if school_name_clean == assigned_clean or assigned_clean in school_name_clean:
                    school.is_assigned = True
                    logger.info(f"배정 학교 표시: {school.name}")
                    break


async def _update_walking_routes(
    origin_lat: float,
    origin_lng: float,
    groups: list[SchoolGroup],
    api_key: str,
) -> None:
    """카카오 모빌리티 API로 실제 도보 경로 기반 거리 및 시간 업데이트"""
    # 모든 학교 리스트 수집
    all_schools: list[NearbySchool] = []
    for group in groups:
        all_schools.extend(group.schools)

    if not all_schools:
        return

    # 병렬로 경로 조회 (최대 50개씩 제한)
    tasks = [
        _get_walking_route_kakao(origin_lat, origin_lng, school.lat, school.lng, api_key)
        for school in all_schools[:50]  # API 호출 제한
    ]

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = 0
        for school, result in zip(all_schools, results):
            if isinstance(result, Exception):
                logger.info(f"도보 경로 조회 실패 ({school.name}): {result}")
                continue

            if result:
                distance_m, duration_sec = result
                school.distance_m = distance_m
                school.walking_min = max(1, round(duration_sec / 60))
                success_count += 1
                logger.info(
                    f"도보 경로 업데이트: {school.name} - "
                    f"{distance_m}m, {school.walking_min}분"
                )

        logger.info(f"카카오 모빌리티 API: {success_count}/{len(all_schools)}건 성공")
    except Exception as e:
        logger.warning(f"도보 경로 일괄 업데이트 실패: {e}")


async def _get_walking_route_kakao(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    api_key: str,
) -> tuple[int, int] | None:
    """카카오 모빌리티 API로 도보 경로 조회

    Returns:
        (거리(m), 소요시간(초)) 또는 None
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                KAKAO_DIRECTIONS_URL,
                params={
                    "origin": f"{origin_lng},{origin_lat}",
                    "destination": f"{dest_lng},{dest_lat}",
                    "priority": "RECOMMEND",
                    "waypoints": "",
                    "road_details": "false",
                },
                headers={"Authorization": f"KakaoAK {api_key}"},
            )

            # 429 (Too Many Requests) 또는 다른 에러 시 None 반환
            if resp.status_code != 200:
                return None

            data = resp.json()

            # 경로 정보 추출
            routes = data.get("routes", [])
            if not routes:
                return None

            route = routes[0]
            summary = route.get("summary", {})

            distance = summary.get("distance", 0)  # 미터
            duration = summary.get("duration", 0)  # 초

            if distance > 0 and duration > 0:
                return (distance, duration)

            return None

    except Exception as e:
        logger.info(f"카카오 모빌리티 API 호출 실패: {e}")
        return None


# ============================================================
# OpenStreetMap Overpass API (무료, API 키 불필요)
# ============================================================

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# 학교 이름에서 유형 판별 (한국 학교명 규칙: 이름 + 유형 suffix)
# 유치원을 먼저 체크 ("초등학교병설유치원" → 유치원으로 분류)
NAME_TYPE_PATTERNS: list[tuple[str, SchoolType]] = [
    ("유치원", SchoolType.KINDERGARTEN),
    ("초등학교", SchoolType.ELEMENTARY),
    ("중학교", SchoolType.MIDDLE),
    ("고등학교", SchoolType.HIGH),
]


async def _find_schools_overpass(
    lat: float, lng: float, radius: int,
) -> list[SchoolGroup]:
    """OpenStreetMap Overpass API로 반경 내 모든 학교 검색"""
    query = f"""[out:json][timeout:10];
(
  nwr["amenity"="school"](around:{radius},{lat},{lng});
  nwr["amenity"="kindergarten"](around:{radius},{lat},{lng});
);
out center;"""

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(
                OVERPASS_URL,
                data={"data": query},
                headers={"User-Agent": "HomeForKid/0.1"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"Overpass API 검색 실패: {e}")
        return []

    elements = data.get("elements", [])
    type_map: dict[SchoolType, list[NearbySchool]] = {t: [] for t in SchoolType}
    seen_names: set[str] = set()

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:ko", "")
        if not name:
            continue

        # 동일 학교의 개별 건물 중복 방지
        if name in seen_names:
            continue
        seen_names.add(name)

        # 좌표 (node → 직접, way/relation → center)
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lng = el.get("lon") or el.get("center", {}).get("lon")
        if not el_lat or not el_lng:
            continue

        # 유형 판별
        school_type = _classify_by_name(name, tags.get("amenity", ""))
        if school_type is None:
            continue

        dist = round(haversine_distance(lat, lng, el_lat, el_lng))
        walking_min = max(1, round(dist / WALKING_SPEED_M_PER_MIN))

        el_id = str(el.get("id", ""))

        type_map[school_type].append(NearbySchool(
            id=el_id,
            name=name,
            school_type=school_type,
            school_type_label=TYPE_LABELS[school_type],
            description=tags.get("operator:type"),  # 공립/사립 등
            address=tags.get("addr:full", "") or _build_address(tags),
            lat=el_lat,
            lng=el_lng,
            distance_m=dist,
            walking_min=walking_min,
            detail_url=f"https://map.kakao.com/link/search/{name}",
        ))

    school_count = sum(len(v) for v in type_map.values())
    if school_count == 0:
        return []

    logger.info(
        f"Overpass 학교 검색 완료: "
        f"유치원={len(type_map[SchoolType.KINDERGARTEN])}, "
        f"초등={len(type_map[SchoolType.ELEMENTARY])}, "
        f"중={len(type_map[SchoolType.MIDDLE])}, "
        f"고={len(type_map[SchoolType.HIGH])}"
    )

    return _build_groups(type_map)


def _classify_by_name(name: str, amenity: str) -> SchoolType | None:
    """학교 이름과 amenity 태그로 유형 판별"""
    for suffix, school_type in NAME_TYPE_PATTERNS:
        if suffix in name:
            return school_type

    # 이름에 유형이 없는 경우 amenity 태그로 판별
    if amenity == "kindergarten":
        return SchoolType.KINDERGARTEN

    return None


def _build_address(tags: dict) -> str:
    """OSM 태그에서 주소 조합"""
    parts = []
    for key in ["addr:city", "addr:district", "addr:subdistrict", "addr:street", "addr:housenumber"]:
        val = tags.get(key, "")
        if val:
            parts.append(val)
    return " ".join(parts)


# ============================================================
# Kakao Local API 기반 검색 (KAKAO_REST_API_KEY 필요)
# ============================================================

KAKAO_CATEGORY_URL = "https://dapi.kakao.com/v2/local/search/category"

KAKAO_SC4_PATTERNS: list[tuple[str, SchoolType]] = [
    ("초등학교", SchoolType.ELEMENTARY),
    ("중학교", SchoolType.MIDDLE),
    ("고등학교", SchoolType.HIGH),
]


async def _find_schools_kakao(
    lat: float, lng: float, radius: int, api_key: str,
) -> list[SchoolGroup]:
    """Kakao Local API로 반경 내 모든 학교 검색"""
    sc4_docs, ps3_docs = await asyncio.gather(
        _kakao_category_all_pages(lat, lng, radius, "SC4", api_key),
        _kakao_category_all_pages(lat, lng, radius, "PS3", api_key),
    )

    type_map: dict[SchoolType, list[NearbySchool]] = {t: [] for t in SchoolType}

    for doc in sc4_docs:
        cat_name = doc.get("category_name", "")
        for pattern, school_type in KAKAO_SC4_PATTERNS:
            if pattern in cat_name:
                type_map[school_type].append(
                    _kakao_doc_to_school(doc, school_type, lat, lng)
                )
                break

    for doc in ps3_docs:
        cat_name = doc.get("category_name", "")
        place_name = doc.get("place_name", "")
        if "유치원" in cat_name or "유치원" in place_name:
            if "어린이집" not in cat_name and "어린이집" not in place_name:
                type_map[SchoolType.KINDERGARTEN].append(
                    _kakao_doc_to_school(doc, SchoolType.KINDERGARTEN, lat, lng)
                )

    logger.info(
        f"Kakao 학교 검색 완료: "
        f"유치원={len(type_map[SchoolType.KINDERGARTEN])}, "
        f"초등={len(type_map[SchoolType.ELEMENTARY])}, "
        f"중={len(type_map[SchoolType.MIDDLE])}, "
        f"고={len(type_map[SchoolType.HIGH])}"
    )

    return _build_groups(type_map)


async def _kakao_category_all_pages(
    lat: float, lng: float, radius: int, category: str, api_key: str,
) -> list[dict]:
    """Kakao 카테고리 검색 전체 페이지 수집 (최대 45건)"""
    all_docs: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            for page in range(1, 4):
                resp = await client.get(
                    KAKAO_CATEGORY_URL,
                    params={
                        "category_group_code": category,
                        "x": str(lng),
                        "y": str(lat),
                        "radius": str(radius),
                        "sort": "distance",
                        "page": str(page),
                        "size": "15",
                    },
                    headers={"Authorization": f"KakaoAK {api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                all_docs.extend(data.get("documents", []))
                if data.get("meta", {}).get("is_end", True):
                    break
    except Exception as e:
        logger.warning(f"Kakao 카테고리 검색 실패 ({category}): {e}")
    return all_docs


def _kakao_doc_to_school(
    doc: dict, school_type: SchoolType, lat: float, lng: float,
) -> NearbySchool:
    """Kakao API 문서를 NearbySchool로 변환"""
    poi_lat = float(doc.get("y", 0))
    poi_lng = float(doc.get("x", 0))
    dist = int(doc.get("distance", 0)) or round(
        haversine_distance(lat, lng, poi_lat, poi_lng)
    )
    walking_min = max(1, round(dist / WALKING_SPEED_M_PER_MIN))
    place_id = doc.get("id", "")

    return NearbySchool(
        id=place_id,
        name=doc.get("place_name", ""),
        school_type=school_type,
        school_type_label=TYPE_LABELS[school_type],
        description=None,
        address=doc.get("road_address_name") or doc.get("address_name", ""),
        lat=poi_lat,
        lng=poi_lng,
        distance_m=dist,
        walking_min=walking_min,
        detail_url=f"https://place.map.kakao.com/{place_id}",
    )


# ============================================================
# 호갱노노 suggestions API 기반 검색 (최후 fallback)
# ============================================================

HOGANGNONO_SUGGEST_URL = "https://hogangnono.com/api/v2/searches/suggestions/new"

CATEGORY_TO_TYPE: dict[int, SchoolType] = {
    3: SchoolType.KINDERGARTEN,
    4: SchoolType.ELEMENTARY,
    5: SchoolType.MIDDLE,
    6: SchoolType.HIGH,
    24: SchoolType.ELEMENTARY,
    25: SchoolType.MIDDLE,
    26: SchoolType.HIGH,
}

SEARCH_SUFFIXES: dict[SchoolType, str] = {
    SchoolType.KINDERGARTEN: "유치원",
    SchoolType.ELEMENTARY: "초등학교",
    SchoolType.MIDDLE: "중학교",
    SchoolType.HIGH: "고등학교",
}


def _extract_district(address: str) -> str:
    m = re.search(r"(\S+?)구[\s]", address)
    if m:
        return m.group(1)
    m = re.search(r"(\S+?)군[\s]", address)
    if m:
        return m.group(1)
    m = re.search(r"\s(\S+?)시[\s]", address)
    if m:
        return m.group(1)
    return ""


def _extract_dong(address: str) -> str:
    m = re.search(r"(\S+?)[동읍면][\s]", address)
    if m:
        return m.group(1)
    return ""


async def _find_schools_hogangnono(
    lat: float, lng: float, radius: int, address: str,
) -> list[SchoolGroup]:
    """호갱노노 suggestions API 기반 학교 검색 (최후 fallback)"""
    district = _extract_district(address)
    dong = _extract_dong(address)

    tasks = [
        _search_type_hogangnono(lat, lng, radius, school_type, district, dong)
        for school_type in SchoolType
    ]
    results = await asyncio.gather(*tasks)

    type_map: dict[SchoolType, list[NearbySchool]] = {}
    for school_type, schools in zip(SchoolType, results):
        if schools:
            type_map[school_type] = schools

    return _build_groups(type_map)


async def _search_type_hogangnono(
    lat: float, lng: float, radius: int,
    school_type: SchoolType, district: str, dong: str,
) -> list[NearbySchool]:
    suffix = SEARCH_SUFFIXES[school_type]
    target_categories = [
        cat for cat, st in CATEGORY_TO_TYPE.items() if st == school_type
    ]

    queries: list[str] = [suffix]
    if district:
        queries.append(f"{district} {suffix}")
    if dong and dong != district:
        queries.append(f"{dong} {suffix}")

    fetch_tasks = [_fetch_suggestions(lat, lng, q) for q in queries]
    all_results = await asyncio.gather(*fetch_tasks)

    schools: list[NearbySchool] = []
    seen_ids: set[str] = set()

    for poi_list in all_results:
        for poi in poi_list:
            cat = poi.get("category")
            if cat not in target_categories:
                continue

            poi_id = str(poi.get("id", ""))
            if not poi_id or poi_id in seen_ids:
                continue
            seen_ids.add(poi_id)

            poi_lat = poi.get("lat") or poi.get("location", {}).get("lat", 0)
            poi_lng = poi.get("lng") or poi.get("location", {}).get("lon", 0)
            if not poi_lat or not poi_lng:
                continue

            dist = haversine_distance(lat, lng, poi_lat, poi_lng)
            if dist > radius:
                continue

            distance_m = round(dist)
            walking_min = max(1, round(dist / WALKING_SPEED_M_PER_MIN))

            schools.append(NearbySchool(
                id=poi_id,
                name=poi.get("name", ""),
                school_type=school_type,
                school_type_label=TYPE_LABELS[school_type],
                description=poi.get("description"),
                address=poi.get("address", ""),
                lat=poi_lat,
                lng=poi_lng,
                distance_m=distance_m,
                walking_min=walking_min,
                detail_url=f"https://hogangnono.com/poi/{poi_id}",
            ))

    schools.sort(key=lambda s: s.distance_m)
    return schools


async def _fetch_suggestions(lat: float, lng: float, query: str) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                HOGANGNONO_SUGGEST_URL,
                params={"query": query, "x": str(lng), "y": str(lat)},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "HomeForKid/0.1",
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"학교 검색 실패 ({query}): {e}")
        return []

    return data.get("data", {}).get("matched", {}).get("poi", {}).get("list", [])
