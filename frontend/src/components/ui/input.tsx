import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "bg-gray-900 border border-neon-blue rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-neon-pink",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export default Input;
