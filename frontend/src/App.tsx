/** 우리아이살집 (HomeForKid) - 메인 앱 */
import { useState, useEffect, useRef } from "react";
import { Header } from "@/components/Header";
import { SearchInput } from "@/components/SearchInput";
import { MapView } from "@/components/MapView";
import { SafetyScoreCard } from "@/components/SafetyScoreCard";
import { RiskFactorList } from "@/components/RiskFactorList";
import { SafetyFactorList } from "@/components/SafetyFactorList";
import { NearbySchools } from "@/components/NearbySchools";
import { NearbyAcademies } from "@/components/NearbyAcademies";
import { ContentTabs } from "@/components/ContentTabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  fetchSafetyScore,
  fetchNearbySchools,
  fetchNearbyAcademies,
} from "@/api/safety";
import type {
  SafetyResponse,
  SearchResultItem,
  NearbySchoolsResponse,
  NearbyAcademiesResponse,
} from "@/types/safety";
import { MapPin, Shield } from "lucide-react";

export default function App() {
  const [selected, setSelected] = useState<SearchResultItem | null>(null);
  const [radius, setRadius] = useState(1000);
  const [result, setResult] = useState<SafetyResponse | null>(null);
  const [schools, setSchools] = useState<NearbySchoolsResponse | null>(null);
  const [academies, setAcademies] = useState<NearbyAcademiesResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 반경 변경 시 자동 갱신용 ref
  const selectedRef = useRef(selected);
  const hasAnalyzed = useRef(false);
  selectedRef.current = selected;

  async function handleAnalyze() {
    if (!selected) return;
    setIsLoading(true);
    setError(null);
    try {
      const [safetyData, schoolData, academyData] = await Promise.all([
        fetchSafetyScore(selected.lat, selected.lng, radius, selected.name),
        fetchNearbySchools(
          selected.lat,
          selected.lng,
          radius,
          selected.name,
          selected.address,
        ),
        fetchNearbyAcademies(
          selected.lat,
          selected.lng,
          radius,
          selected.name,
          selected.address,
        ),
      ]);
      setResult(safetyData);
      setSchools(schoolData);
      setAcademies(academyData);
      hasAnalyzed.current = true;
    } catch {
      setError("분석에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setIsLoading(false);
    }
  }

  // 반경 변경 → 이미 분석된 상태면 자동 재분석
  useEffect(() => {
    const target = selectedRef.current;
    if (!hasAnalyzed.current || !target) return;

    setIsLoading(true);
    setError(null);
    Promise.all([
      fetchSafetyScore(target.lat, target.lng, radius, target.name),
      fetchNearbySchools(
        target.lat,
        target.lng,
        radius,
        target.name,
        target.address,
      ),
      fetchNearbyAcademies(
        target.lat,
        target.lng,
        radius,
        target.name,
        target.address,
      ),
    ])
      .then(([safetyData, schoolData, academyData]) => {
        setResult(safetyData);
        setSchools(schoolData);
        setAcademies(academyData);
      })
      .catch(() => {
        setError("분석에 실패했습니다. 잠시 후 다시 시도해주세요.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [radius]);

  return (
    <div className="min-h-screen bg-background-second">
      <Header />

      <main className="w-full max-w-[540px] mx-auto px-5 py-5 flex flex-col gap-4">
        {/* 검색 영역 */}
        <section className="flex flex-col gap-3">
          <SearchInput onSelect={setSelected} />

          {selected && (
            <>
              <div className="flex items-center gap-2 px-1">
                <MapPin className="w-4 h-4 text-primary flex-none" />
                <span className="text-sm text-foreground-second truncate">
                  {selected.name} · {selected.address}
                </span>
              </div>

              {/* 지도 */}
              <MapView
                lat={selected.lat}
                lng={selected.lng}
                name={selected.name}
                address={selected.address}
              />
            </>
          )}

          {/* 반경 선택 */}
          <div className="flex items-center gap-2">
            {[3000, 2000, 1000, 500].map((r) => (
              <button
                key={r}
                onClick={() => setRadius(r)}
                className={`flex-1 h-9 rounded-md text-sm font-semibold transition-colors border border-solid ${
                  radius === r
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-white text-foreground-second border-border hover:border-primary-300"
                }`}
              >
                {r >= 1000 ? `${r / 1000}km` : `${r}m`}
              </button>
            ))}
          </div>

          <Button
            variant="primary"
            onClick={handleAnalyze}
            disabled={!selected || isLoading}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>분석 중...</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                <span className="font-semibold">안전 점수 분석</span>
              </div>
            )}
          </Button>
        </section>

        {/* 에러 */}
        {error && (
          <Card>
            <CardContent className="py-4">
              <p className="text-sm text-semantic-red text-center">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* 결과 */}
        {result && !error && (
          <section className="flex flex-col gap-4">
            <SafetyScoreCard data={result} />

            {/* 콘텐츠 탭 네비게이션 */}
            <ContentTabs
              riskFactorCount={
                result.risk_factors.filter((f) => f.icon !== "check-circle").length
              }
              safetyFactorCount={result.safety_factors?.length ?? 0}
              kindergartenCount={
                schools?.groups.find((g) => g.school_type === "kindergarten")?.count ?? 0
              }
              schoolCount={
                schools?.groups
                  .filter((g) => g.school_type !== "kindergarten")
                  .reduce((sum, g) => sum + g.count, 0) ?? 0
              }
              academyCount={academies?.total_count ?? 0}
            />

            {/* 주요 위험 요인 */}
            <div id="risk-factors">
              <RiskFactorList factors={result.risk_factors} />
            </div>

            {/* 안전 요인 */}
            <div id="safety-factors">
              <SafetyFactorList factors={result.safety_factors || []} />
            </div>

            {/* 주변 유치원 */}
            <div id="kindergartens">
              {schools && (
                <NearbySchools
                  data={schools}
                  address={selected?.address}
                  filterTypes={["kindergarten"]}
                  title="주변 유치원"
                />
              )}
            </div>

            {/* 주변 학교 */}
            <div id="schools">
              {schools && (
                <NearbySchools
                  data={schools}
                  address={selected?.address}
                  filterTypes={["elementary", "middle", "high"]}
                  title="주변 학교"
                />
              )}
            </div>

            {/* 주변 학원 */}
            <div id="academies">
              {academies && <NearbyAcademies data={academies} />}
            </div>
          </section>
        )}

        {/* 초기 상태 가이드 */}
        {!result && !error && (
          <Card>
            <CardContent className="py-8 flex flex-col items-center gap-3">
              <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-base font-bold text-foreground">
                아파트를 검색해보세요
              </h3>
              <p className="text-sm text-foreground-muted text-center leading-relaxed">
                아이 키우기 안전한 동네인지
                <br />
                데이터 기반으로 분석해드립니다
              </p>
            </CardContent>
          </Card>
        )}
      </main>

      <footer className="border-0 border-t border-solid border-border py-6 mt-4">
        <div className="w-full max-w-[540px] mx-auto px-5 flex flex-col items-center gap-1">
          <span className="text-xs font-semibold text-foreground-muted">
            HomeForKid
          </span>
          <span className="text-[11px] text-foreground-muted">
            made by dadamom
          </span>
        </div>
      </footer>
    </div>
  );
}
