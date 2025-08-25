import { useState } from "react";
import { cn } from "@/lib/utils";

interface DropdownMenuProps {
  label: string;
  options: { label: string; onSelect: () => void }[];
  className?: string;
}

export function DropdownMenu({ label, options, className }: DropdownMenuProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className={cn("relative inline-block text-left", className)}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="px-2 py-1 border border-neutral-700 rounded-md hover:bg-neutral-800"
      >
        {label}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-40 rounded-md border border-neutral-700 bg-neutral-900 shadow-lg z-20">
          {options.map((opt) => (
            <button
              key={opt.label}
              className="block w-full px-4 py-2 text-left text-sm hover:bg-neutral-800"
              onClick={() => {
                opt.onSelect();
                setOpen(false);
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
