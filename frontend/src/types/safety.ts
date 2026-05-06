/** API 타입 정의 */

export type SafetyGrade = "안전" | "보통" | "주의";
export type RiskCategoryType = "crime" | "traffic" | "disaster";
export type SafetyCategoryType = "cctv" | "police" | "safe_house" | "street_light" | "school_zone";

export interface SubcategoryDetail {
  label: string;
  count: number;
  avg_severity: number;
}

export interface CategoryScore {
  category: RiskCategoryType;
  raw_score: number;
  weight: number;
  weighted_score: number;
  hotspot_count: number;
  avg_severity: number;
  detail: string;
  subcategories: SubcategoryDetail[];
}

export interface SourceLink {
  label: string;
  url: string;
  type: "data" | "news";
}

export interface RiskFactor {
  rank: number;
  icon: string;
  title: string;
  description: string;
  category: RiskCategoryType;
  sources: SourceLink[];
}

export interface RiskPoint {
  id: string;
  category: RiskCategoryType;
  lat: number;
  lng: number;
  severity: number;
  label: string;
  description: string;
}

export interface SafetyPoint {
  id: string;
  category: SafetyCategoryType;
  lat: number;
  lng: number;
  effectiveness: number;
  label: string;
  description: string;
}

export interface SafetyCategoryScore {
  category: SafetyCategoryType;
  raw_score: number;
  weight: number;
  weighted_score: number;
  facility_count: number;
  avg_effectiveness: number;
  detail: string;
}

export interface SafetyFactor {
  rank: number;
  icon: string;
  title: string;
  description: string;
  category: SafetyCategoryType;
  sources: SourceLink[];
}

export interface SafetyResponse {
  score: number;
  risk_score: number;
  safety_score: number;
  grade: SafetyGrade;
  grade_label: string;
  location_name: string;
  radius: number;
  category_scores: CategoryScore[];
  risk_factors: RiskFactor[];
  nearby_risks: RiskPoint[];
  safety_category_scores: SafetyCategoryScore[];
  safety_factors: SafetyFactor[];
  nearby_safeties: SafetyPoint[];
}

/** 통합 검색 결과 항목 */
export type SearchItemType = "apt" | "region" | "subway" | "poi";

export interface SearchResultItem {
  id: string;
  name: string;
  address: string;
  road_address: string | null;
  lat: number;
  lng: number;
  type: SearchItemType;
  type_label: string;
  household: number | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

/** 주변 학교 */
export type SchoolType = "kindergarten" | "elementary" | "middle" | "high";

export interface NearbySchool {
  id: string;
  name: string;
  school_type: SchoolType;
  school_type_label: string;
  description: string | null;
  address: string;
  lat: number;
  lng: number;
  distance_m: number;
  walking_min: number;
  detail_url: string;
  is_assigned: boolean;
}

export interface SchoolGroup {
  school_type: SchoolType;
  label: string;
  count: number;
  schools: NearbySchool[];
}

export interface NearbySchoolsResponse {
  location_name: string;
  radius: number;
  total_count: number;
  groups: SchoolGroup[];
}

/** 주변 학원 (NEIS 공공데이터) */
export interface AcademyCategory {
  realm: string;
  count: number;
}

export interface NearbyAcademiesResponse {
  location_name: string;
  district: string;
  total_count: number;
  categories: AcademyCategory[];
  source: string;
}
