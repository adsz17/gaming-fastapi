import * as React from "react";
import { cn } from "@/lib/utils";

interface TabsProps {
  tabs: { id: string; label: string }[];
  value: string;
  onValueChange: (v: string) => void;
  className?: string;
}

export function Tabs({ tabs, value, onValueChange, className }: TabsProps) {
  return (
    <div className={cn("flex space-x-2 border-b border-neutral-800", className)}>
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onValueChange(t.id)}
          className={cn(
            "px-3 py-2 text-sm font-medium", 
            value === t.id ? "border-b-2 border-neutral-100" : "text-neutral-400"
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
