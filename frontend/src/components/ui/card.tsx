import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("bg-gray-800/50 border border-neon-blue rounded-lg p-4", className)} {...props} />;
}

export default Card;
