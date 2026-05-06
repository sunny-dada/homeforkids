"""배정 초등학교 조회 서비스

schoolgis.emac.kr의 ArcGIS REST API를 활용하여 좌표 기반으로
실제 배정된 초등학교를 조회합니다.

통합배정(공동학구):
  - 하나의 통학구역에 여러 학교가 배정된 경우
  - 학부모가 선택하거나 추첨으로 배정
"""

import logging
import re

import httpx
from pyproj import Transformer

logger = logging.getLogger(__name__)

# 학구도 GIS 서버 (교육시설환경원 운영)
SCHOOLGIS_URL = "https://schoolgis.emac.kr/arcgis/rest/services/SCHZONE/EDU_LAYER_SCHOOLZONE_QUERY/MapServer"

# 좌표계 변환: WGS84 (GPS) → Korea 2000 TM (EPSG:5186)
_transformer = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True)


async def find_assigned_elementary_schools(
    lat: float, lng: float
) -> list[str]:
    """좌표 기반 배정 초등학교 조회

    Returns:
        배정된 초등학교 이름 리스트 (공동학구인 경우 여러 개)
    """
    # WGS84 → EPSG:5186 변환
    x, y = _transformer.transform(lng, lat)

    # ArcGIS Query Layer 0 = 초등학교학구도
    url = f"{SCHOOLGIS_URL}/0/query"
    params = {
        "geometry": f"{x},{y}",
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"학구도 조회 실패: {e}")
        return []

    features = data.get("features", [])
    if not features:
        logger.info(f"배정 학구 없음: lat={lat}, lng={lng}")
        return []

    # 학구명에서 학교 이름 추출
    schools: set[str] = set()
    for feat in features:
        attrs = feat.get("attributes", {})
        zone_name = attrs.get("HAKGUDO_NAME", "")

        if not zone_name:
            continue

        # 학구명 패턴:
        # "서울구로초통학구역" → "서울구로초등학교"
        # "서울구로·신구로초공동통학구역" → ["서울구로초등학교", "서울신구로초등학교"]
        # "강일초공동통학구역" → "강일초등학교" (여러 학교가 같은 구역)

        # 공동학구 분리 (·, ・, -, 등으로 구분)
        parts = re.split(r'[·・\-]', zone_name)

        for part in parts:
            # "통학구역", "공동통학구역" 제거
            school_base = re.sub(r'(공동)?(통학)?구역$', '', part)

            # "초"로 끝나면 → "초등학교" 추가
            if school_base.endswith('초'):
                school_name = school_base + '등학교'
                schools.add(school_name)
            # 이미 "초등학교"가 포함된 경우
            elif '초등학교' in school_base:
                schools.add(school_base)

        logger.info(f"학구 발견: {zone_name} (HAKGUDO_ID={attrs.get('HAKGUDO_ID')})")

    result = sorted(schools)
    if result:
        logger.info(f"배정 초등학교: {', '.join(result)} (총 {len(result)}개)")

    return result
