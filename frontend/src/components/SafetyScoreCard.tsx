/** 안전 점수 카드 - HDS Card + Badge 패턴 */
import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Info, ChevronDown, ChevronRight } from "lucide-react";
import type { SafetyResponse, SafetyGrade } from "@/types/safety";

const GRADE_CONFIG: Record<
  SafetyGrade,
  { variant: "safe" | "normal" | "caution"; ringColor: string; scoreColor: string }
> = {
  안전: {
    variant: "safe",
    ringColor: "text-safety-safe",
    scoreColor: "text-safety-safe",
  },
  보통: {
    variant: "normal",
    ringColor: "text-safety-normal",
    scoreColor: "text-safety-normal",
  },
  주의: {
    variant: "caution",
    ringColor: "text-safety-caution",
    scoreColor: "text-safety-caution",
  },
};

function ScoreRing({
  score,
  grade,
}: {
  score: number;
  grade: SafetyGrade;
}) {
  const config = GRADE_CONFIG[grade];
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-36 h-36 flex items-center justify-center">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="#f3f4f6"
          strokeWidth="10"
        />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn("transition-all duration-700 ease-out", config.ringColor)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn("text-4xl font-bold", config.scoreColor)}>
          {score}
        </span>
        <span className="text-xs text-foreground-muted">/ 100</span>
      </div>
    </div>
  );
}

interface SafetyScoreCardProps {
  data: SafetyResponse;
}

