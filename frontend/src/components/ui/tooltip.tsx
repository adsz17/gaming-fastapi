import * as React from "react";
import { cn } from "@/lib/utils";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

export function Tooltip({ content, children }: TooltipProps) {
  return (
    <div className="relative group inline-block">
      {children}
      <div
        role="tooltip"
        className={cn(
          "absolute left-1/2 -translate-x-1/2 top-full mt-2 hidden group-hover:block bg-gray-800 text-xs text-gray-100 px-2 py-1 rounded shadow-lg z-10"
        )}
      >
        {content}
      </div>
    </div>
  );
}

export default Tooltip;
