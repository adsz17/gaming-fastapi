import { createContext, useContext, useState, ReactNode } from "react";
import { addDays, startOfDay, endOfDay } from "date-fns";

export interface DateRange {
  from?: Date;
  to?: Date;
}

interface FilterContext {
  range: DateRange;
  setRange: (r: DateRange) => void;
  userId: string;
  setUserId: (v: string) => void;
}

const defaultRange: DateRange = { from: startOfDay(new Date()), to: endOfDay(new Date()) };

const Ctx = createContext<FilterContext | undefined>(undefined);

export function FiltersProvider({ children }: { children: ReactNode }) {
  const [range, setRange] = useState<DateRange>(defaultRange);
  const [userId, setUserId] = useState("");
  return (
    <Ctx.Provider value={{ range, setRange, userId, setUserId }}>
      {children}
    </Ctx.Provider>
  );
}

export function useFilters() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useFilters must be used within provider");
  return ctx;
}

export function predefinedRange(option: string): DateRange {
  const now = new Date();
  switch (option) {
    case "7d":
      return { from: startOfDay(addDays(now, -7)), to: endOfDay(now) };
    case "30d":
      return { from: startOfDay(addDays(now, -30)), to: endOfDay(now) };
    default:
      return { from: startOfDay(now), to: endOfDay(now) };
  }
}
