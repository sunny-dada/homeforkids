/** 아파트 검색 - 호갱노노 suggestions API 기반
 *
 * 호갱노노 검색 패턴 적용:
 * - 500ms 쓰로틀 (SearchActionsV2.ts THROTTLE_TIME)
 * - 카테고리별 그룹 표시 (apt, region, subway, poi)
 * - 키보드 네비게이션 (↑↓ Enter Escape)
 * - type_label 뱃지 표시
 */
import { useState, useEffect, useRef, useCallback } from "react";
import {
  Search,
  MapPin,
  Building2,
  MapPinned,
  TrainFront,
  School,
  X,
  Clock,
  Trash2,
} from "lucide-react";
import { searchSuggestions } from "@/api/safety";
import type { SearchResultItem, SearchItemType } from "@/types/safety";
import { cn } from "@/lib/utils";

const THROTTLE_MS = 500;
const RECENT_KEY = "homeforkid_recent";
const MAX_RECENT = 5;

function getRecent(): SearchResultItem[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveRecent(item: SearchResultItem) {
  const list = getRecent().filter((r) => r.id !== item.id);
  list.unshift(item);
  localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, MAX_RECENT)));
}

function clearRecent() {
  localStorage.removeItem(RECENT_KEY);
}

const TYPE_ICON: Record<SearchItemType, React.ElementType> = {
  apt: Building2,
  region: MapPinned,
  subway: TrainFront,
  poi: School,
};

const TYPE_GROUP_LABEL: Record<SearchItemType, string> = {
  apt: "아파트·오피스텔",
  region: "지역",
  subway: "지하철",
  poi: "학교·병원·주변",
};

interface SearchInputProps {
  onSelect: (item: SearchResultItem) => void;
}