export function SafetyScoreCard({ data }: SafetyScoreCardProps) {
  const config = GRADE_CONFIG[data.grade];
  const [showSources, setShowSources] = useState(false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1.5">
              <h2 className="text-lg font-bold text-foreground">
                아이 안전 점수
              </h2>
              <button
                onClick={() => setShowSources((v) => !v)}
                className={cn(
                  "inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-semibold transition-colors border border-solid",
                  showSources
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-background-second text-foreground-muted border-border hover:border-primary-300 hover:text-primary",
                )}
              >
                <Info className="w-3 h-3" />
                데이터 출처
                <ChevronDown
                  className={cn(
                    "w-3 h-3 transition-transform",
                    showSources && "rotate-180",
                  )}
                />
              </button>
            </div>
            <p className="text-sm text-foreground-second">
              {data.location_name} · 반경 {data.radius}m
            </p>
          </div>
          <Badge variant={config.variant} size="lg">
            {data.grade}
          </Badge>
        </div>
      </CardHeader>

      {/* 데이터 출처 & 계산 로직 패널 */}
      {showSources && <DataSourcePanel radius={data.radius} />}

      <CardContent>
        <div className="flex flex-col gap-4">
          {/* 위험 vs 안전 점수 */}
          <div className="flex items-center justify-center gap-6">
            <div className="flex flex-col items-center gap-2">
              <span className="text-xs font-semibold text-foreground-muted">위험 점수</span>
              <div className="relative w-24 h-24 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#f3f4f6"
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 45}
                    strokeDashoffset={2 * Math.PI * 45 - (data.risk_score / 100) * 2 * Math.PI * 45}
                    className="text-safety-caution transition-all duration-700"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold text-safety-caution">{data.risk_score}</span>
                </div>
              </div>
              <span className="text-[11px] text-foreground-muted">낮을수록 좋음</span>
            </div>

            <div className="flex flex-col items-center gap-2">
              <span className="text-xs font-semibold text-foreground-muted">안전 점수</span>
              <div className="relative w-24 h-24 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#f3f4f6"
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 45}
                    strokeDashoffset={2 * Math.PI * 45 - (data.safety_score / 100) * 2 * Math.PI * 45}
                    className="text-safety-safe transition-all duration-700"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold text-safety-safe">{data.safety_score}</span>
                </div>
              </div>
              <span className="text-[11px] text-foreground-muted">높을수록 좋음</span>
            </div>
          </div>

          <p className="text-sm text-foreground-second text-center">
            {data.grade_label}
          </p>

          {/* 위험 요인 카테고리 */}
          <div className="w-full flex flex-col gap-2">
            <h3 className="text-xs font-bold text-foreground">위험 요인</h3>
            {data.category_scores.map((cs) => (
              <CategoryBar key={cs.category} score={cs} />
            ))}
          </div>

          {/* 안전 요인 카테고리 */}
          {data.safety_category_scores && data.safety_category_scores.length > 0 && (
            <div className="w-full flex flex-col gap-2">
              <h3 className="text-xs font-bold text-foreground">안전 요인</h3>
              {data.safety_category_scores.map((scs) => (
                <SafetyCategoryBar key={scs.category} score={scs} />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/* ── 데이터 출처 & 계산 로직 패널 ─────────────────────── */

function DataSourcePanel({ radius }: { radius: number }) {
  return (
    <div className="px-5 pb-2">
      <div className="rounded-lg bg-background-second p-4 flex flex-col gap-4 text-xs leading-relaxed text-foreground-second">
        {/* 계산 공식 */}
        <div>
          <h3 className="text-sm font-bold text-foreground mb-1.5">
            점수 계산 방식
          </h3>
          <div className="rounded-md bg-white border border-solid border-border p-3 flex flex-col gap-2">
            <div className="font-mono text-[11px] text-foreground">
              <div className="text-semantic-red font-semibold mb-1">위험점수 = 범죄×0.4 + 교통×0.3 + 재난×0.3</div>
              <div className="text-safety-safe font-semibold mb-1">안전점수 = CCTV×0.25 + 치안×0.25 + 안전지킴이집×0.2 + 가로등×0.15 + 보호구역×0.15</div>
              <div className="text-primary font-semibold mt-2 pt-2 border-0 border-t border-solid border-border">종합점수 = 100 − 위험점수 + (안전점수 × 0.3)</div>
            </div>
          </div>
          <ul className="mt-2 flex flex-col gap-1 pl-3">
            <li className="list-disc">
              반경 <strong className="text-foreground">{radius}m</strong> 내
              위험 요소와 안전 요소를 각각 평가
            </li>
            <li className="list-disc">
              위험점수는 밀집도+심각도 기반, 안전점수는 밀집도+효과성 기반으로 산출
            </li>
            <li className="list-disc">
              위험 감점과 안전 가점을 종합하여 최종 점수 계산
            </li>
          </ul>
        </div>

        {/* 등급 기준 */}
        <div>
          <h3 className="text-sm font-bold text-foreground mb-1.5">
            등급 기준
          </h3>
          <div className="grid grid-cols-3 gap-2">
            <div className="flex flex-col items-center gap-1 rounded-md bg-safety-safe-bg py-2">
              <span className="text-sm font-bold text-safety-safe">안전</span>
              <span className="text-[11px]">80점 이상</span>
            </div>
            <div className="flex flex-col items-center gap-1 rounded-md bg-safety-normal-bg py-2">
              <span className="text-sm font-bold text-safety-normal">보통</span>
              <span className="text-[11px]">50 ~ 79점</span>
            </div>
            <div className="flex flex-col items-center gap-1 rounded-md bg-safety-caution-bg py-2">
              <span className="text-sm font-bold text-safety-caution">주의</span>
              <span className="text-[11px]">50점 미만</span>
            </div>
          </div>
        </div>

        {/* 카테고리별 설명 + 출처 */}
        <div>
          <h3 className="text-sm font-bold text-foreground mb-1.5">
            위험요인 데이터 출처
          </h3>
          <div className="flex flex-col gap-2.5">
            <SourceGroup
              emoji="🚨"
              label="범죄 위험 (40%)"
              description="범죄 발생 밀집도와 평균 심각도를 기반으로 산출"
              sources={[
                { name: "생활안전지도", url: "https://www.safemap.go.kr/main/smap.do" },
                { name: "성범죄자 알림e", url: "https://www.sexoffender.go.kr" },
              ]}
            />
            <SourceGroup
              emoji="🚗"
              label="교통 위험 (30%)"
              description="교통사고 다발지역 밀집도 및 사고 심각도 기반 산출"
              sources={[
                { name: "도로교통공단 TAAS", url: "https://taas.koroad.or.kr" },
                { name: "어린이보호구역 정보", url: "https://www.schoolzone.go.kr" },
              ]}
            />
            <SourceGroup
              emoji="🌊"
              label="재난 위험 (30%)"
              description="자연재해 위험지역 밀집도 및 재난 심각도 기반 산출"
              sources={[
                { name: "재난안전포털", url: "https://www.safekorea.go.kr" },
                { name: "국토정보플랫폼 침수흔적도", url: "https://www.data.go.kr/data/15048634/fileData.do" },
              ]}
            />
          </div>
        </div>

        {/* 안전요인 출처 */}
        <div>
          <h3 className="text-sm font-bold text-foreground mb-1.5">
            안전요인 데이터 출처
          </h3>
          <div className="flex flex-col gap-2.5">
            <SourceGroup
              emoji="📹"
              label="CCTV 설치 (25%)"
              description="반경 내 CCTV 밀집도 및 범죄예방 효과 기반 산출"
              sources={[
                { name: "전국CCTV표준데이터", url: "https://www.data.go.kr/data/15013094/standard.do" },
              ]}
            />
            <SourceGroup
              emoji="🛡️"
              label="치안 시설 (25%)"
              description="경찰서/파출소 근접도 및 긴급 대응 시간 기반 산출"
              sources={[
                { name: "경찰관서 위치 현황", url: "https://www.data.go.kr/data/15077036/fileData.do" },
              ]}
            />
            <SourceGroup
              emoji="🏠"
              label="안전지킴이집 (20%)"
              description="아동 긴급 대피처 밀집도 및 등하굣길 안전 기반 산출"
              sources={[
                { name: "아동안전지킴이집", url: "https://www.data.go.kr/data/3052084/openapi.do" },
              ]}
            />
            <SourceGroup
              emoji="💡"
              label="가로등/보안등 (15%)"
              description="야간 조도 안전성 및 보안등 밀집도 기반 산출"
              sources={[
                { name: "전국보안등정보표준데이터", url: "https://www.data.go.kr/data/15017320/standard.do" },
              ]}
            />
            <SourceGroup
              emoji="🚸"
              label="어린이보호구역 (15%)"
              description="스쿨존 근접도 및 안전시설 설치 현황 기반 산출"
              sources={[
                { name: "전국어린이보호구역표준데이터", url: "https://www.data.go.kr/data/15012891/standard.do" },
              ]}
            />
          </div>
        </div>

        {/* MVP 안내 */}
        <p className="text-[11px] text-foreground-muted pt-1 border-0 border-t border-solid border-border">
          현재 MVP 단계로 Mock 데이터를 사용하고 있으며, 향후 실제 공공데이터
          API로 전환될 예정입니다.
        </p>
      </div>
    </div>
  );
}

function SourceGroup({
  emoji,
  label,
  description,
  sources,
}: {
  emoji: string;
  label: string;
  description: string;
  sources: { name: string; url: string }[];
}) {
  return (
    <div className="rounded-md bg-white border border-solid border-border p-3">
      <div className="flex items-center gap-1.5 mb-1">
        <span>{emoji}</span>
        <span className="text-xs font-semibold text-foreground">{label}</span>
      </div>
      <p className="text-[11px] mb-1.5">{description}</p>
      <div className="flex flex-col gap-0.5">
        {sources.map((s) => (
          <a
            key={s.url}
            href={s.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] text-primary hover:underline no-underline"
          >
            {s.name} ↗
          </a>
        ))}
      </div>
    </div>
  );
}

const CATEGORY_LABEL: Record<string, string> = {
  crime: "범죄 위험",
  traffic: "교통 위험",
  disaster: "재난 위험",
};

const SAFETY_CATEGORY_LABEL: Record<string, string> = {
  cctv: "CCTV 설치",
  police: "치안 시설",
  safe_house: "안전지킴이집",
  street_light: "가로등/보안등",
  school_zone: "어린이보호구역",
};

function CategoryBar({
  score,
}: {
  score: SafetyResponse["category_scores"][number];
}) {
  const [showDetail, setShowDetail] = useState(false);
  const safetyLevel = 100 - score.raw_score;
  const barColor =
    safetyLevel >= 80
      ? "bg-safety-safe"
      : safetyLevel >= 50
        ? "bg-safety-normal"
        : "bg-safety-caution";

  const hasSubcategories = score.subcategories && score.subcategories.length > 0;

  return (
    <div className="flex flex-col gap-1">
      <button
        onClick={() => hasSubcategories && setShowDetail((v) => !v)}
        className={cn(
          "flex items-center justify-between text-left w-full",
          hasSubcategories && "cursor-pointer hover:opacity-70 transition-opacity"
        )}
        disabled={!hasSubcategories}
      >
        <div className="flex items-center gap-1">
          {hasSubcategories && (
            <ChevronRight
              className={cn(
                "w-3.5 h-3.5 text-foreground-muted transition-transform flex-none",
                showDetail && "rotate-90"
              )}
            />
          )}
          <span className="text-xs font-semibold text-foreground">
            {CATEGORY_LABEL[score.category] ?? score.category}
          </span>
        </div>
        <span className="text-xs text-foreground-muted">
          {score.hotspot_count}건 · 가중 {score.weighted_score.toFixed(1)}점
        </span>
      </button>
      <div className="w-full h-2 bg-background-second rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", barColor)}
          style={{ width: `${Math.max(safetyLevel, 4)}%` }}
        />
      </div>

      {/* 세부 유형 상세 */}
      {showDetail && hasSubcategories && (
        <div className="mt-1 pl-5 flex flex-col gap-1">
          {score.subcategories.map((sub, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between text-[11px] py-0.5"
            >
              <span className="text-foreground-second">• {sub.label}</span>
              <span className="text-foreground-muted">
                {sub.count}건 · 심각도 {sub.avg_severity}/5
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SafetyCategoryBar({
  score,
}: {
  score: SafetyResponse["safety_category_scores"][number];
}) {
  const barColor = "bg-safety-safe";

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-foreground">
          {SAFETY_CATEGORY_LABEL[score.category] ?? score.category}
        </span>
        <span className="text-xs text-foreground-muted">
          {score.facility_count}개 · 가중 {score.weighted_score.toFixed(1)}점
        </span>
      </div>
      <div className="w-full h-2 bg-background-second rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", barColor)}
          style={{ width: `${Math.max(score.raw_score, 4)}%` }}
        />
      </div>
    </div>
  );
}
