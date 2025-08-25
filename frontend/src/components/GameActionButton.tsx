import * as React from "react";
import { motion } from "framer-motion";
import PlaneDuotone from "@/components/icons/PlaneDuotone";
import { cn } from "@/lib/utils";

interface GameActionButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
}

export default function GameActionButton({
  loading,
  disabled,
  className,
  ...props
}: GameActionButtonProps) {
  const isDisabled = disabled || loading;
  return (
    <motion.button
      whileHover={!isDisabled ? { scale: 1.05 } : undefined}
      whileTap={!isDisabled ? { scale: 0.95 } : undefined}
      transition={{ type: "spring", stiffness: 400, damping: 20 }}
      className={cn(
        "relative inline-flex items-center justify-center rounded-2xl px-4 py-2 text-white bg-gradient-to-r from-indigo-500 to-violet-500 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed", 
        className
      )}
      aria-label={props["aria-label"] || "Acción"}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <svg
          className="h-5 w-5 animate-spin text-white"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4l3-3-3-3v4a12 12 0 00-12 12h4z"
          />
        </svg>
      ) : (
        <PlaneDuotone className="h-5 w-5" />
      )}
    </motion.button>
  );
}
