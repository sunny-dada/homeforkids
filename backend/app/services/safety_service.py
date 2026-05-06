"""안전 점수 서비스 - 데이터 조회 + 점수 계산 통합"""

from app.core.scoring import (
    filter_nearby_risks,
    filter_nearby_safeties,
    calculate_safety_score,
    calculate_overall_safety_score,
    determine_grade,
    extract_risk_factors,
    extract_safety_factors,
)
from app.data.mock_data import get_all_risks, get_all_safeties
from app.models.schemas import (
    SafetyRequest,
    SafetyResponse,
)


def evaluate_safety(req: SafetyRequest) -> SafetyResponse:
    """특정 좌표의 아이 안전 점수 평가"""
    # 위험 요인 평가
    all_risks = get_all_risks()
    nearby_risks = filter_nearby_risks(all_risks, req.lat, req.lng, req.radius)
    risk_score, category_scores = calculate_safety_score(nearby_risks)
    risk_factors = extract_risk_factors(nearby_risks, category_scores)

    # 안전 요인 평가
    all_safeties = get_all_safeties()
    nearby_safeties = filter_nearby_safeties(all_safeties, req.lat, req.lng, req.radius)
    safety_score, safety_category_scores = calculate_overall_safety_score(nearby_safeties)
    safety_factors = extract_safety_factors(nearby_safeties, safety_category_scores)

    # 통합 점수 계산: 100 - 위험점수 + (안전점수 × 0.3)
    overall_score = max(0, min(100, round(100 - risk_score + (safety_score * 0.3))))
    grade, grade_label = determine_grade(overall_score)

    location_name = req.name or "선택한 위치"

    return SafetyResponse(
        score=overall_score,
        risk_score=risk_score,
        safety_score=safety_score,
        grade=grade,
        grade_label=grade_label,
        location_name=location_name,
        radius=req.radius,
        category_scores=category_scores,
        risk_factors=risk_factors,
        nearby_risks=nearby_risks,
        safety_category_scores=safety_category_scores,
        safety_factors=safety_factors,
        nearby_safeties=nearby_safeties,
    )
