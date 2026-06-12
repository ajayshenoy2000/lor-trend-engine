"use client";

import { useState } from "react";

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  side?: "top" | "right" | "bottom" | "left";
}

export function Tooltip({ children, content, side = "top" }: TooltipProps) {
  const [isOpen, setIsOpen] = useState(false);

  const positionClasses = {
    top: "bottom-full mb-2 left-1/2 -translate-x-1/2",
    bottom: "top-full mt-2 left-1/2 -translate-x-1/2",
    left: "right-full mr-2 top-1/2 -translate-y-1/2",
    right: "left-full ml-2 top-1/2 -translate-y-1/2",
  };

  const arrowClasses = {
    top: "top-full left-1/2 -translate-x-1/2 border-t-ink/80 border-l-transparent border-r-transparent",
    bottom: "bottom-full left-1/2 -translate-x-1/2 border-b-ink/80 border-l-transparent border-r-transparent",
    left: "left-full top-1/2 -translate-y-1/2 border-l-ink/80 border-t-transparent border-b-transparent",
    right: "right-full top-1/2 -translate-y-1/2 border-r-ink/80 border-t-transparent border-b-transparent",
  };

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onTouchStart={() => setIsOpen(true)}
        onTouchEnd={() => setIsOpen(false)}
      >
        {children}
      </div>

      {isOpen && (
        <div
          className={`fadeIn pointer-events-none absolute z-50 whitespace-nowrap rounded-md bg-ink/80 px-2.5 py-1.5 text-xs font-semibold text-white shadow-lg ${positionClasses[side]}`}
        >
          {content}
          <div className={`absolute border-4 ${arrowClasses[side]}`} />
        </div>
      )}
    </div>
  );
}