export function SearchInput({ onSelect }: SearchInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [recentItems, setRecentItems] = useState<SearchResultItem[]>([]);
  const [showRecent, setShowRecent] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const justSelected = useRef(false);

  // 500ms 쓰로틀 검색 (호갱노노 패턴)
  useEffect(() => {
    // 항목 선택으로 query가 바뀐 경우 검색 스킵
    if (justSelected.current) {
      justSelected.current = false;
      return;
    }
    if (query.trim().length < 1) {
      setResults([]);
      setIsOpen(false);
      return;
    }
    setShowRecent(false);
    setIsLoading(true);
    const timer = setTimeout(async () => {
      try {
        const data = await searchSuggestions(query);
        // 아파트 단지만 필터링
        const aptOnly = data.results.filter((item) => item.type === "apt");
        setResults(aptOnly);
        setIsOpen(aptOnly.length > 0);
        setSelectedIndex(-1);
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, THROTTLE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  // 외부 클릭 시 닫기
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setShowRecent(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 키보드 네비게이션 (호갱노노 AptSearchInput 패턴)
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isOpen || results.length === 0) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) =>
            prev < results.length - 1 ? prev + 1 : 0,
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) =>
            prev > 0 ? prev - 1 : results.length - 1,
          );
          break;
        case "Enter":
          e.preventDefault();
          if (selectedIndex >= 0 && selectedIndex < results.length) {
            selectItem(results[selectedIndex]);
          }
          break;
        case "Escape":
          setIsOpen(false);
          inputRef.current?.blur();
          break;
      }
    },
    [isOpen, results, selectedIndex],
  );

  // 선택된 항목 스크롤
  useEffect(() => {
    if (selectedIndex < 0 || !listRef.current) return;
    const items = listRef.current.querySelectorAll("[data-search-item]");
    items[selectedIndex]?.scrollIntoView({ block: "nearest" });
  }, [selectedIndex]);

  function selectItem(item: SearchResultItem) {
    justSelected.current = true;
    saveRecent(item);
    onSelect(item);
    setQuery(item.name);
    setResults([]);
    setIsOpen(false);
    setShowRecent(false);
    setSelectedIndex(-1);
    inputRef.current?.blur();
  }

  function handleClear() {
    setQuery("");
    setResults([]);
    setIsOpen(false);
    const recent = getRecent().filter((item) => item.type === "apt");
    if (recent.length > 0) {
      setRecentItems(recent);
      setShowRecent(true);
    }
    inputRef.current?.focus();
  }

  function handleClearRecent() {
    clearRecent();
    setRecentItems([]);
    setShowRecent(false);
  }

  // 카테고리별 그룹핑 (호갱노노 order 기반 정렬은 backend에서 처리됨)
  const grouped = groupByType(results);
  let flatIndex = -1;

  return (
    <div ref={wrapperRef} className="relative">
      {/* 검색 입력 */}
      <div className="flex items-center gap-2 bg-white rounded-md border border-solid border-border px-4 h-12 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary-50 transition-all">
        <Search className="w-5 h-5 text-foreground-muted flex-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            if (results.length > 0) {
              setIsOpen(true);
            } else if (!query.trim()) {
              const recent = getRecent().filter((item) => item.type === "apt");
              if (recent.length > 0) {
                setRecentItems(recent);
                setShowRecent(true);
              }
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder="아파트 단지 검색"
          className="flex-1 bg-transparent outline-none text-base text-foreground placeholder:text-foreground-muted"
        />
        {isLoading && (
          <div className="w-4 h-4 border-2 border-primary-300 border-t-primary rounded-full animate-spin flex-none" />
        )}
        {query && !isLoading && (
          <button
            onClick={handleClear}
            className="w-5 h-5 rounded-full bg-foreground-muted/20 flex items-center justify-center flex-none hover:bg-foreground-muted/30 transition-colors"
          >
            <X className="w-3 h-3 text-foreground-second" />
          </button>
        )}
      </div>

      {/* 검색 결과 드롭다운 */}
      {isOpen && (
        <ul
          ref={listRef}
          className="absolute top-14 left-0 right-0 bg-white border border-solid border-border rounded-md shadow-card-hover z-20 max-h-80 overflow-y-auto"
        >
          {grouped.map(([type, items]) => (
            <li key={type}>
              {/* 카테고리 헤더 */}
              <div className="px-4 py-1.5 bg-background-second border-0 border-b border-solid border-border sticky top-0">
                <span className="text-xs font-semibold text-foreground-muted">
                  {TYPE_GROUP_LABEL[type]}
                </span>
              </div>
              {/* 항목 목록 */}
              <ul>
                {items.map((item) => {
                  flatIndex++;
                  const idx = flatIndex;
                  const Icon = TYPE_ICON[item.type] ?? MapPin;
                  return (
                    <li
                      key={`${item.type}-${item.id}`}
                      data-search-item
                      className={cn(
                        "px-4 py-2.5 flex items-start gap-3 cursor-pointer border-0 border-b border-solid border-border last:border-b-0",
                        "transition-colors",
                        idx === selectedIndex
                          ? "bg-primary-50"
                          : "hover:bg-background-second active:bg-primary-50",
                      )}
                      onClick={() => selectItem(item)}
                      onMouseEnter={() => setSelectedIndex(idx)}
                    >
                      <Icon className="w-4 h-4 text-foreground-muted mt-0.5 flex-none" />
                      <div className="flex flex-col gap-0.5 overflow-hidden min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className="text-sm font-semibold text-foreground truncate">
                            {item.name}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-background-second text-foreground-muted font-medium flex-none">
                            {item.type_label}
                          </span>
                          {item.household != null && item.household > 0 && (
                            <span className="text-[10px] text-foreground-muted flex-none">
                              {item.household.toLocaleString()}세대
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-foreground-second truncate">
                          {item.road_address || item.address}
                        </span>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </li>
          ))}
        </ul>
      )}

      {/* 최근 검색 드롭다운 */}
      {showRecent && !isOpen && recentItems.length > 0 && (
        <div className="absolute top-14 left-0 right-0 bg-white border border-solid border-border rounded-md shadow-card-hover z-20">
          <div className="flex items-center justify-between px-4 py-2 border-0 border-b border-solid border-border">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-foreground-muted" />
              <span className="text-xs font-semibold text-foreground-muted">
                최근 검색
              </span>
            </div>
            <button
              onClick={handleClearRecent}
              className="flex items-center gap-1 text-[11px] text-foreground-muted hover:text-safety-caution transition-colors bg-transparent border-0 cursor-pointer px-0"
            >
              <Trash2 className="w-3 h-3" />
              전체 삭제
            </button>
          </div>
          <ul>
            {recentItems.map((item) => {
              const Icon = TYPE_ICON[item.type] ?? MapPin;
              return (
                <li
                  key={`recent-${item.id}`}
                  className="px-4 py-2.5 flex items-center gap-3 cursor-pointer hover:bg-background-second active:bg-primary-50 transition-colors border-0 border-b border-solid border-border last:border-b-0"
                  onClick={() => selectItem(item)}
                >
                  <Icon className="w-4 h-4 text-foreground-muted flex-none" />
                  <div className="flex flex-col gap-0.5 overflow-hidden min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-semibold text-foreground truncate">
                        {item.name}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-background-second text-foreground-muted font-medium flex-none">
                        {item.type_label}
                      </span>
                    </div>
                    <span className="text-xs text-foreground-second truncate">
                      {item.road_address || item.address}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

/** 검색 결과를 type별로 그룹핑 (순서 유지) */
function groupByType(
  items: SearchResultItem[],
): [SearchItemType, SearchResultItem[]][] {
  const map = new Map<SearchItemType, SearchResultItem[]>();
  for (const item of items) {
    const list = map.get(item.type);
    if (list) {
      list.push(item);
    } else {
      map.set(item.type, [item]);
    }
  }
  return Array.from(map.entries());
}
