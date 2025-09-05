import * as React from "react";
import { cn } from "@/lib/utils";

export const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "px-4 py-2 rounded bg-neon-blue text-gray-900 hover:bg-neon-pink transition disabled:opacity-50 transform hover:scale-105",
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";

export default Button;
