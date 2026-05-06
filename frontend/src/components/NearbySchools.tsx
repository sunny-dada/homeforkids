/** 주변 학교 목록 - HDS ListItemA 패턴 */
import { useState } from "react";
import { GraduationCap, Footprints, ExternalLink, Star, ChevronDown } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type {
  NearbySchoolsResponse,
  SchoolGroup,
  NearbySchool,
  SchoolType,
} from "@/types/safety";

const TYPE_COLOR: Record<SchoolType, string> = {
  kindergarten: "bg-amber-50 text-amber-600",
  elementary: "bg-emerald-50 text-emerald-600",
  middle: "bg-sky-50 text-sky-600",
  high: "bg-violet-50 text-violet-600",
};

const TYPE_EMOJI: Record<SchoolType, string> = {
  kindergarten: "🌱",
  elementary: "🏫",
  middle: "📚",
  high: "🎓",
};

const ITEMS_PER_PAGE = 5;

interface NearbySchoolsProps {
  data: NearbySchoolsResponse;
  address?: string;
  filterTypes?: SchoolType[]; // 표시할 학교 유형 필터
  title?: string; // 커스텀 제목
}

export function NearbySchools({ data, address, filterTypes, title }: NearbySchoolsProps) {
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  // 학교 유형 필터링
  const filteredGroups = filterTypes
    ? data.groups.filter((g) => filterTypes.includes(g.school_type))
    : data.groups;

  const totalCount = filteredGroups.reduce((sum, g) => sum + g.count, 0);

  // 모든 학교를 플랫하게 펼쳐서 페이지네이션
  const allSchools = filteredGroups.flatMap((group) =>
    group.schools.map((school) => ({ ...school, groupType: group.school_type, groupLabel: group.label }))
  );

  const visibleSchools = allSchools.slice(0, visibleCount);
  const remainingCount = allSchools.length - visibleCount;
  const hasMore = remainingCount > 0;

  // visible한 학교들을 다시 그룹으로 재구성
  const visibleGroups: SchoolGroup[] = filteredGroups
    .map((group) => ({
      ...group,
      schools: visibleSchools.filter((s) => s.groupType === group.school_type),
      count: visibleSchools.filter((s) => s.groupType === group.school_type).length,
    }))
    .filter((group) => group.schools.length > 0);

  const handleLoadMore = () => {
    setVisibleCount((prev) => prev + ITEMS_PER_PAGE);
  };
  if (totalCount === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-foreground-muted" />
            <h2 className="text-lg font-bold text-foreground">
              {title || "주변 학교"}
            </h2>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-foreground-muted text-center py-4">
            반경 {data.radius}m 내 {title || "학교"}가 없습니다
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-bold text-foreground">
              {title || "주변 학교"}
            </h2>
          </div>
          <span className="text-xs text-foreground-muted">
            반경 {data.radius}m · {totalCount}개
          </span>
        </div>
      </CardHeader>
      <CardContent>
        {/* 배정 초등학교 안내 */}
        {filteredGroups.some((g) => g.school_type === "elementary") && (
          <div className="mb-4 rounded-lg bg-emerald-50 border border-solid border-emerald-200 px-3 py-2.5">
            <div className="flex items-start gap-2">
              <span className="text-sm leading-none mt-0.5">🏫</span>
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-emerald-700">
                  배정 초등학교
                </span>
                <span className="text-[11px] text-emerald-600 leading-relaxed">
                  학구도 데이터를 기반으로 배정 초등학교를 표시합니다.
                  공동학구인 경우 여러 학교가 표시될 수 있습니다.
                </span>
                <a
                  href={
                    address
                      ? `https://schoolzone.emac.kr/gis/gis.do?searchText=${encodeURIComponent(address)}`
                      : "https://schoolzone.emac.kr/"
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-emerald-700 hover:underline no-underline w-fit"
                >
                  학구도 알리미에서 자세히 보기
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {visibleGroups.map((group) => (
            <SchoolGroupSection key={group.school_type} group={group} />
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
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-3 mt-1 border-0 border-t border-solid border-border">
          <span className="text-[11px] text-foreground-muted">출처:</span>
          <a
            href="https://www.openstreetmap.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-0.5 text-[11px] text-primary hover:underline no-underline"
          >
            OpenStreetMap
            <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href="https://schoolzone.emac.kr/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-0.5 text-[11px] text-primary hover:underline no-underline"
          >
            학구도 알리미
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </CardContent>
    </Card>
  );
}

function SchoolGroupSection({ group }: { group: SchoolGroup }) {
  return (
    <div>
      {/* 그룹 헤더 */}
      <div className="flex items-center gap-1.5 mb-2">
        <span className="text-sm">{TYPE_EMOJI[group.school_type]}</span>
        <span className="text-sm font-semibold text-foreground">
          {group.label}
        </span>
        <span className="text-xs text-foreground-muted">{group.count}개</span>
      </div>

      {/* 학교 목록 */}
      <ul className="flex flex-col gap-0">
        {group.schools.map((school) => (
          <SchoolItem key={school.id} school={school} />
        ))}
      </ul>
    </div>
  );
}

function SchoolItem({ school }: { school: NearbySchool }) {
  const colorClass = TYPE_COLOR[school.school_type];

  return (
    <li
      className={cn(
        "border-0 border-b border-solid border-border last:border-b-0",
      )}
    >
      <a
        href={school.detail_url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-3 py-2.5 no-underline group cursor-pointer"
      >
        {/* 타입 뱃지 */}
        <div
          className={cn(
            "w-9 h-9 rounded-lg flex items-center justify-center flex-none text-xs font-bold",
            colorClass,
          )}
        >
          {school.school_type_label.charAt(0)}
        </div>

        {/* 학교 정보 */}
        <div className="flex flex-col gap-0.5 overflow-hidden min-w-0 flex-1">
          <div className="flex items-center gap-1">
            <span className="text-sm font-semibold text-foreground truncate group-hover:text-primary transition-colors">
              {school.name}
            </span>
            {school.is_assigned && (
              <span className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 font-semibold flex-none">
                <Star className="w-2.5 h-2.5 fill-emerald-700" />
                배정
              </span>
            )}
            {school.description && (
              <span className="text-[10px] px-1 py-0.5 rounded bg-background-second text-foreground-muted flex-none">
                {school.description}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-foreground-second">
            <Footprints className="w-3 h-3 flex-none" />
            <span>도보 {school.walking_min}분</span>
            <span className="text-foreground-muted">·</span>
            <span className="text-foreground-muted">{school.distance_m}m</span>
          </div>
        </div>

        {/* 외부 링크 아이콘 */}
        <ExternalLink className="w-3.5 h-3.5 text-foreground-muted flex-none opacity-0 group-hover:opacity-100 transition-opacity" />
      </a>
    </li>
  );
}
