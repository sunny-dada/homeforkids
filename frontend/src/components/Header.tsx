/** 헤더 - HDS Header 패턴 */
export function Header() {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-solid border-border px-5 py-3">
      <div className="w-full max-w-[540px] mx-auto flex items-center gap-2">
        <span className="text-2xl leading-none">👶</span>
        <h1 className="text-base font-bold text-foreground leading-tight">
          우리아이 살 집
        </h1>
      </div>
    </header>
  );
}
