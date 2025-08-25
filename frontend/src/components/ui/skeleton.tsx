import * as React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-gray-700 animate-pulse rounded-md",
        className
      )}
      aria-hidden="true"
    />
  );
}

export default Skeleton;
