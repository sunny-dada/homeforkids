"""주변 학원 서비스 - 나이스(NEIS) 교육정보 개방 포털 기반

API: https://open.neis.go.kr/hub/acaInsTiInfo
- 시도교육청코드 + 행정구역명으로 학원 목록 조회
- REALM_SC_NM (분야명) 기준으로 종류별 개수 집계
- 무료 API 키 필요: https://open.neis.go.kr/portal/guide/actKeyPage.do

분야(REALM_SC_NM) 예시:
  입시·검정 및 보습, 국제화, 예능(음악·미술), 체육, 직업기술, 독서실
"""

import logging
import os
import re
from collections import Counter

import httpx

from app.models.schemas import (
    AcademyCategory,
    NearbyAcademiesResponse,
)

logger = logging.getLogger(__name__)

NEIS_API_URL = "https://open.neis.go.kr/hub/acaInsTiInfo"

# 시도교육청코드 매핑
OFFICE_CODES: dict[str, str] = {
    "서울": "B10",
    "부산": "C10",
    "대구": "D10",
    "인천": "E10",
    "광주광역": "F10",
    "대전": "G10",
    "울산": "H10",
    "세종": "I10",
    "경기": "J10",
    "강원": "K10",
    "충북": "M10",
    "충남": "N10",
    "전북": "P10",
    "전남": "Q10",
    "경북": "R10",
    "경남": "S10",
    "제주": "T10",
}

# 분야별 표시 순서 (사용자 관심도 순)
REALM_ORDER = [
    "입시·검정 및 보습",
    "국제화",
    "예능(음악·미술)",
    "체육",
    "직업기술",
    "독서실",
]


def _get_office_code(address: str) -> str | None:
    """주소에서 시도교육청코드 추출"""
    for keyword, code in OFFICE_CODES.items():
        if keyword in address:
            return code
    return None


def _extract_district_full(address: str) -> str:
    """주소에서 행정구역명(구/군) 추출 (suffix 포함)

    예: '서울특별시 송파구 가락동' → '송파구'
        '경기도 고양시 덕양구 ...' → '덕양구'
    """
    m = re.search(r"(\S+구)\s", address)
    if m:
        return m.group(1)
    m = re.search(r"(\S+군)\s", address)
    if m:
        return m.group(1)
    # 시 단위 (구가 없는 시, e.g., 과천시)
    m = re.search(r"\s(\S+시)\s", address)
    if m:
        return m.group(1)
    return ""


async def find_nearby_academies(
    lat: float,
    lng: float,
    radius: int,
    location_name: str = "",
    address: str = "",
) -> NearbyAcademiesResponse:
    """NEIS API로 행정구역 내 학원 분야별 통계 조회"""
    api_key = os.environ.get("NEIS_API_KEY", "")
    district = _extract_district_full(address)
    office_code = _get_office_code(address)

    if not api_key or not office_code or not district:
        logger.warning(
            f"학원 조회 불가: api_key={'있음' if api_key else '없음'}, "
            f"office_code={office_code}, district={district}"
        )
        return NearbyAcademiesResponse(
            location_name=location_name,
            district=district,
            total_count=0,
            categories=[],
        )

    rows = await _fetch_neis_academies(api_key, office_code, district)

    # 개원 상태인 학원만 분야별 집계
    realm_counts: Counter[str] = Counter()
    for row in rows:
        status = row.get("REG_STTUS_NM", "")
        if status != "개원":
            continue
        realm = row.get("REALM_SC_NM", "기타")
        realm_counts[realm] += 1

    # 정렬: 정의된 순서 → 나머지 → 개수 내림차순
    def sort_key(item: tuple[str, int]) -> tuple[int, int]:
        realm, count = item
        try:
            order = REALM_ORDER.index(realm)
        except ValueError:
            order = len(REALM_ORDER)
        return (order, -count)

    sorted_counts = sorted(realm_counts.items(), key=sort_key)

    categories = [
        AcademyCategory(realm=realm, count=count)
        for realm, count in sorted_counts
        if count > 0
    ]

    return NearbyAcademiesResponse(
        location_name=location_name,
        district=district,
        total_count=sum(realm_counts.values()),
        categories=categories,
    )


async def _fetch_neis_academies(
    api_key: str,
    office_code: str,
    district: str,
) -> list[dict]:
    """NEIS API에서 학원 데이터 조회 (최대 2페이지 = 2000건)"""
    all_rows: list[dict] = []
    total_count = 0

    for page in range(1, 3):  # 최대 2페이지
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    NEIS_API_URL,
                    params={
                        "KEY": api_key,
                        "Type": "json",
                        "pIndex": page,
                        "pSize": 1000,
                        "ATPT_OFCDC_SC_CODE": office_code,
                        "ADMST_ZONE_NM": district,
                        "ACA_INSTI_SC_NM": "학원",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.warning(f"NEIS 학원 조회 실패 (page={page}): {e}")
            break

        info = data.get("acaInsTiInfo")
        if not info or len(info) < 2:
            break

        # 첫 페이지에서 전체 건수 파악
        if page == 1:
            head = info[0].get("head", [])
            if head:
                total_count = head[0].get("list_total_count", 0)

        rows = info[1].get("row", [])
        all_rows.extend(rows)

        # 전부 가져왔으면 중단
        if len(all_rows) >= total_count or len(rows) < 1000:
            break

    logger.info(
        f"NEIS 학원 조회: {district} - {len(all_rows)}/{total_count}건"
    )
    return all_rows
