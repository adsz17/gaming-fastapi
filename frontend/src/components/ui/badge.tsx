import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn("px-2 py-1 rounded bg-neon-pink text-gray-900 text-xs", className)} {...props} />;
}

export default Badge;
