/** 주변 학원 - NEIS 공공데이터 기반 분야별 통계 */
import { useState } from "react";
import { BookOpen, ExternalLink, ChevronDown } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { NearbyAcademiesResponse, AcademyCategory } from "@/types/safety";

const REALM_CONFIG: Record<string, { emoji: string; color: string }> = {
  "입시·검정 및 보습": { emoji: "📖", color: "bg-blue-50 text-blue-600" },
  "국제화": { emoji: "🌍", color: "bg-rose-50 text-rose-600" },
  "예능(음악·미술)": { emoji: "🎨", color: "bg-amber-50 text-amber-600" },
  체육: { emoji: "⚽", color: "bg-emerald-50 text-emerald-600" },
  직업기술: { emoji: "💻", color: "bg-teal-50 text-teal-600" },
  독서실: { emoji: "📚", color: "bg-gray-100 text-gray-600" },
};

const DEFAULT_CONFIG = { emoji: "🏫", color: "bg-gray-100 text-gray-600" };

const ITEMS_PER_PAGE = 5;

interface NearbyAcademiesProps {
  data: NearbyAcademiesResponse;
}

export function NearbyAcademies({ data }: NearbyAcademiesProps) {
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);
  if (data.total_count === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-foreground-muted" />
            <h2 className="text-lg font-bold text-foreground">주변 학원</h2>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground-muted text-center py-4">
            {data.district
              ? `${data.district} 학원 정보를 조회할 수 없습니다`
              : "NEIS API 키가 설정되지 않았습니다"}
          </p>
          <p className="text-[11px] text-foreground-muted text-center">
            <a
              href="https://open.neis.go.kr/portal/guide/actKeyPage.do"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline no-underline"
            >
              NEIS API 키 발급 (무료) ↗
            </a>
          </p>
        </CardContent>
      </Card>
    );
  }

  const visibleCategories = data.categories.slice(0, visibleCount);
  const remainingCount = data.categories.length - visibleCount;
  const hasMore = remainingCount > 0;

  const handleLoadMore = () => {
    setVisibleCount((prev) => prev + ITEMS_PER_PAGE);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold text-foreground">주변 학원</h2>
          </div>
          <span className="text-xs text-foreground-muted">
            {data.district} · {data.total_count.toLocaleString()}개
          </span>
        </div>
      </CardHeader>
      <CardContent>
        {/* 분야별 통계 그리드 */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          {visibleCategories.map((cat) => (
            <CategoryCard key={cat.realm} category={cat} />
          ))}
        </div>

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
        <div className="flex items-center justify-between pt-3 mt-1 border-0 border-t border-solid border-border">
          <span className="text-[11px] text-foreground-muted">
            출처: {data.source}
          </span>
          <a
            href="https://open.neis.go.kr/portal/data/service/selectServicePage.do?infId=OPEN19220231012134453534385&infSeq=1"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-0.5 text-[11px] text-primary hover:underline no-underline"
          >
            원본 데이터
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </CardContent>
    </Card>
  );
}

function CategoryCard({ category }: { category: AcademyCategory }) {
  const config = REALM_CONFIG[category.realm] ?? DEFAULT_CONFIG;

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-3",
        config.color,
      )}
    >
      <span className="text-xl">{config.emoji}</span>
      <div className="flex flex-col min-w-0">
        <span className="text-xs font-semibold truncate">{category.realm}</span>
        <span className="text-lg font-bold">{category.count.toLocaleString()}개</span>
      </div>
    </div>
  );
}
