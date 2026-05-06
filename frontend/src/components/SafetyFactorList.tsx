/** 주요 안전 요인 목록 - HDS ListItemA 패턴 + 출처 링크 */
import { useState } from "react";
import {
  Camera,
  Shield,
  Home,
  Lightbulb,
  Flag,
  ExternalLink,
  Newspaper,
  ChevronDown,
} from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { SafetyFactor, SafetyCategoryType, SourceLink } from "@/types/safety";

const ICON_MAP: Record<string, React.ElementType> = {
  camera: Camera,
  shield: Shield,
  home: Home,
  lightbulb: Lightbulb,
  flag: Flag,
};

const CATEGORY_COLOR: Record<SafetyCategoryType, string> = {
  cctv: "bg-safety-safe-bg text-safety-safe",
  police: "bg-safety-safe-bg text-safety-safe",
  safe_house: "bg-safety-safe-bg text-safety-safe",
  street_light: "bg-safety-safe-bg text-safety-safe",
  school_zone: "bg-safety-safe-bg text-safety-safe",
};

const ITEMS_PER_PAGE = 5;

interface SafetyFactorListProps {
  factors: SafetyFactor[];
}

export function SafetyFactorList({ factors }: SafetyFactorListProps) {
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  const visibleFactors = factors.slice(0, visibleCount);
  const remainingCount = factors.length - visibleCount;
  const hasMore = remainingCount > 0;

  const handleLoadMore = () => {
    setVisibleCount((prev) => prev + ITEMS_PER_PAGE);
  };

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-bold text-foreground">주요 안전 요인</h2>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-0">
          {visibleFactors.map((f) => (
            <SafetyFactorItem key={f.rank} factor={f} />
          ))}
        </ul>

        {/* 더보기 버튼 */}
        {hasMore && (
          <div className="mt-4 flex justify-center">
            <Button
              variant="outline"
              onClick={handleLoadMore}
              className="flex items-center gap-2"
            >
              {remainingCount}개 더보기
              <ChevronDown className="w-4 h-4" />
            </Button>
          </div>
        )}

        {/* 데이터 출처 */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-3 mt-1 border-0 border-t border-solid border-border">
          <span className="text-[11px] text-foreground-muted">출처:</span>
          {[
            { label: "전국CCTV표준데이터", url: "https://www.data.go.kr/data/15013094/standard.do" },
            { label: "경찰관서 위치 현황", url: "https://www.data.go.kr/data/15077036/fileData.do" },
            { label: "아동안전지킴이집", url: "https://www.data.go.kr/data/3052084/openapi.do" },
            { label: "전국보안등정보표준데이터", url: "https://www.data.go.kr/data/15017320/standard.do" },
            { label: "전국어린이보호구역표준데이터", url: "https://www.data.go.kr/data/15012891/standard.do" },
          ].map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-0.5 text-[11px] text-primary hover:underline no-underline"
            >
              {s.label}
              <ExternalLink className="w-3 h-3" />
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function SafetyFactorItem({ factor }: { factor: SafetyFactor }) {
  const Icon = ICON_MAP[factor.icon] ?? ShieldAlert;
  const colorClasses =
    CATEGORY_COLOR[factor.category] ??
    "bg-background-second text-foreground-muted";

  const newsLinks = factor.sources.filter((s) => s.type === "news");
  const dataSources = factor.sources.filter((s) => s.type === "data");

  return (
    <li
      className={cn(
        "flex flex-col gap-2 px-0 py-3",
        "border-0 border-b border-solid border-border last:border-b-0",
      )}
    >
      {/* 상단: 아이콘 + 제목/설명 */}
      <div className="flex items-start gap-3">
        <div
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center flex-none",
            colorClasses,
          )}
        >
          <Icon className="w-5 h-5" />
        </div>

        <div className="flex flex-col gap-1 overflow-hidden min-w-0">
          <span className="text-sm font-semibold text-foreground truncate">
            {factor.title}
          </span>
          <span className="text-xs text-foreground-second leading-relaxed">
            {factor.description}
          </span>

          {/* 뉴스 검색 링크 (클릭 가능) */}
          {newsLinks.map((link) => (
            <NewsLink key={link.url} source={link} />
          ))}

          {/* 출처 텍스트 */}
          {dataSources.length > 0 && (
            <span className="text-[11px] text-foreground-muted leading-relaxed">
              출처: {dataSources.map((s) => s.label).join(", ")}
            </span>
          )}
        </div>
      </div>
    </li>
  );
}

function NewsLink({ source }: { source: SourceLink }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-xs text-primary font-medium no-underline hover:underline w-fit"
    >
      <Newspaper className="w-3 h-3 flex-none" />
      <span>{source.label}</span>
      <ExternalLink className="w-2.5 h-2.5 flex-none opacity-50" />
    </a>
  );
}
