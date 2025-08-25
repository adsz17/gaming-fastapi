import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DialogProps {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  className?: string;
}

export function Dialog({ open, onClose, children, className }: DialogProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/50">
      <div className={cn("bg-neutral-900 p-4 rounded-md shadow-lg", className)}>
        {children}
        <div className="mt-4 text-right">
          <button
            className="px-4 py-2 text-sm border border-neutral-700 rounded-md"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
