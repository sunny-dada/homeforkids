/** 콘텐츠 탭 네비게이션 - 스크롤 연동 */
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface Tab {
  id: string;
  label: string;
  count?: number;
}

interface ContentTabsProps {
  riskFactorCount?: number;
  safetyFactorCount?: number;
  kindergartenCount?: number;
  schoolCount?: number;
  academyCount?: number;
}

export function ContentTabs({
  riskFactorCount = 0,
  safetyFactorCount = 0,
  kindergartenCount = 0,
  schoolCount = 0,
  academyCount = 0,
}: ContentTabsProps) {
  const TABS: Tab[] = [
    { id: "risk-factors", label: "위험요인", count: riskFactorCount },
    { id: "safety-factors", label: "안전요인", count: safetyFactorCount },
    { id: "kindergartens", label: "유치원", count: kindergartenCount },
    { id: "schools", label: "학교", count: schoolCount },
    { id: "academies", label: "학원", count: academyCount },
  ];
  const [activeTab, setActiveTab] = useState<string>("risk-factors");
  const [isSticky, setIsSticky] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // 탭 위치 확인 (sticky 활성화 여부)
      const tabsElement = document.getElementById("content-tabs");
      if (tabsElement) {
        const rect = tabsElement.getBoundingClientRect();
        setIsSticky(rect.top <= 60); // GNB 높이 기준
      }

      // 현재 보이는 섹션 감지
      const sections = TABS.map((tab) => ({
        id: tab.id,
        element: document.getElementById(tab.id),
      }));

      for (const section of sections) {
        if (section.element) {
          const rect = section.element.getBoundingClientRect();
          // 화면 상단 1/3 지점에 있는 섹션을 활성화
          if (rect.top <= window.innerHeight / 3 && rect.bottom > 0) {
            setActiveTab(section.id);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // 초기 실행

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 120; // GNB(60px) + Tabs(60px)
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.scrollY - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <div
      id="content-tabs"
      className={cn(
        "bg-background border-0 border-b border-solid border-border transition-all",
        isSticky && "sticky top-[60px] z-40 shadow-sm"
      )}
    >
      <div className="flex items-center overflow-x-auto scrollbar-hide">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => scrollToSection(tab.id)}
            className={cn(
              "flex-none py-3 px-4 text-sm font-semibold transition-colors relative whitespace-nowrap",
              "hover:text-primary",
              activeTab === tab.id
                ? "text-primary"
                : "text-foreground-muted"
            )}
          >
            <span className="flex items-center justify-center gap-1">
              {tab.label}
              {tab.count !== undefined && tab.count > 0 && (
                <span
                  className={cn(
                    "text-xs font-semibold",
                    activeTab === tab.id
                      ? "text-primary"
                      : "text-foreground-muted"
                  )}
                >
                  ({tab.count})
                </span>
              )}
            </span>
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
